from pyqtgraph import PlotWidget, BarGraphItem


class CommentsByLang(PlotWidget):
    def __init__(self, parent=None, background='default', plotItem=None, **kargs):
        super().__init__(parent, background, plotItem, **kargs)
        
        self.setBackground("w")
        
        self.__bar_graph = None
        
    def draw(self, data: dict) -> None:
        x = list(data.keys())
        y = list(data.values())

        if len(x) == 0:
            return

        self.__bar_graph = BarGraphItem(x=range(len(x)), height=y, width=0.6, brush='b')

        self.addItem(self.__bar_graph)

        axis = self.getAxis('bottom')
        axis.setTicks([[(i, label) for i, label in enumerate(x)]])
        
    def clear_graph(self) -> None:
        self.clear()
        self.removeItem(self.__bar_graph)
