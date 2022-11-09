from TableModel import TableModel
from PyQt5.QtWidgets import QMainWindow, QStatusBar, QTableView, QAction, QMessageBox, QDesktopWidget, QFileDialog
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QUrl
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

        OpenButton = QAction("&Open", self)
        OpenButton.setShortcut('Ctrl+O')
        OpenButton.setStatusTip('Open an existing file.')
        OpenButton.triggered.connect(self.open_existing_file)
        FileMenu.addAction(OpenButton)

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
        message_text = "Do you want to save the actual file before creating a new one?"
        Reply = self.show_question_message_box(message_text)

        if Reply == QMessageBox.Yes:
            self.save_current_file()

        if Reply == QMessageBox.Yes or Reply == QMessageBox.No:
            self.signals_and_descriptions = self.define_all_signals_without_descriptions()

            self.refresh_table_view()

            self.actual_file_name = "unnamed.csv"
            self.setWindowTitle(self.title + self.actual_file_name)
            self.StatusField.showMessage("New file was created.")

    def get_signals_list_as_dictionary(self):
        return {
            signal: description
            for signal, description in self.signals_and_descriptions
        }

    def show_critical_message_box(self, message_text="Not the right data format!", window_title="Error", button=QMessageBox.Cancel):
        Reply = QMessageBox.critical(self, window_title, message_text, button)
        return Reply

    def open_existing_file(self):

        message_text = "Do you want to save the actual file before opening a new one?"
        Reply = self.show_question_message_box(message_text)

        if Reply == QMessageBox.Yes:
            self.save_current_file()

        self.file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open existing file",
            "",
            "*.csv"
        )

        if self.file_path:

            Reply = QMessageBox.Ok

            with open(self.file_path, 'r',  encoding="utf-8-sig") as file:
                opened_file_reader = csv.reader(file, delimiter=";")

                try:
                    self.signals_and_descriptions = self.define_all_signals_without_descriptions()

                    signals_and_descriptions_dict = self.get_signals_list_as_dictionary()

                    for signal, description in opened_file_reader:
                        if signal in signals_and_descriptions_dict:
                            signals_and_descriptions_dict[signal] = description
                        else:
                            Reply = self.show_critical_message_box()
                            break

                    if Reply == QMessageBox.Ok:
                        self.signals_and_descriptions = [
                            [signal, signals_and_descriptions_dict[signal]]
                            for signal in signals_and_descriptions_dict
                        ]

                        self.actual_file_name = QUrl.fromLocalFile(
                            self.file_path).fileName()
                        self.setWindowTitle(self.title + self.actual_file_name)

                except ValueError:

                    Reply = self.show_critical_message_box()

                if Reply == QMessageBox.Ok:
                    self.refresh_table_view()
                    message = "Existing file called {} was opened."
                    self.StatusField.showMessage(
                        message.format(self.actual_file_name)
                    )

    def save_current_file(self):
        pass
