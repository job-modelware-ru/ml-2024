from PyQt5.QtWidgets import QApplication, QTreeWidget, QTreeWidgetItem, QVBoxLayout, QWidget
from PyQt5.QtCore import Qt, pyqtSignal


class VideosTree(QWidget):
    item_select = pyqtSignal(str, bool)
    
    def __init__(self):
        super().__init__()
        
        self.__tree = QTreeWidget(self)
        self.__tree.setHeaderHidden(True)
        
        self.__tree.currentItemChanged.connect(self.current_item_change)

        self.__layout = QVBoxLayout()
        self.setLayout(self.__layout)
        self.__layout.addWidget(self.__tree)
        self.__layout.setSpacing(0)
        self.__layout.setContentsMargins(0, 0, 0, 0)

    def fill(self, channels: list) -> None:
        self.__tree.clear()

        for channel in channels:
            channelItem = QTreeWidgetItem(self.__tree)
            channelItem.setText(0, channel["title"])
            channelItem.setData(0, Qt.ItemDataRole.UserRole, channel["id"])

            for video in channel["videos"]:
                videoItem = QTreeWidgetItem(channelItem)
                videoItem.setText(0, video["title"])
                videoItem.setData(0, Qt.ItemDataRole.UserRole, video["video_id"])
    
    def get_current_id(self) -> (str, bool):
        cur_item = self.__tree.currentItem()
        if cur_item is None:
            return ('', True)
        
        is_channel = False

        if cur_item.parent() == self.__tree.itemFromIndex(self.__tree.rootIndex()):
            is_channel = True
            
        return (cur_item.data(0, Qt.ItemDataRole.UserRole), is_channel)
    
    def current_item_change(self, cur: QTreeWidgetItem, prev: QTreeWidgetItem) -> None:
        is_channel = False
        
        if cur.parent() == self.__tree.itemFromIndex(self.__tree.rootIndex()):
            is_channel = True
            
        self.item_select.emit(cur.data(0, Qt.ItemDataRole.UserRole), is_channel)
        