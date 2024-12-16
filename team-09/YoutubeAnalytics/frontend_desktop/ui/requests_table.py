from PyQt5.QtWidgets import QTableWidget, QAbstractItemView, \
    QAbstractScrollArea, QTableWidgetItem
from PyQt5.QtGui import QColor
from config import type_request_str


class RequestsTable(QTableWidget):
    def __init__(self) -> None:
        super().__init__(0, 3)

        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setSelectionMode(QAbstractItemView.NoSelection)
        self.setSizeAdjustPolicy(
            QAbstractScrollArea.AdjustToContents)

        self.setHorizontalHeaderLabels(["Тип", "Дата завершения", "Данные"])

    def fill(self, requests: list) -> None:
        self.clearContents()

        for row, request in enumerate(requests):
            if row == self.rowCount():
                self.insertRow(self.rowCount())

            type = QTableWidgetItem(type_request_str[request["type"]])
            date = QTableWidgetItem(request["date_completion"])
            data = QTableWidgetItem(str(request["data"]))
            
            color = QColor(225, 139, 139) if not request["date_completion"] else QColor(139, 225, 139)
            
            type.setBackground(color)
            date.setBackground(color)
            data.setBackground(color)
            
            self.setItem(row, 0, type)
            self.setItem(row, 1, date)
            self.setItem(row, 2, data)
            
        self.resizeColumnsToContents()
        self.setColumnWidth(2, 100)
