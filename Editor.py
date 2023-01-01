from TableModel import TableModel
from ProgressDialog import ProgressDialog
from SignalDataBase import SignalDataBase
from ModifyDialogWindow import ModifyDialogWindow
from PlcDialogWindow import PlcDialogWindow
from PyQt5.QtWidgets import QMainWindow, QStatusBar, QTableView, QAction, QMessageBox, QDesktopWidget, QFileDialog
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QUrl, Qt
import csv
import sys
import os
import glob
import re
import openpyxl as xl


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
        OptionsMenu = MenuBar.addMenu("&Options")

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

        AddApplicationButton = QAction("&Add application", self)
        AddApplicationButton.setStatusTip(
            'Add signals description of chosen application')
        AddApplicationButton.triggered.connect(
            self.add_application_signals_descriptions)
        OptionsMenu.addAction(AddApplicationButton)

        RemoveApplicationButton = QAction("&Remove application", self)
        RemoveApplicationButton.setStatusTip(
            'Remove signals description of chosen application')
        RemoveApplicationButton.triggered.connect(
            self.remove_application_signals_descriptions)
        OptionsMenu.addAction(RemoveApplicationButton)

        AddMarkersFromSrcFile = QAction("&Add markers from .src file", self)
        AddMarkersFromSrcFile.setStatusTip(
            'Add markers and descriptions from .src file')
        AddMarkersFromSrcFile.triggered.connect(
            self.add_markers_from_src_file)
        OptionsMenu.addAction(AddMarkersFromSrcFile)

        AddFlagsFromSrcFile = QAction("&Add flags from .src file", self)
        AddFlagsFromSrcFile.setStatusTip(
            'Add flags and descriptions from .src file')
        AddFlagsFromSrcFile.triggered.connect(
            self.add_flags_from_src_file)
        OptionsMenu.addAction(AddFlagsFromSrcFile)

        AddSignalsFromElectricPlan = QAction(
            "&Add signals from .asc file", self)
        AddSignalsFromElectricPlan.setStatusTip(
            'Add signals and descriptions from .asc Eplan file')
        AddSignalsFromElectricPlan.triggered.connect(
            self.add_signals_from_asc_file)
        OptionsMenu.addAction(AddSignalsFromElectricPlan)

        AddPlcSignals = QAction("&Add signals from .xlsm file", self)
        AddPlcSignals.setStatusTip(
            'Add plc signals and descriptions from .xlsm file')
        AddPlcSignals.triggered.connect(
            self.add_plc_signals_from_xlsm_file)
        OptionsMenu.addAction(AddPlcSignals)

        font = MenuBar.font()
        font.setPointSize(11)
        MenuBar.setFont(font)

        self.Table = QTableView()
        self.header_data = ['Signal', 'Description']
        self.Table.setFont(font)

        self.Model = TableModel(
            self.signals_and_descriptions, self.header_data)
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
        self.Model = TableModel(
            self.signals_and_descriptions, self.header_data)
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
            self.successful_selection_existing_database = False
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
                    table_name = file_name.replace(" ", "_")
                    table_name = table_name.replace(".de.csv", "")
                    table_name = table_name.replace("-", "_")
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

    def add_application_signals_descriptions(self):

        if self.successful_selection_existing_database and self.successful_database_connection:
            applications_table = self.SignalDataBase.get_tables_names()
            title = "Add application descriptions"
            message = "Select application to add:"

            AddModifyDialogWindow = ModifyDialogWindow(
                applications_table, title, message)

            if AddModifyDialogWindow.exec() and AddModifyDialogWindow.application_to_modify != "":

                signals_and_descriptions_to_add = {
                    signal: description
                    for signal, description in self.SignalDataBase.select_application(AddModifyDialogWindow.application_to_modify)}

                actual_signals_and_descriptions = self.get_signals_list_as_dictionary()

                for signal in signals_and_descriptions_to_add:
                    actual_signals_and_descriptions[signal] = signals_and_descriptions_to_add[signal]

                self.signals_and_descriptions = [
                    [signal, actual_signals_and_descriptions[signal]]
                    for signal in actual_signals_and_descriptions]

                self.refresh_table_view()

                message = "Descriptions of {} signals were added.".format(
                    AddModifyDialogWindow.application_to_modify)
                self.StatusField.showMessage(message)
        else:
            message_text = "The database of signals does not exist or can not establish a connection! Create a new database first!"
            self.show_information_message_box(message_text)

    def remove_application_signals_descriptions(self):

        if self.successful_selection_existing_database and self.successful_database_connection:
            applications_table = self.SignalDataBase.get_tables_names()
            title = "Remove application descriptions"
            message = "Select application to remove:"

            RemoveModifyDialogWindow = ModifyDialogWindow(
                applications_table, title, message)

            if RemoveModifyDialogWindow.exec() and RemoveModifyDialogWindow.application_to_modify != "":

                signals_and_descriptions_to_remove = {
                    signal: description
                    for signal, description in self.SignalDataBase.select_application(RemoveModifyDialogWindow.application_to_modify)}

                actual_signals_and_descriptions = self.get_signals_list_as_dictionary()

                for signal in signals_and_descriptions_to_remove:
                    actual_signals_and_descriptions[signal] = ""

                self.signals_and_descriptions = [
                    [signal, actual_signals_and_descriptions[signal]]
                    for signal in actual_signals_and_descriptions]

                self.refresh_table_view()

                message = "Descriptions of {} signals were removed.".format(
                    RemoveModifyDialogWindow.application_to_modify)
                self.StatusField.showMessage(message)
        else:

            message_text = "The database of signals does not exist or can not establish a connection! Create a new database first!"
            self.show_information_message_box(message_text)

    def add_markers_from_src_file(self):

        file_name, _ = QFileDialog.getOpenFileName(
            self, "Open src file", "", "*.src")

        if file_name:
            with open(file_name, "r") as file:

                try:

                    lines = file.readlines()
                    actual_signals_and_descriptions = self.get_signals_list_as_dictionary()

                    for line in lines:
                        marker_line = re.search(
                            "M[0-9]{1} = |M[0-9]{2} = |M[0-9]{3} =", line)

                        if marker_line:

                            marker = marker_line.group().split(" =")[0]

                            if int(marker.replace("M", "")) in range(0, 200):
                                index_comment_line = lines.index(line) - 2
                                comment_line = re.search(
                                    "--(.*?)--", lines[index_comment_line])

                                if comment_line:
                                    comment = comment_line.group(1)
                                    if marker in actual_signals_and_descriptions:
                                        actual_signals_and_descriptions[marker] = comment

                    self.signals_and_descriptions = [
                        [signal, actual_signals_and_descriptions[signal]]
                        for signal in actual_signals_and_descriptions]

                    self.refresh_table_view()

                    message = "Marker descriptions included in {} file were added."
                    message = message.format(file_name)
                    self.StatusField.showMessage(message)

                except AttributeError:
                    self.show_critical_message_box(button=QMessageBox.Ok)

    def add_flags_from_src_file(self):

        file_name, _ = QFileDialog.getOpenFileName(
            self, "Open src file", "", "*.src")

        if file_name:
            with open(file_name, "r") as file:

                try:

                    lines = file.readlines()
                    actual_signals_and_descriptions = self.get_signals_list_as_dictionary()

                    for line in lines:
                        flag_line = re.search("F9[0-5][0-9] =", line)

                        if flag_line:

                            flag = flag_line.group().strip(" =")
                            index_comment_line = lines.index(line)-2
                            comment_line = re.search(
                                "--(.*?)--", lines[index_comment_line])

                            if comment_line:
                                comment = comment_line.group(1)
                                if flag in actual_signals_and_descriptions:
                                    actual_signals_and_descriptions[flag] = comment

                    self.signals_and_descriptions = [
                        [signal, actual_signals_and_descriptions[signal]]
                        for signal in actual_signals_and_descriptions]

                    self.refresh_table_view()

                    message = "Flags descriptions included in {} file were added."
                    message = message.format(file_name)
                    self.StatusField.showMessage(message)

                except AttributeError:
                    self.show_critical_message_box(button=QMessageBox.Ok)

    def add_signals_from_asc_file(self):

        signals_changed = False
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Open asc file", "", "*.asc")

        if file_name:
            with open(file_name, "r") as file:

                actual_signals_and_descriptions = self.get_signals_list_as_dictionary()

                lines = file.readlines()

                try:

                    for line in lines:
                        splitted_line = line.split(',')
                        signal_name = splitted_line[1].replace('"', '')
                        signal_name = signal_name.replace(' ', '')
                        actual_signal_number = int(float(signal_name[1:]))
                        valve_name = splitted_line[0][10:- 1].replace(" ", "")

                        if (actual_signal_number > 576) & (actual_signal_number < 705):
                            if valve_name != "":
                                comment = splitted_line[6].replace('"', '')
                                if signal_name in actual_signals_and_descriptions:
                                    signal_description = valve_name + " " + comment
                                    actual_signals_and_descriptions[signal_name] = signal_description
                                    signals_changed = True

                except (IndexError, ValueError):
                    self.show_critical_message_box(button=QMessageBox.Ok)

            self.signals_and_descriptions = [[signal, actual_signals_and_descriptions[signal]]
                                             for signal in actual_signals_and_descriptions]

            if signals_changed:
                self.refresh_table_view()

                message = "Descriptions included in {} file were added."
                self.StatusField.showMessage(message.format(file_name))

    def add_plc_signals_from_xlsm_file(self):

        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select file", "", "*.xlsm")

        if file_path:
            workbook = xl.load_workbook(file_path)

            sheets_with_robot = []

            for sheet in workbook.sheetnames:
                if "R0" in sheet:
                    sheets_with_robot.append(sheet)

            title = "Add plc signals from .xlsm file"
            message = "Select sheet to add:"
            actual_signals_and_descriptions = self.get_signals_list_as_dictionary()

            PlcSignalsDialogWindow = PlcDialogWindow(
                sheets_with_robot, title, message, workbook, actual_signals_and_descriptions)

            if PlcSignalsDialogWindow.exec_() and PlcSignalsDialogWindow.sheet_to_add_name != "":

                actual_signals_and_descriptions = PlcSignalsDialogWindow.get_robot_collisions_signals()
                actual_signals_and_descriptions = PlcSignalsDialogWindow.get_robot_plc_signals()

                self.signals_and_descriptions = [
                    [signal, actual_signals_and_descriptions[signal]]
                    for signal in actual_signals_and_descriptions
                ]

                self.refresh_table_view()

                message = "Descriptions included in {} file were added."
                self.StatusField.showMessage(message.format(file_path))
