from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import pandas as pd
import uvicorn
import numpy as np
from contextlib import asynccontextmanager
from pytorch_forecasting import Baseline, TemporalFusionTransformer, TimeSeriesDataSet
import os
import torch
from collections import defaultdict
# Define Pydantic models for request and response
class DataPoint(BaseModel):
    opentime: int
    symbol: str
    open: str
    high: str
    low: str
    close: str
    volume: str
    tradenum: int
    volume_imbalance: str
    spread: str
    liquidity_imbalance: str
    max_bid_size: str
    max_ask_size: str
    max_bid_price: str
    max_ask_price: str
    bid_vwap: str
    ask_vwap: str
    mid_price: str
    imbalance_level_5: str
    imbalance_level_10: str


class PredictionRequest(BaseModel):
    data: List[DataPoint]


# Initialize FastAPI app
app = FastAPI(title="TFT Prediction API")

# Global variables for data storage
assets_df = None
oldData = None

# Define functions for calculations
def ResidualizeMarket(df, mktColumn, window):
    if mktColumn not in df.columns:
        return df

    mkt = df[mktColumn]
    num = df.multiply(mkt.values, axis=0).rolling(window).mean()
    denom = mkt.multiply(mkt.values, axis=0).rolling(window).mean()
    beta = np.nan_to_num(num.values.T / denom.values, nan=0.0, posinf=0.0, neginf=0.0)

    resultRet = df - (beta * mkt.values).T
    resultBeta = 0.0 * df + beta.T

    return resultRet.drop(columns=[mktColumn]), resultBeta.drop(columns=[mktColumn])


def log_return_ahead(series, periods=1):
    return np.exp(-np.log(series).diff(periods=-periods).shift(-1)) - 1


def getTarget(df, assets_df, countData):
    prices = df.pivot(index=["opentime"], columns=["symbol"], values=["close"])
    log_returns_15min = log_return_ahead(prices, periods=15)
    weights = assets_df.weight.values
    weighted_avg_market_log_returns = log_returns_15min.mul(weights, axis='columns').div(
        log_returns_15min.notnull().mul(weights, axis='columns').sum(axis=1), axis=0).sum(axis=1)

    log_returns_15min["market"] = weighted_avg_market_log_returns
    residualized_market_returns, beta = ResidualizeMarket(log_returns_15min, "market", window=3750)

    residualized_market_returns_stacked = residualized_market_returns.stack('symbol', future_stack=True)

    residualized_market_returns_stacked.rename(columns={'close': 'Target'}, inplace=True)

    itg_data = df.set_index(['opentime', 'symbol']).join(residualized_market_returns_stacked).sort_index()[-countData:]


    itg_data = itg_data.fillna(0)
    timedelta = itg_data.index.get_level_values('opentime') - itg_data.index.get_level_values('opentime').min()
    itg_data['time_idx'] = timedelta.total_seconds() / 60

    minutes_since_midnight = itg_data.index.get_level_values('opentime').hour * 60 + itg_data.index.get_level_values('opentime').minute
    itg_data['minutes_since_midnight'] = minutes_since_midnight

    itg_data = itg_data.join(assets_df)
    itg_data = itg_data.reset_index()
    itg_data['time_idx'] = itg_data['time_idx'].astype('int')
    itg_data['symbol'] = itg_data['symbol'].astype('str')
    itg_data['minutes_since_midnight'] = itg_data['minutes_since_midnight'].astype('str')

    return itg_data

# Lifespan event handler to load data on startup
@asynccontextmanager
async def lifespan(app: FastAPI):
    global assets_df, oldData, model
    try:
        assets_df = pd.read_csv('symbolWeight.csv', index_col="symbol")
        assets_df.sort_index(inplace=True)
        oldData = pd.read_csv('oldData.csv', parse_dates=['opentime'])
        model = TemporalFusionTransformer.load_from_checkpoint(os.path.join('ml_service', 'model', '1ep_80.ckpt'))
        model.eval()
        model.cuda()
        print("Data and model loaded successfully.")
    except FileNotFoundError as e:
        print(f"Error loading files: {e}")
        oldData = pd.DataFrame(columns=[...])
        assets_df = pd.DataFrame(columns=["weight"])
        model = None
    yield
    try:
        oldData.to_csv('oldData.csv', index=False)
        print("Data saved successfully.")
    except Exception as e:
        print(f"Error saving data: {e}")

# Set lifespan event handler
app = FastAPI(title="TFT Prediction API", lifespan=lifespan)



