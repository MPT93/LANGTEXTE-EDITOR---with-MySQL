from TableModel import TableModel
from PyQt5.QtWidgets import QMainWindow, QStatusBar, QTableView, QDesktopWidget
from PyQt5.QtGui import QIcon
import csv


class Editor(QMainWindow):

    def __init__(self):
        super().__init__()

        self.signals_and_descriptions = self.define_all_signals_without_descriptions()

        self.interface()

    def interface(self):

        MenuBar = self.menuBar()

        font = MenuBar.font()
        font.setPointSize(11)
        MenuBar.setFont(font)

        self.Table = QTableView()
        self.headerdata = ['Signal', 'Description']
        self.Table.setFont(font)

        self.Model = TableModel(self.signals_and_descriptions, self.headerdata)
        self.Table.setModel(self.Model)
        self.Table.horizontalHeader().setStretchLastSection(True)
        self.setCentralWidget(self.Table)

        self.StatusField = QStatusBar()
        self.setStatusBar(self.StatusField)

        self.resize(1000, 700)
        self.center()

        self.setWindowIcon(QIcon('kuka.png'))
        self.actual_file_name = ".csv"
        self.title = "Langtexte Editor - "
        self.setWindowTitle(self.title + self.actual_file_name)

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def define_all_signals_without_descriptions(self):

        config_file_path = "config/config.csv"

        with open(config_file_path, "r", encoding="utf-8-sig") as file:
            fileReader = csv.reader(file, delimiter=";")
            return [[signal, ""] for signal, _ in fileReader]
