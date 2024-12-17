package database

import (
	"MyCrypto/preprocDepth"
	"context"
	"fmt"
	"log"
	"os"
	"time"

	SDK "github.com/CoinAPI/coinapi-sdk/data-api/go-rest/v1"
	"github.com/adshao/go-binance/v2"
	"go.mongodb.org/mongo-driver/bson"
	"go.mongodb.org/mongo-driver/mongo"
	"go.mongodb.org/mongo-driver/mongo/options"
	"go.mongodb.org/mongo-driver/mongo/readpref"
)

type HistoricalData map[string]map[int64]float64

type DataPoint struct {
	OpenTime           int64  `bson:"start_time" json:"opentime"`
	Symbol             string `bson:"symbol" json:"symbol"`
	Open               string `bson:"open" json:"open"`
	High               string `bson:"high" json:"high"`
	Low                string `bson:"low" json:"low"`
	Close              string `bson:"close" json:"close"`
	Volume             string `bson:"volume" json:"volume"`
	TradeNum           int64  `bson:"tradenum" json:"tradenum"`
	VolumeImbalance    string `bson:"volume_imbalance" json:"volume_imbalance"`
	Spread             string `bson:"spread" json:"spread"`
	LiquidityImbalance string `bson:"liquidity_imbalance" json:"liquidity_imbalance"`
	MaxBidSize         string `bson:"max_bid_size" json:"max_bid_size"`
	MaxAskSize         string `bson:"max_ask_size" json:"max_ask_size"`
	MaxBidPrice        string `bson:"max_bid_price" json:"max_bid_price"`
	MaxAskPrice        string `bson:"max_ask_price" json:"max_ask_price"`
	BidVWAP            string `bson:"bid_vwap" json:"bid_vwap"`
	AskVWAP            string `bson:"ask_vwap" json:"ask_vwap"`
	MidPrice           string `bson:"mid_price" json:"mid_price"`
	ImbalanceLevel5    string `bson:"imbalance_level_5" json:"imbalance_level_5"`
	ImbalanceLevel10   string `bson:"imbalance_level_10" json:"imbalance_level_10"`
}

func GetDataFromDB(db *mongo.Database, n int64) ([]DataPoint, error) {
	// Получаем имя коллекции из переменной окружения
	collection := db.Collection(os.Getenv("DbName"))

	// Создаем параметры запроса для сортировки по полю start_time в порядке убывания (от новейших)
	findOptions := options.Find()
	findOptions.SetLimit(n)
	findOptions.SetSort(bson.D{{"start_time", -1}})

	// Выполняем запрос
	ctx := context.Background()
	cursor, err := collection.Find(ctx, bson.M{}, findOptions)
	if err != nil {
		return nil, fmt.Errorf("ошибка при выполнении запроса Find: %v", err)
	}
	defer cursor.Close(ctx)

	// Считываем данные в срез
	var results []DataPoint
	for cursor.Next(ctx) {
		var dataPoint DataPoint
		if err := cursor.Decode(&dataPoint); err != nil {
			return nil, fmt.Errorf("ошибка при декодировании документа: %v", err)
		}
		results = append(results, dataPoint)
	}

	if err := cursor.Err(); err != nil {
		return nil, fmt.Errorf("ошибка курсора: %v", err)
	}

	return results, nil
}

func SaveData(db *mongo.Database, depth preprocDepth.DepthData, kline binance.WsKline) {
	// Получаем коллекцию по имени символа валюты
	collection := db.Collection(os.Getenv("DbName"))

	// Подготавливаем документ для вставки, добавляя данные из DepthData
	doc := map[string]interface{}{
		"symbol":                  kline.Symbol,
		"start_time":              kline.StartTime,
		"end_time":                kline.EndTime,
		"open":                    kline.Open,
		"close":                   kline.Close,
		"high":                    kline.High,
		"low":                     kline.Low,
		"volume":                  kline.Volume,
		"tradenum":                kline.TradeNum,
		"quoteassetvolume":        kline.QuoteVolume,
		"active_buy_volume":       kline.ActiveBuyVolume,
		"active_buy_quote_volume": kline.ActiveBuyQuoteVolume,
		// Данные из DepthData
		"volume_imbalance":    depth.VolumeImbalance,
		"spread":              depth.Spread,
		"liquidity_imbalance": depth.LiquidityImbalance,
		"max_bid_size":        depth.MaxBidSize,
		"max_ask_size":        depth.MaxAskSize,
		"max_bid_price":       depth.MaxBidPrice,
		"max_ask_price":       depth.MaxAskPrice,
		"bid_vwap":            depth.BidVWAP,
		"ask_vwap":            depth.AskVWAP,
		"mid_price":           depth.MidPrice,
		"cum_bid_volume_5":    depth.CumBidVolume5,
		"cum_ask_volume_5":    depth.CumAskVolume5,
		"imbalance_level_5":   depth.ImbalanceLevel5,
		"imbalance_level_10":  depth.ImbalanceLevel10,
	}

	_, err := collection.InsertOne(context.TODO(), doc)
	if err != nil {
		fmt.Printf("Ошибка при вставке данных для символа %s: %v\n", kline.Symbol, err)
		return
	}

	fmt.Printf("Данные для символа %s успешно сохранены в MongoDB\n", kline.Symbol)
}

func GetTotalDocumentCount(db *mongo.Database) (int64, error) {
	collection := db.Collection(os.Getenv("DbName"))
	totalDocuments, err := collection.CountDocuments(context.Background(), bson.D{})
	if err != nil {
		return 0, err
	}
	return totalDocuments, nil
}

