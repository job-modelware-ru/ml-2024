package main

import (
	"MyCrypto/database"
	"MyCrypto/preprocDepth"
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"os"
	"strconv"
	"strings"
	"sync"
	"time"

	"github.com/adshao/go-binance/v2"
	"github.com/gin-gonic/gin"
	"github.com/gorilla/websocket"
	"github.com/joho/godotenv"
	"go.mongodb.org/mongo-driver/mongo"
)

var upgrader = websocket.Upgrader{
	ReadBufferSize:  1024,
	WriteBufferSize: 1024,
	CheckOrigin: func(r *http.Request) bool {
		return true
	},
}

var (
	priceDataMap      sync.Map
	dataUpdateChannel = make(chan *binance.WsKlineEvent)
	wg                sync.WaitGroup
)

// Shared KlineCounter to synchronize symbol processing
type KlineCounter struct {
	sync.Mutex
	counts map[int64]int
}

var klineCounter = &KlineCounter{
	counts: make(map[int64]int),
}

var totalSymbols int

type HistoricalData map[string]map[int64]float64

// Predictions представляет предсказания с квантилями.
type Predictions map[string]map[int64]map[string]float64

// MLResponse представляет структуру данных, возвращаемую ML-сервисом.
type MLResponse struct {
	HistoricalData HistoricalData `json:"data"`
	Predictions    Predictions    `json:"predictions"`
}

// WebSocketPayload defines the structure sent over WebSocket
type WebSocketPayload struct {
	PriceData map[string]binance.WsKline `json:"priceData"`
	MLData    *MLResponse                `json:"mlData,omitempty"`
}

// Global variables to store the latest MLResponse
var (
	latestMLResponse *MLResponse
	mlResponseMutex  sync.RWMutex
)

func main() {
	err := godotenv.Load(".env")
	if err != nil {
		log.Fatal("Error loading .env file")
	}
	port := os.Getenv("ServerPort")

	client, ctx, err := database.ConnectToDatabase()
	if err != nil {
		log.Fatal(err)
	}
	defer database.CloseDatabase(client, ctx)

	db := client.Database(os.Getenv("DbName"))
	fmt.Print("Успешное подключение к базе данных!\n")

	LatestDataTime, err := database.GetLatestTimeExchange(db)
	if err != nil {
		log.Fatal(err)
	}
	fmt.Println("Последняя дата в базе: ", LatestDataTime)

	symbols := strings.Split(os.Getenv("BINANCE_SYMBOLS"), ",")
	totalSymbols = len(symbols) // Store total number of symbols

	minCount, _ := strconv.ParseInt(os.Getenv("minCountDocuments"), 10, 64)
	minCountDocuments := minCount * int64(len(symbols))

	server := gin.New()
	server.Use(gin.Recovery(), gin.Logger())

	server.GET("/", func(c *gin.Context) {
		c.String(http.StatusOK, "Hello, World!")
	})

	// Обработчик для веб-сокета
	server.GET("/ws", func(c *gin.Context) {
		handleWebSocket(c)
	})

	// Запускаем обновление данных в отдельной горутине
	go updatePriceDataMap()

	// Подписываемся на все символы
	go subscribeToSymbols(db, symbols, minCountDocuments)

	server.Run(":" + port)
}

func subscribeToSymbols(db *mongo.Database, symbols []string, minCountDocuments int64) {
	for _, symbol := range symbols {
		wg.Add(1)
		go func(symbol string) {
			defer wg.Done()
			wsKlineHandler := func(event *binance.WsKlineEvent) {
				if event.Kline.IsFinal {
					depth := getDepth(symbol)
					depthData := preprocDepth.NewDepthData(depth)
					database.SaveData(db, depthData, event.Kline)

					// After saving to database, update the counter
					klineCloseTime := event.Kline.EndTime

					klineCounter.Lock()
					klineCounter.counts[klineCloseTime]++

					if klineCounter.counts[klineCloseTime] == totalSymbols {
						// All symbols have processed Kline for this CloseTime
						// Now check if total number of documents > minCountDocuments
						totalDocuments, err := database.GetTotalDocumentCount(db)
						if err != nil {
							log.Println("Error getting document count:", err)
						} else if totalDocuments >= minCountDocuments {

							fmt.Println("Делается предсказание!")

							// // Тестовое предсказание
							// res, err := sendToMLServiceTest()
							// if err != nil {
							// 	log.Println("Error sending data to ML service:", err)
							// } else {
							// 	// Store the entire MLResponse
							// 	mlResponseMutex.Lock()
							// 	latestMLResponse = res
							// 	mlResponseMutex.Unlock()

							// 	// database.SaveHistoricalDataToDB(db, res.HistoricalData)
							// 	respJSON, err := json.MarshalIndent(res, "", "  ")
							// 	if err != nil {
							// 		fmt.Println("error marshaling predictions: %v", err)
							// 	}
							// 	fmt.Println("ML Response from service:")
							// 	fmt.Println(string(respJSON))
							// }

							// Если нужно использовать реальные данные, расскоментировать:

							r, _ := database.GetDataFromDB(db, minCountDocuments)
							res, err := sendToMLService(r)
							if err != nil {
								log.Println("Error sending data to ML service:", err)
							} else {
								mlResponseMutex.Lock()
								latestMLResponse = res
								mlResponseMutex.Unlock()

								respJSON, err := json.MarshalIndent(res, "", "  ")
								if err != nil {
									fmt.Println("error marshaling predictions: %v", err)
								}
								fmt.Println("Predictions from ML service:")
								fmt.Println(string(respJSON))
							}

						}
						// Clean up to prevent memory leak
						delete(klineCounter.counts, klineCloseTime)
					}
					klineCounter.Unlock()
				}

				dataUpdateChannel <- event
			}

			errHandler := func(err error) {
				log.Println("Error:", err)
			}

			doneC, stopC, err := binance.WsKlineServe(symbol, "1m", wsKlineHandler, errHandler)
			if err != nil {
				log.Println("Error subscribing to kline data:", err)
				return
			}

			defer func() {
				stopC <- struct{}{}
			}()

			// Ожидание завершения соединения
			<-doneC
			log.Println("WebSocket closed for symbol:", symbol)
		}(symbol)
	}
	wg.Wait()
}

