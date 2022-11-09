from TableModel import TableModel
from PyQt5.QtWidgets import QMainWindow, QStatusBar, QTableView, QAction, QMessageBox, QDesktopWidget
from PyQt5.QtGui import QIcon
import csv


class Editor(QMainWindow):

    def __init__(self):
        super().__init__()

        self.signals_and_descriptions = self.define_all_signals_without_descriptions()
        self.interface()

    def interface(self):
        MenuBar = self.menuBar()

        FileMenu = MenuBar.addMenu("&File")

        self.NewButton = QAction("&New", self)
        self.NewButton.setShortcut('Ctrl+N')
        self.NewButton.setStatusTip('Create an empty file.')
        self.NewButton.triggered.connect(self.create_new_file)
        FileMenu.addAction(self.NewButton)

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

    def refresh_table_view(self):
        self.Model = TableModel(self.signals_and_descriptions, self.headerdata)
        self.Table.setModel(self.Model)

    def show_question_message_box(self, message_text, window_title="Question", buttons=QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel):
        Reply = QMessageBox.question(self, window_title, message_text, buttons)
        return Reply

    def create_new_file(self):
        question_text = "Do you want to save the actual file before creating a new one?"
        Reply = self.show_question_message_box(question_text)

        if Reply == QMessageBox.Yes:
            self.save_current_file()

        if Reply == QMessageBox.Yes or Reply == QMessageBox.No:
            self.signals_and_descriptions = self.define_all_signals_without_descriptions()

            self.refresh_table_view()

            self.actual_file_name = "unnamed.csv"
            self.setWindowTitle(self.title + self.actual_file_name)
            self.StatusField.showMessage("New file was created.")

    def save_current_file(self):
        pass
