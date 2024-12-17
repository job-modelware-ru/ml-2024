from PyQt5.QtWidgets import QStackedWidget, QWidget
from ui.comments_by_time_graph import CommentsByTime
from ui.comments_by_lang import CommentsByLang
from ui.emotion_piechart import EmotionPieChart
from ui.replies_by_likes import RepliesByLikes
from ui.neg_pos_piechart import NegPosPieChart
from ui.word_map import WordMap
from config import GET_ANALYSIS_OF_TIME, GET_ANALYSIS_OF_LANGUAGES,\
    GET_ANALYSIS_OF_EMOTION, GET_ANALYSIS_OF_LIKES_VS_REPLIES,\
    GET_ANALYSIS_OF_NEQ_POS, GET_WORD_MAP


class GraphicsWidget(QStackedWidget):
    def __init__(self) -> None:
        super().__init__(None)

        self.__comments_by_time = CommentsByTime()
        self.__comments_by_lang = CommentsByLang()
        self.__emotion_piechart = EmotionPieChart()
        self.__replies_by_likecount = RepliesByLikes()
        self.__neg_pos_piechart = NegPosPieChart()
        self.__word_map = WordMap()

        self.addWidget(self.__comments_by_time)
        self.addWidget(self.__comments_by_lang)
        self.addWidget(self.__emotion_piechart)
        self.addWidget(self.__replies_by_likecount)
        self.addWidget(self.__neg_pos_piechart)
        self.addWidget(self.__word_map)
        
    def draw_comments_by_time(self, times: list, comments_count: list) -> None:
        self.__comments_by_time.draw(times, comments_count)
        
    def draw(self, data: dict, type: int) -> None:
        if type == GET_ANALYSIS_OF_TIME:
            self.__comments_by_time.clear_graph()
            self.draw_comments_by_time(data["metric"][0], data["metric"][1])
            self.setCurrentWidget(self.__comments_by_time)
        elif type == GET_ANALYSIS_OF_LANGUAGES:
            self.__comments_by_lang.clear_graph()
            self.__comments_by_lang.draw(data["metric"])
            self.setCurrentWidget(self.__comments_by_lang)
        elif type == GET_ANALYSIS_OF_EMOTION:
            self.__emotion_piechart.clear_graph()
            self.__emotion_piechart.draw(data["metric"])
            self.setCurrentWidget(self.__emotion_piechart)
        elif type == GET_ANALYSIS_OF_LIKES_VS_REPLIES:
            self.__replies_by_likecount.clear_graph()
            self.__replies_by_likecount.draw(data["metric"])
            self.setCurrentWidget(self.__replies_by_likecount)
        elif type == GET_ANALYSIS_OF_NEQ_POS:
            self.__neg_pos_piechart.clear_graph()
            self.__neg_pos_piechart.draw(data["metric"])
            self.setCurrentWidget(self.__neg_pos_piechart)
        elif type == GET_WORD_MAP:
            self.__word_map.draw(data["metric"])
            self.setCurrentWidget(self.__word_map)
