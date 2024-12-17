from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QListWidget, QListWidgetItem, QSplitter

from ui.download_widget import UrlWidget
from ui.left_panel import LeftPanel
from ui.requests_table import RequestsTable
from ui.graphics_widget import GraphicsWidget

from core.data_updater import DataUpdater

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.__main_layout = QVBoxLayout()
        self.__url_widget = UrlWidget()
        self.__data_updater = DataUpdater()
        self.__left_panel = LeftPanel()
        self.__requests_table = RequestsTable()
        self.__graphics_widget = GraphicsWidget()

        self.__left_panel.update_button_click.connect(self.__data_updater.fetch_data)

        self.__main_layout.addWidget(self.__url_widget)
        self.__main_layout.addWidget(self.__graphics_widget)

        splitter = QSplitter()

        widget = QWidget()
        widget.setLayout(self.__main_layout)

        splitter.addWidget(self.__left_panel)
        splitter.addWidget(widget)
        splitter.addWidget(self.__requests_table)
        self.setCentralWidget(splitter)

        self.__data_updater.channels_videos_fetch.connect(
            self.__left_panel.fill_videos_tree
        )

        self.__data_updater.requests_fetch.connect(
            self.__requests_table.fill
        )

        self.__left_panel.analyze.connect(
            self.__data_updater.send_analyze_request
        )
        
        self.__url_widget.download.connect(
            self.__data_updater.send_download_data_request
        )
        
        self.__left_panel.analytics.connect(
            lambda id, is_channel: self.__data_updater.get_analytics(id, is_channel, self.__left_panel.get_cur_analytic_type())
        )
        
        self.__data_updater.analytic_fetch.connect(
            lambda data: self.__graphics_widget.draw(data, self.__left_panel.get_cur_analytic_type())
        )
        
        self.__data_updater.fetch_data()