func SaveHistoricalDataToDB(db *mongo.Database, historicalData HistoricalData) error {
	// Указываем имя коллекции для исторических данных
	collection := db.Collection(os.Getenv("DbName")) // Название коллекции можно изменить

	// Подготовим данные для вставки в базу данных
	var dataToInsert []interface{}
	for symbol, data := range historicalData {
		for timestamp, value := range data {
			document := map[string]interface{}{
				"symbol":    symbol,
				"timestamp": timestamp,
				"value":     value,
			}
			dataToInsert = append(dataToInsert, document)
		}
	}

	// Создаем контекст для работы с MongoDB
	ctx := context.Background()

	// Выполняем вставку в коллекцию
	_, err := collection.InsertMany(ctx, dataToInsert)
	if err != nil {
		return fmt.Errorf("error inserting historical data into database: %v", err)
	}

	return nil
}

func GetLatestTimeExchange(db *mongo.Database) (time.Time, error) {
	// Получаем коллекцию по имени символа
	collection := db.Collection(os.Getenv("DbName"))

	// Параметры поиска и сортировки
	opts := options.FindOne().SetSort(bson.D{{"start_time", -1}}) // Сортировка по убыванию даты

	// Структура для хранения результата
	var result struct {
		StartTime int64 `bson:"start_time"` // Дата в формате int64
	}

	// Выполняем запрос
	err := collection.FindOne(context.TODO(), bson.D{}, opts).Decode(&result)
	if err != nil {
		if err == mongo.ErrNoDocuments {
			// Если документов нет, возвращаем текущую дату
			return time.Now(), nil
		}
		return time.Time{}, fmt.Errorf("ошибка при получении последней даты start_time: %v", err)
	}

	// Преобразуем int64 в time.Time
	latestTime := time.Unix(0, result.StartTime*int64(time.Millisecond))

	// Возвращаем время в формате time.Time
	return latestTime, nil
}

// ConnectToDatabase подключается к базе данных и возвращает клиент MongoDB
func ConnectToDatabase() (*mongo.Client, context.Context, error) {
	// Получение хоста и порта из переменных окружения
	host := os.Getenv("Host")
	port := os.Getenv("DbPort")

	if host == "" || port == "" {
		return nil, nil, fmt.Errorf("Host или DbPort не заданы в переменных окружения")
	}

	// Формирование строки подключения
	connStr := fmt.Sprintf("mongodb://%s:%s", host, port)

	// Установите контекст с таймаутом
	ctx, cancel := context.WithTimeout(context.Background(), 120*time.Second)

	// Не вызываем defer cancel() здесь, контекст должен закрываться там, где используется
	clientOptions := options.Client().ApplyURI(connStr)

	// Подключение к MongoDB
	client, err := mongo.Connect(ctx, clientOptions)
	if err != nil {
		cancel() // Закрываем контекст, если подключение не удалось
		return nil, nil, fmt.Errorf("ошибка подключения к MongoDB: %v", err)
	}

	// Проверка подключения
	err = client.Ping(ctx, readpref.Primary())
	if err != nil {
		cancel() // Закрываем контекст, если не удалось выполнить пинг
		return nil, nil, fmt.Errorf("не удалось подключиться к базе данных: %v", err)
	}

	fmt.Println("Успешно подключено к MongoDB")

	// Возвращаем клиент и контекст
	return client, ctx, nil
}

// CloseDatabase завершает соединение с MongoDB
func CloseDatabase(client *mongo.Client, ctx context.Context) {
	if err := client.Disconnect(ctx); err != nil {
		log.Printf("Ошибка при отключении от MongoDB: %v", err)
	} else {
		fmt.Println("Соединение с MongoDB успешно закрыто")
	}
}

type Bid struct {
	Price string `json:"price"`
	Size  string `json:"size"`
}

type Orderbook struct {
	Symbol_id     string    `json:"symbol_id"`
	Time_exchange time.Time `json:"time_exchange"`
	Time_coinapi  time.Time `json:"time_coinapi"`
	Asks          []Bid     `json:"asks"`
	Bids          []Bid     `json:"bids"`
}

func SaveD(db *mongo.Database, Orderbooks_historical_data []SDK.Orderbook, symbol_id string) {
	// Получаем коллекцию по имени символа валюты
	collection := db.Collection(symbol_id)

	// Преобразуем данные в []interface{} для вставки в MongoDB

	var documents []interface{}
	for _, orderbook := range Orderbooks_historical_data {
		doc := Orderbook{
			Symbol_id:     orderbook.Symbol_id,
			Time_exchange: orderbook.Time_exchange,
			Time_coinapi:  orderbook.Time_coinapi,
		}

		// Преобразуем Asks
		for _, ask := range orderbook.Asks {
			doc.Asks = append(doc.Asks, Bid{
				Price: ask.Price.String(), // Преобразуем decimal.Decimal в строку
				Size:  ask.Size.String(),  // Преобразуем decimal.Decimal в строку
			})
		}

		// Преобразуем Bids
		for _, bid := range orderbook.Bids {
			doc.Bids = append(doc.Bids, Bid{
				Price: bid.Price.String(), // Преобразуем decimal.Decimal в строку
				Size:  bid.Size.String(),  // Преобразуем decimal.Decimal в строку
			})
		}
		documents = append(documents, doc)

	}

	// Вставляем данные в коллекцию
	_, err := collection.InsertMany(context.TODO(), documents)

	if err != nil {
		fmt.Printf("Ошибка при вставке данных для символа %s: %v\n", symbol_id, err)
		return
	}

	fmt.Printf("Данные для символа %s успешно сохранены в MongoDB\n", symbol_id)
}
