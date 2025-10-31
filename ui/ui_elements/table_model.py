from PyQt6.QtCore import QAbstractTableModel, Qt


class TableModel(QAbstractTableModel):
    def __init__(self, tData, headers):
        super().__init__()
        self.tData = tData
        self.headers = headers

    def rowCount(self, parent=None):
        return len(self.tData)

    def columnCount(self,parent=None):
        return len(self.headers)

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return None

        if role == Qt.ItemDataRole.DisplayRole:
            return str(self.tData[index.row()][index.column()])

        return None

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if role != Qt.ItemDataRole.DisplayRole:
            return None

        if orientation == Qt.Orientation.Horizontal:
            return self.headers[section]

        if orientation == Qt.Orientation.Vertical:
            return str(section+1)

        return None

    def update_data(self, newData):
        self.beginResetModel()
        self.tData = newData
        self.endResetModel()