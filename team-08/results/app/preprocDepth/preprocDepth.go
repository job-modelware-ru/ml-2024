package preprocDepth

import (
	"fmt"
	"math"
	"strconv"

	"github.com/adshao/go-binance/v2"
)

// DepthData - структура для хранения агрегации данных depth.
type DepthData struct {
	VolumeImbalance    string // Дисбаланс объема заявок
	Spread             string // Относительный спред
	LiquidityImbalance string // Глубина рынка на лучших ценах
	MaxBidSize         string // Максимальный размер на стороне Bid
	MaxAskSize         string // Максимальный размер на стороне Ask
	MaxBidPrice        string // Цена с максимальным размером на стороне Bid
	MaxAskPrice        string // Цена с максимальным размером на стороне Ask
	BidVWAP            string // VWAP для Bid
	AskVWAP            string // VWAP для Ask
	MidPrice           string // Средняя цена
	CumBidVolume5      string // Кумулятивный объем Bid на 5 уровнях
	CumAskVolume5      string // Кумулятивный объем Ask на 5 уровнях
	ImbalanceLevel5    string // Дисбаланс на 5 уровнях
	ImbalanceLevel10   string // Дисбаланс на 10 уровнях
}

// computeImbalance - вспомогательная функция для вычисления дисбаланса.
func computeImbalance(bidVolumes, askVolumes []float64, levels int) float64 {
	bidCum, askCum := 0.0, 0.0
	for i := 0; i < levels; i++ {
		if i < len(bidVolumes) {
			bidCum += bidVolumes[i]
		}
		if i < len(askVolumes) {
			askCum += askVolumes[i]
		}
	}
	return (bidCum - askCum) / (bidCum + askCum)
}

// NewDepthData - функция для создания структуры DepthData на основе *binance.DepthResponse.
func NewDepthData(depth *binance.DepthResponse) DepthData {
	var bidVolumes, askVolumes, bidPrices, askPrices []float64

	// Извлечение объемов и цен для Bid и Ask с обработкой ошибок.
	for _, bid := range depth.Bids {
		price, err := strconv.ParseFloat(bid.Price, 64)
		if err != nil {
			fmt.Printf("Ошибка преобразования цены bid: %v\n", err)
			continue
		}
		volume, err := strconv.ParseFloat(bid.Quantity, 64)
		if err != nil {
			fmt.Printf("Ошибка преобразования объема bid: %v\n", err)
			continue
		}
		bidPrices = append(bidPrices, price)
		bidVolumes = append(bidVolumes, volume)
	}

	for _, ask := range depth.Asks {
		price, err := strconv.ParseFloat(ask.Price, 64)
		if err != nil {
			fmt.Printf("Ошибка преобразования цены ask: %v\n", err)
			continue
		}
		volume, err := strconv.ParseFloat(ask.Quantity, 64)
		if err != nil {
			fmt.Printf("Ошибка преобразования объема ask: %v\n", err)
			continue
		}
		askPrices = append(askPrices, price)
		askVolumes = append(askVolumes, volume)
	}

	// Вычисление полей и преобразование в строку
	volumeImbalance := strconv.FormatFloat((sum(bidVolumes)-sum(askVolumes))/(sum(bidVolumes)+sum(askVolumes)), 'f', 6, 64)
	spread := strconv.FormatFloat((askPrices[0]-bidPrices[0])/((askPrices[0]+bidPrices[0])/2), 'f', 6, 64)
	liquidityImbalance := strconv.FormatFloat((bidVolumes[0]-askVolumes[0])/(bidVolumes[0]+askVolumes[0]), 'f', 6, 64)
	maxBidSize, maxBidIndex := max(bidVolumes)
	maxAskSize, maxAskIndex := max(askVolumes)
	maxBidPrice := strconv.FormatFloat(bidPrices[maxBidIndex], 'f', 6, 64)
	maxAskPrice := strconv.FormatFloat(askPrices[maxAskIndex], 'f', 6, 64)
	bidVWAP := strconv.FormatFloat(vwap(bidPrices, bidVolumes), 'f', 6, 64)
	askVWAP := strconv.FormatFloat(vwap(askPrices, askVolumes), 'f', 6, 64)
	midPrice := strconv.FormatFloat((askPrices[0]+bidPrices[0])/2, 'f', 6, 64)
	cumBidVolume5 := strconv.FormatFloat(sum(bidVolumes[:int(math.Min(5, float64(len(bidVolumes))))]), 'f', 6, 64)
	cumAskVolume5 := strconv.FormatFloat(sum(askVolumes[:int(math.Min(5, float64(len(askVolumes))))]), 'f', 6, 64)
	imbalanceLevel5 := strconv.FormatFloat(computeImbalance(bidVolumes, askVolumes, 5), 'f', 6, 64)
	imbalanceLevel10 := strconv.FormatFloat(computeImbalance(bidVolumes, askVolumes, 10), 'f', 6, 64)

	return DepthData{
		VolumeImbalance:    volumeImbalance,
		Spread:             spread,
		LiquidityImbalance: liquidityImbalance,
		MaxBidSize:         strconv.FormatFloat(maxBidSize, 'f', 6, 64),
		MaxAskSize:         strconv.FormatFloat(maxAskSize, 'f', 6, 64),
		MaxBidPrice:        maxBidPrice,
		MaxAskPrice:        maxAskPrice,
		BidVWAP:            bidVWAP,
		AskVWAP:            askVWAP,
		MidPrice:           midPrice,
		CumBidVolume5:      cumBidVolume5,
		CumAskVolume5:      cumAskVolume5,
		ImbalanceLevel5:    imbalanceLevel5,
		ImbalanceLevel10:   imbalanceLevel10,
	}
}

// sum - функция для расчета суммы значений в слайсе.
func sum(arr []float64) float64 {
	result := 0.0
	for _, val := range arr {
		result += val
	}
	return result
}

// max - функция для нахождения максимального значения и его индекса в слайсе.
func max(arr []float64) (float64, int) {
	maxVal := arr[0]
	maxIndex := 0
	for i, val := range arr {
		if val > maxVal {
			maxVal = val
			maxIndex = i
		}
	}
	return maxVal, maxIndex
}

// vwap - функция для вычисления VWAP.
func vwap(prices, volumes []float64) float64 {
	totalPriceVolume := 0.0
	totalVolume := 0.0
	for i := range prices {
		totalPriceVolume += prices[i] * volumes[i]
		totalVolume += volumes[i]
	}
	return totalPriceVolume / totalVolume
}
