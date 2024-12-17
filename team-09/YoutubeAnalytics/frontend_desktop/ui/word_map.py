from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt5.QtGui import QPixmap, QImage
from wordcloud import WordCloud
from PIL import Image, ImageQt
from stop_words import safe_get_stop_words


class WordMap(QWidget):
    def __init__(self, flags: Qt.WindowFlags = Qt.WindowFlags()) -> None:
        super().__init__(None, flags)

        self.__word_map_pos = QLabel()
        self.__word_map_neg = QLabel()

        layout = QVBoxLayout()
        layout.addWidget(self.__word_map_pos)
        layout.addWidget(self.__word_map_neg)
        self.setLayout(layout)

        self.__stop_words = safe_get_stop_words('en')

    def create_word_map(self, freq: dict) -> QPixmap:
        if "video" in freq:
            freq.pop("video")
        if "emoji" in freq:
            freq.pop("emoji")

        wordcloud = WordCloud(width=800,
                              height=400,
                              random_state=1,
                              background_color='white',
                              relative_scaling=1,
                            #   collocations=False,
                              stopwords=self.__stop_words).generate_from_frequencies(freq)

        pil_img = wordcloud.to_image()
        qim = QImage(pil_img.tobytes('raw', "RGBA"), 800, 400, QImage.Format.Format_RGBA8888)

        return QPixmap.fromImage(qim)

    def draw(self, data: dict) -> None:
        pos = data["pos_freq"]
        neg = data["neg_freq"]

        self.__word_map_pos.setPixmap(self.create_word_map(pos))
        self.__word_map_neg.setPixmap(self.create_word_map(neg))
