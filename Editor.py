from TableModel import TableModel
from ProgressDialog import ProgressDialog
from SignalDataBase import SignalDataBase
from PyQt5.QtWidgets import QMainWindow, QStatusBar, QTableView, QAction, QMessageBox, QDesktopWidget, QFileDialog
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QUrl, Qt
import csv
import sys
import os
import glob


class Editor(QMainWindow):

    def __init__(self):
        super().__init__()

        self.signals_and_descriptions = self.define_all_signals_without_descriptions()

        self.interface()

        self.SignalDataBase = SignalDataBase()
        self.successful_database_connection = self.SignalDataBase.connect_with_database()
        self.check_database_state()

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

        SaveButton = QAction("&Save", self)
        SaveButton.setShortcut('Ctrl+S')
        SaveButton.setStatusTip('Save actual file')
        SaveButton.triggered.connect(self.save_current_file)
        FileMenu.addAction(SaveButton)

        SaveAsButton = QAction("&Save As", self)
        SaveAsButton.setShortcut('Ctrl+Alt+S')
        SaveButton.setStatusTip('Save as actual file')
        SaveAsButton.triggered.connect(self.save_as_current_file)
        FileMenu.addAction(SaveAsButton)

        FileMenu.addSeparator()

        CreateDataBaseButton = QAction("&Create new database", self)
        CreateDataBaseButton.setStatusTip(
            'Create a new database from selected folder with given csv files')
        CreateDataBaseButton.triggered.connect(self.create_new_database)
        FileMenu.addAction(CreateDataBaseButton)

        FileMenu.addSeparator()

        ExitButton = QAction("&Exit", self)
        ExitButton.setShortcut('Alt+F4')
        ExitButton.setStatusTip('Close application')
        ExitButton.triggered.connect(self.close_editor)
        FileMenu.addAction(ExitButton)

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

        if self.actual_file_name == "unnamed.csv" or self.actual_file_name == ".csv":
            self.save_as_current_file()

        else:
            if not self.file_path:
                directory_name = os.path.dirname(sys.argv[0])
                self.file_path = directory_name + "/" + self.actual_file_name

            with open(self.file_path, "w", encoding="utf-8-sig", newline="") as file:
                writer = csv.writer(file, delimiter=";")
                writer.writerows(self.signals_and_descriptions)

                message = 'File was saved under: {}.'
                self.StatusField.showMessage(
                    message.format(str(self.file_path))
                )

    def save_as_current_file(self):

        self.file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save this file as...",
            "",
            "*.csv"
        )

        if self.file_path:

            with open(self.file_path, "w", encoding="utf-8-sig", newline="") as file:
                writer = csv.writer(file, delimiter=";")
                writer.writerows(self.signals_and_descriptions)

                self.actual_file_name = QUrl.fromLocalFile(
                    self.file_path).fileName()
                self.setWindowTitle(self.title + self.actual_file_name)

                message = 'File was saved as {} under: {}.'
                self.StatusField.showMessage(
                    message.format(self.actual_file_name, str(self.file_path))
                )

    def close_editor(self):

        self.close()

    def closeEvent(self, event):

        message_text = "Do you want to close editor?"
        buttons = QMessageBox.Yes | QMessageBox.No
        Reply = self.show_question_message_box(
            message_text,
            buttons=buttons
        )

        if Reply == QMessageBox.Yes:
            message_text = "Do you want to save actual file before closing?"
            Reply = self.show_question_message_box(
                message_text,
                buttons=buttons
            )

            if Reply == QMessageBox.Yes:
                self.save_current_file()

            event.accept()
        else:
            event.ignore()

    def keyPressEvent(self, event):

        if event.key() == Qt.Key_Escape:
            self.close_editor()

    def check_database_state(self):

        button = QMessageBox.Ok

        if not self.successful_database_connection:
            message_text = "Can not connect to the ({}) database! Check user, password and root data in credentials.py file!".format(
                self.SignalDataBase.database_name)
            self.show_critical_message_box(
                message_text=message_text,
                button=button)
        else:
            self.successful_selection_existing_database = self.SignalDataBase.try_to_select_existing_database()

            if not self.successful_selection_existing_database:
                message_text = "Database ({}) does not exist! Please create a new database!".format(
                    self.SignalDataBase.database_name)

                self.show_critical_message_box(
                    message_text=message_text,
                    button=button)
                self.create_new_database()

    def show_information_message_box(self, message_text, window_title="Information", button=QMessageBox.Ok):

        QMessageBox.information(self, window_title, message_text, button)

    def create_new_database(self):

        caption = "Select folder with original long texts."
        base_path = QFileDialog.getExistingDirectory(caption=caption)
        self.successful_table_creation = False

        if base_path:
            recursive_path = os.path.join(
                base_path, "**/*.csv").replace("\\", "/")

            paths_of_all_csv_files = (path.replace("\\", "/")
                                      for path in glob.iglob(recursive_path, recursive=True))

            amount_of_csv_files = self.SignalDataBase.get_amount_of_csv_files_good_to_create_database(
                base_path+"/")

            if amount_of_csv_files != 0:
                label_text = 'Creating a new database in progress. Please wait.'
                window_title = "Create a new database."
                size = amount_of_csv_files
                self.progressDialog = ProgressDialog(
                    size,
                    window_title,
                    label_text)

                progress_value = 0
                self.progressDialog.set_value(progress_value)

                self.SignalDataBase.create_empty_database()

                for path in paths_of_all_csv_files:
                    file_name = path.split("/")[-1]
                    table_name = file_name.replace(
                        " ", "_").replace(".de.csv", "")
                    self.successful_table_creation = self.SignalDataBase.create_and_fill_table(
                        path, table_name)

                    progress_value += 1
                    self.progressDialog.set_value(progress_value)

                    if not self.successful_table_creation:
                        message_text = "The CSV file does not meet any requirements! Please check the content of {} file and create database again."
                        message_text = message_text.format(path.split("/")[-1])
                        button = QMessageBox.Ok
                        self.show_critical_message_box(
                            message_text=message_text, button=button)
                        break

                self.successful_selection_existing_database = self.SignalDataBase.try_to_select_existing_database()

                if self.successful_table_creation and self.successful_selection_existing_database:
                    message_text = "Database ({}) creation was successful!".format(
                        self.SignalDataBase.database_name)
                    self.show_information_message_box(message_text)
                    self.StatusField.showMessage(message_text)

                else:
                    self.SignalDataBase.drop_database()
                    message_text = "Database was not created!"
                    self.show_information_message_box(message_text)
            else:
                message_text = "Selected path {} does not contain any csv files.".format(
                    base_path)
                self.show_information_message_box(message_text)
