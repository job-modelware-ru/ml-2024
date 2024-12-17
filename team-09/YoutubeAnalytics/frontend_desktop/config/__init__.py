from decouple import config


API_URL = config('API_URL')

GET_CHANNELS_BY_CATEGORY = 0
GET_CHANNEL_BY_ID = 1
GET_VIDEOS_BY_CHANNEL_ID = 2
GET_VIDEO_BY_ID = 3
GET_COMMENTS_BY_VIDEO_ID = 4
GET_CHANNEL_BY_URL = 5
GET_CHANNEL_BY_VIDEO_ID = 6

GET_ANALYSIS_OF_TIME = 7
GET_ANALYSIS_OF_LANGUAGES = 8
GET_ANALYSIS_OF_EMOTION = 9
GET_ANALYSIS_OF_LIKES_VS_REPLIES = 10
GET_ANALYSIS_OF_NEQ_POS = 11
GET_POPULARITY = 12
GET_WORD_MAP = 13

type_request_str = {
    GET_CHANNELS_BY_CATEGORY: "Скачать данные канала по категориям",
    GET_CHANNEL_BY_ID: "Скачать данные канала по id",
    GET_VIDEOS_BY_CHANNEL_ID: "Скачать данные видео по id канала",
    GET_VIDEO_BY_ID: "Скачать данные видео по его id",
    GET_COMMENTS_BY_VIDEO_ID: "Скачать данные комментариев по id видео",
    GET_CHANNEL_BY_URL: "Скачать данные канала по url",
    GET_CHANNEL_BY_VIDEO_ID: "Скачать данные канала по видео id",
    GET_ANALYSIS_OF_TIME: "Построить аналитику коментариев от времени",
    GET_ANALYSIS_OF_LANGUAGES: "Построить аналитику комментариев по языкам",
    GET_ANALYSIS_OF_EMOTION: "Построить аналитику эмоциональности комментариев",
    GET_ANALYSIS_OF_LIKES_VS_REPLIES: "Построить аналитику количества лайков от ответов",
    GET_ANALYSIS_OF_NEQ_POS: "Построить аналитику позитивных, негативных комментариев",
    GET_POPULARITY: "Построить аналитику популярности видео",
    GET_WORD_MAP: "Построить аналитику карты слов",
}

graphics_types = {
    GET_ANALYSIS_OF_TIME: "Количество комментариев от времени",
    GET_ANALYSIS_OF_LANGUAGES: "Комментарии по языкам",
    GET_ANALYSIS_OF_EMOTION: "Эмоциональность",
    GET_ANALYSIS_OF_LIKES_VS_REPLIES: "Количество лайков от ответов",
    GET_ANALYSIS_OF_NEQ_POS: "Негативные и позитивные коментарии",
    GET_POPULARITY: "Популярность",
    GET_WORD_MAP: "Карта слов"
}
