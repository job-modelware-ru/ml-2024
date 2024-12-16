from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QWidget, QComboBox, QVBoxLayout, QPushButton

from ui.videos_tree import VideosTree
from config import graphics_types


class LeftPanel(QWidget):
    update_button_click = pyqtSignal()
    analyze = pyqtSignal(str, bool)
    analytics = pyqtSignal(str, bool)
    
    def __init__(self, flags: Qt.WindowFlags = Qt.WindowFlags()) -> None:
        super().__init__(None, flags)
        
        self.__statistics_combobox = QComboBox()

        for row, (k, v) in enumerate(graphics_types.items()):
            self.__statistics_combobox.addItem(v)
            self.__statistics_combobox.setItemData(row, k, Qt.ItemDataRole.UserRole)
            
        self.__update_button = QPushButton("Обновить")
        self.__update_button.clicked.connect(self.update_button_click)
        
        self.__videos_tree = VideosTree()
        self.__videos_tree.item_select.connect(
            self.analytics
        )
        
        self.__analyze_button = QPushButton("Проанализировать")
        self.__analyze_button.clicked.connect(self.analyze_clicked)
        
        self.__layout = QVBoxLayout(self)
        self.__layout.addWidget(self.__update_button)
        self.__layout.addWidget(self.__statistics_combobox)
        self.__layout.addWidget(self.__videos_tree)
        self.__layout.addWidget(self.__analyze_button)
        
        self.__statistics_combobox.currentIndexChanged.connect(lambda x: self.analytics.emit(*self.__videos_tree.get_current_id()))
        
    def fill_videos_tree(self, channels: list) -> None:
        self.__videos_tree.fill(channels)
        
    def analyze_clicked(self) -> None:
        id, is_channel = self.__videos_tree.get_current_id()
        
        self.analyze.emit(id, is_channel)
        
    def get_cur_analytic_type(self) -> int:
        return self.__statistics_combobox.currentData(Qt.ItemDataRole.UserRole)
    