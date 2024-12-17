package fetchAdditionalData

import (
	"MyCrypto/database"
	"encoding/json"
	"fmt"
	"io"
	"os"
	"strings"
	"sync"
	"time"

	SDK "github.com/CoinAPI/coinapi-sdk/data-api/go-rest/v1"
	"go.mongodb.org/mongo-driver/mongo"
)

type Keys struct {
	Keys []string `json:"keys"`
}

func FetchAdditionalData(db *mongo.Database, LatestDataTime time.Time) error {

	symbols := strings.Split(os.Getenv("Symbols"), ",")

	// currentTime := time.Now().UTC().Format(time.RFC3339)

	// dateNow, _ := time.Parse(time.RFC3339, currentTime)

	// dateNow, _ := time.Parse(time.RFC3339, os.Getenv("DataEnd"))

	// dateNow := time.Now().UTC()

	ApiKeys, err := loadApiKeys("apiKeys.json")
	if err != nil {
		return fmt.Errorf("error loading API keys: %v", err)
	}

	apiKeyChan := make(chan string, len(ApiKeys))
	for _, key := range ApiKeys {
		apiKeyChan <- key
	}
	close(apiKeyChan)

	var wg sync.WaitGroup
	for _, symbol := range symbols {
		wg.Add(1)
		go func(symbol string) {
			defer wg.Done()
			for {
				key := <-apiKeyChan
				sdk := SDK.NewSDK(key)

				// orderbooksHistoricalData, err := sdk.Orderbooks_historical_data_with_time_end_and_limit(symbol, dateNow, dateNow, 1000)
				orderbooksHistoricalData, err := sdk.Orderbooks_latest_data_with_limit(symbol, 100000)

				if err != nil {
					fmt.Printf("Error fetching historical order book data for API_KEY: %s, Symbol: %s\n", key, symbol)
					// Если возникает ошибка, попытаться с другим ключом
					if len(apiKeyChan) > 0 {
						continue
					} else {
						// Если ключи закончились, записать ошибку и выйти
						fmt.Printf("No more API keys available. Error: %v\n", err)
						return
					}

				}

				fmt.Printf("Получено %d данных для символа %s\n", len(orderbooksHistoricalData), symbol)
				database.SaveD(db, orderbooksHistoricalData, symbol)

				orderbooksHistoricalData = aggregateOrderbooks(orderbooksHistoricalData)
				fmt.Printf("Данных после агрегации %d для символа %s\n", len(orderbooksHistoricalData), symbol)
				aggregate_symbol := fmt.Sprintf("%s_aggregate", symbol)
				database.SaveD(db, orderbooksHistoricalData, aggregate_symbol)

				// Сохранение данных в базу данных
				// Пример: err = saveDataToDB(db, orderbooksHistoricalData)
				if err != nil {
					fmt.Printf("Error saving data for symbol: %s, error: %v\n", symbol, err)
				}
				// Если данные успешно получены, выходим из цикла
				break
			}
		}(symbol)
	}

	wg.Wait()
	fmt.Printf("все данные получены")
	time.Sleep(time.Second * 30)

	return nil
}

func aggregateOrderbooks(orderbooks []SDK.Orderbook) []SDK.Orderbook {
	// Мапа для хранения самых актуальных записей
	latestRecords := make(map[string]SDK.Orderbook)

	for _, ob := range orderbooks {
		// Преобразуем время к формату "год-месяц-день-час-минута"
		key := fmt.Sprintf("%s-%d-%02d-%02d-%02d-%02d",
			ob.Symbol_id,
			ob.Time_exchange.Year(),
			ob.Time_exchange.Month(),
			ob.Time_exchange.Day(),
			ob.Time_exchange.Hour(),
			ob.Time_exchange.Minute(),
		)

		// Если запись в мапе еще не существует или текущая запись новее, обновляем мапу
		if existing, found := latestRecords[key]; !found || ob.Time_exchange.After(existing.Time_exchange) {
			latestRecords[key] = ob
		}
	}

	// После агрегации округляем время до меньшей минуты
	for key, ob := range latestRecords {
		// Округляем время в меньшую сторону до начала текущей минуты
		roundedTime := ob.Time_exchange.Truncate(time.Minute)

		// Обновляем запись в мапе, сохраняя округленное время и другие поля
		latestRecords[key] = SDK.Orderbook{
			Symbol_id:     ob.Symbol_id,
			Time_exchange: roundedTime,
			// Копируем остальные поля, включая bids и asks
			Bids: ob.Bids, // Здесь добавьте ваши поля
			Asks: ob.Asks, // Здесь добавьте ваши поля
			// Если есть другие поля, добавьте их сюда
		}
	}

	// Преобразуем мапу обратно в слайс
	aggregatedOrderbooks := make([]SDK.Orderbook, 0, len(latestRecords))
	for _, ob := range latestRecords {
		aggregatedOrderbooks = append(aggregatedOrderbooks, ob)
	}

	return aggregatedOrderbooks
}

func loadApiKeys(filename string) ([]string, error) {
	file, err := os.Open(filename)
	if err != nil {
		return nil, err
	}
	defer file.Close()

	bytes, err := io.ReadAll(file)
	if err != nil {
		return nil, err
	}

	var config Keys
	err = json.Unmarshal(bytes, &config)
	if err != nil {
		return nil, err
	}
	return config.Keys, nil
}
