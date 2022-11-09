from PyQt5.QtCore import QAbstractTableModel, Qt, QVariant


class TableModel(QAbstractTableModel):
    def __init__(self, input_data, headerdata):
        super().__init__()
        self.input_data = input_data
        self.headerdata = headerdata

    def data(self, index, role):

        if role == Qt.DisplayRole or role == Qt.EditRole:
            return self.input_data[index.row()][index.column()]

    def rowCount(self, index):
        return len(self.input_data)

    def columnCount(self, index):
        return len(self.input_data[0])

    def flags(self, index):
        if index.column() == 1:
            return Qt.ItemIsEditable | Qt.ItemIsEnabled | Qt.ItemIsSelectable
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable

    def setData(self, index, value, role=Qt.EditRole):
        if index.isValid():
            if role == Qt.EditRole:
                row = index.row()
                column = index.column()
                if row > len(self.input_data) or column > len(self.input_data[row]):
                    return False
                else:
                    self.input_data[row][column] = value
                    return True
        return False

    def headerData(self, column, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return QVariant(self.headerdata[column])
        return QVariant()
