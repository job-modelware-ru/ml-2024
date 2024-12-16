from PyQt5.QtWidgets import QApplication
from ui.main_window import MainWindow


app = QApplication([])
main = MainWindow()
main.showMaximized()
app.exec()
