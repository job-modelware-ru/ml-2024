from pyqtgraph import PlotWidget, ScatterPlotItem
import numpy as np


class RepliesByLikes(PlotWidget):
    def __init__(self, parent=None, background='default', plotItem=None, **kargs):
        super().__init__(parent, background, plotItem, **kargs)
        
        self.setBackground("w")
        
        self.__scatter_plot = None
        
    def draw(self, data: dict) -> None:
        y = list(data["like_count"].values())
        x = list(data["reply_count"].values())
        
        if len(x) == 0:
            return
        
        self.__scatter_plot = ScatterPlotItem(x=x, y=y, pen=None, symbol='o', size=10, brush='b')
        
        self.addItem(self.__scatter_plot)
    
    def clear_graph(self) -> None:
        self.clear()
        self.removeItem(self.__scatter_plot)