type PredictionRequest struct {
	Data []database.DataPoint `json:"data"`
}

func sendToMLServiceTest() (*MLResponse, error) {
	mlServiceURL := os.Getenv("mlServiceURL")
	if mlServiceURL == "" {
		return nil, fmt.Errorf("ML service URL is not set in environment variables")
	}

	resp, err := http.Post(mlServiceURL+"/testpredict", "application/json", nil)
	if err != nil {
		return nil, fmt.Errorf("error sending request to ML service: %v", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("received non-OK response from ML service: %d", resp.StatusCode)
	}

	var mlResponse MLResponse
	err = json.NewDecoder(resp.Body).Decode(&mlResponse)
	if err != nil {
		return nil, fmt.Errorf("error decoding ML service response: %v", err)
	}

	return &mlResponse, nil
}

func sendToMLService(data interface{}) (*MLResponse, error) {
	requestBody := map[string]interface{}{
		"data": data,
	}

	jsonData, err := json.Marshal(requestBody)
	if err != nil {
		return nil, fmt.Errorf("error marshaling data: %v", err)
	}

	mlServiceURL := os.Getenv("mlServiceURL")
	if mlServiceURL == "" {
		return nil, fmt.Errorf("ML service URL is not set in environment variables")
	}

	resp, err := http.Post(mlServiceURL+"/predict", "application/json", bytes.NewBuffer(jsonData))
	if err != nil {
		return nil, fmt.Errorf("error sending request to ML service: %v", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("received non-OK response from ML service: %d", resp.StatusCode)
	}

	var mlResponse MLResponse
	err = json.NewDecoder(resp.Body).Decode(&mlResponse)
	if err != nil {
		return nil, fmt.Errorf("error decoding ML service response: %v", err)
	}

	return &mlResponse, nil
}

func getDepth(symbol string) *binance.DepthResponse {
	client := binance.NewClient("", "")

	res, err := client.NewDepthService().Symbol(symbol).Limit(50).Do(context.Background())
	if err != nil {
		fmt.Println(err)
	}
	return res
}

func updatePriceDataMap() {
	for data := range dataUpdateChannel {
		priceDataMap.Store(data.Symbol, data.Kline)
	}
}

func handleWebSocket(c *gin.Context) {
	conn, err := upgrader.Upgrade(c.Writer, c.Request, nil)
	if err != nil {
		log.Println("Failed to set websocket upgrade: ", err)
		http.Error(c.Writer, "Failed to upgrade to websocket", http.StatusInternalServerError)
		return
	}
	defer conn.Close()

	for {
		// Создаем временную карту для хранения текущих данных
		tempMap := make(map[string]binance.WsKline)

		// Проходим по всем элементам sync.Map и копируем их в временную карту
		priceDataMap.Range(func(key, value interface{}) bool {
			symbol := key.(string)
			kline := value.(binance.WsKline)
			tempMap[symbol] = kline
			return true
		})

		// Получаем последние данные MLResponse
		mlResponseMutex.RLock()
		currentMLResponse := latestMLResponse
		mlResponseMutex.RUnlock()

		// Создаем payload для отправки
		payload := WebSocketPayload{
			PriceData: tempMap,
			MLData:    currentMLResponse,
		}

		if err := conn.WriteJSON(payload); err != nil {
			log.Println("WriteJSON error:", err)
			return
		}
		time.Sleep(time.Second * 1)
	}
}
