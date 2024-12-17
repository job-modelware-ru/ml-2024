# Скачивание данных

## Получить данные каналов по категории
При выполнении запроса каналы скачиваются полностью, т.е. генерируются запросы на скачивание видео с каждого канала и запросы на скачивание комментариев с каждого видео
```json
{
    "type": 0,
    "tasks_left": 1,
    "completed": false,
    "date_completion": null,
    "data": {
        "category": "some_category"
    }
}
```

## Получить данные канала по его id
При выполнении запроса по мимо информации о канале скачиваются все видео с этого канала и комментарии к каждому видео, т.е. генерируются соответсвующие запросы
```json
{
    "type": 1,
    "tasks_left": 1,
    "completed": false,
    "date_completion": null,
    "data": {
        "channel_id": "some_channel_id",
        "category": "some_category_or_null"
    }
}
```

## Получить данные о видео с канала
В поле "tasks_left" нужно указать целое число, а именно количество видео на канале деленное на 50 (округлять в большую сторону). В поле "data.playlist_id" нужно указать "channel_id", но при этом заменить второй символ (который должен быть "C") на "U". В данном случае скачаются все видео с канала и их комментарии. Можно также укзать id конкретного плейлиста, но тогда заменять ничего не нужно, а просто указать id плейлиста
```json
{
    "type": 2,
    "tasks_left": 3,
    "completed": false,
    "date_completion": null,
    "data": {
        "playlist_id": "some_playlist_id",
        "pageToken": null
    }
}
```

## Получить данные о видео по его id
При выполнении данного запроса также будут скачаны комментарии к видео
```json
{
    "type": 3,
    "tasks_left": 1,
    "completed": false,
    "date_completion": null,
    "data": {
        "video_id": "some_video_id",
    }
}
```

## Получить данные о комментариях по видео id
В поле "tasks_left" нужно указать целое число, а именно количество комментариев деленное на 100 (округление в большую сторону). 
```json
{
    "type": 4,
    "tasks_left": 6,
    "completed": false,
    "date_completion": null,
    "data": {
        "video_id": "some_vieo_id",
        "pageToken": null
    }
}
```

## Получить данные о канале по url
Есть вероятность, что скачается не тот канал, поэтому этим лучше не пользоваться. Пример url: https://www.youtube.com/@NeetCode. В данном случае скачаются все видео с канала и их комментарии
```json
{
    "type": 5,
    "tasks_left": 1,
    "completed": false,
    "date_completion": null,
    "data": {
        "channel_url": "some_channel_url",
    }
}
```

## Получить данные о канале по видео id с канала
В данном случае скачаются все видео с канала и их комментарии, а также сам канал
```json
{
    "type": 6,
    "tasks_left": 1,
    "completed": false,
    "date_completion": null,
    "data": {
        "video_id": "some_video_id",
    }
}
```