@app.post("/testpredict")
def save_datatest():
    global oldData, assets_df
    # oldData = pd.read_csv('oldData.csv', parse_dates=['opentime'])
    currentData = pd.read_csv("tes.csv")
    # assets_df = pd.read_csv('symbolWeight.csv', index_col="symbol")
    # assets_df.sort_index(inplace=True)

    currentData['opentime'] = pd.to_datetime(currentData['opentime'] / 1000, unit='s', utc=True)
    countData = currentData.shape[0]

    oldData = pd.concat([oldData, currentData], axis=0)
    oldData = oldData.drop_duplicates()
    
    
    data_to_pred = getTarget(oldData.sort_values('opentime'), assets_df, countData)

    data_predictions = model.predict(data_to_pred, mode="raw", return_x=True).output.prediction.cpu()

    data_to_pred['opentime'] = (data_to_pred['opentime'].view('int64') // 1_000_000).astype('int64')


    dates = sorted(data_to_pred['opentime'].unique())
    symbols = sorted(data_to_pred.symbol.unique())

    historicel_data = {symbol: {int(date): float(data_to_pred[(data_to_pred.opentime == date) & (data_to_pred.symbol == symbol)].Target.values[0]) for date in dates[:-16]} for symbol in symbols}
    
    
    index = pd.MultiIndex.from_product([symbols, dates[-16:], range(7)], names=['symbol', 'timestamp', 'quantiles'])
    prediction_df = pd.DataFrame(data_predictions.flatten(), index=index, columns=['target'])
    prediction_df = prediction_df.reset_index()

    out_pred = {
        symbol: {
            int(date): {
                f'quantile_{i}': float(prediction_df[(prediction_df.symbol == symbol) & (prediction_df.timestamp == date) & (prediction_df.quantiles == i)].target.values[0])
                for i in range(7)
            }
            for date in dates[-16:]
        }
        for symbol in symbols
    }

    return {"data": historicel_data, "predictions": out_pred}


# Prediction endpoint
@app.post("/predict")
def save_data(request: PredictionRequest):
    global oldData
    data = [dp.model_dump() for dp in request.data]

    dtype_mapping = {
        "opentime": "int64",
        "symbol": "object",
        "open": "float64",
        "high": "float64",
        "low": "float64",
        "close": "float64",
        "volume": "float64",
        "tradenum": "int64",
        "volume_imbalance": "float64",
        "spread": "float64",
        "liquidity_imbalance": "float64",
        "max_bid_size": "float64",
        "max_ask_size": "float64",
        "max_bid_price": "float64",
        "max_ask_price": "float64",
        "bid_vwap": "float64",
        "ask_vwap": "float64",
        "mid_price": "float64",
        "imbalance_level_5": "float64",
        "imbalance_level_10": "float64",
    }

    currentData = pd.DataFrame(data).astype(dtype_mapping)

    currentData['opentime'] = pd.to_datetime(currentData['opentime'] / 1000, unit='s', utc=True)
    countData = currentData.shape[0]

    oldData = pd.concat([oldData, currentData], axis=0)
    oldData = oldData.drop_duplicates()
    
    
    data_to_pred = getTarget(oldData.sort_values('opentime'), assets_df, countData)

    data_predictions = model.predict(data_to_pred, mode="raw", return_x=True).output.prediction.cpu()

    data_to_pred['opentime'] = (data_to_pred['opentime'].view('int64') // 1_000_000).astype('int64')


    dates = sorted(data_to_pred['opentime'].unique())
    symbols = sorted(data_to_pred.symbol.unique())

    historicel_data = {symbol: {int(date): float(data_to_pred[(data_to_pred.opentime == date) & (data_to_pred.symbol == symbol)].Target.values[0]) for date in dates[:-16]} for symbol in symbols}
    
    
    
    index = pd.MultiIndex.from_product([symbols, dates[-16:], range(7)], names=['symbol', 'timestamp', 'quantiles'])
    prediction_df = pd.DataFrame(data_predictions.flatten(), index=index, columns=['target'])
    prediction_df = prediction_df.reset_index()

    out_pred = {
        symbol: {
            int(date): {
                f'quantile_{i}': float(prediction_df[(prediction_df.symbol == symbol) & (prediction_df.timestamp == date) & (prediction_df.quantiles == i)].target.values[0])
                for i in range(7)
            }
            for date in dates[-16:]
        }
        for symbol in symbols
    }

    return {"data": historicel_data, "predictions": out_pred}

# Root endpoint
@app.get("/")
def read_root():
    return {"message": "TFT Prediction API is up and running."}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
