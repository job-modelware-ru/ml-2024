from pyqtgraph import PlotWidget, mkPen
import numpy as np
from datetime import datetime
from matplotlib.dates import date2num


class CommentsByTime(PlotWidget):
    def __init__(self, parent=None, background='default', plotItem=None, **kargs):
        super().__init__(parent, background, plotItem, **kargs)

        self.setBackground("w")
        self.__pen = mkPen(color=(255, 0, 0))

    def draw(self, times: list, comment_count: list) -> None:
        datetime_objects = [datetime.strptime(time, '%Y-%m-%dT%H:%M:%S') for time in times]
        counts = np.array(comment_count)
        
        x = date2num(datetime_objects)

        self.plot(x, counts, name='Count vs Time', pen=self.__pen)

        axis = self.getAxis('bottom')
        axis.setLabel(text='Time', units='s', unitPrefix=None, autoPrecision=True)
        axis.setTicks([[(x[i], str(datetime_objects[i])) for i in range(0, len(x), 10)]])
        # axis.setTicks([[(x[0], str(datetime_objects[0])), (x[len(x) - 1], str(datetime_objects[len(x) - 1]))]])
        
    def clear_graph(self) -> None:
        self.clear()
