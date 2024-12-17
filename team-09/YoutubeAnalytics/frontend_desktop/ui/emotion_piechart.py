from PyQt5.QtWidgets import QVBoxLayout, QWidget
from PyQt5.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt


class EmotionPieChart(QWidget):
    def __init__(self):
        super(EmotionPieChart, self).__init__(None)
        self.__figure, self.__ax = plt.subplots()
        self.__canvas = FigureCanvas(self.__figure)
        
        layout = QVBoxLayout()
        layout.addWidget(self.__canvas)
        self.setLayout(layout)
        
    def draw(self, data: dict) -> None:
        labels = list(data.keys())
        sizes = list(data.values())

        if len(labels) == 0:
            return
        
        self.__ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, colors=plt.cm.Paired.colors)
        self.__canvas.draw()
        
    def clear_graph(self) -> None:
        self.__ax.cla()
