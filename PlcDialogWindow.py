from PyQt5.QtWidgets import QDialog, QDialogButtonBox, QVBoxLayout, QLabel, QComboBox
from PyQt5.QtGui import QIcon


class PlcDialogWindow(QDialog):
    def __init__(self, sheets_with_robot, title, message, workbook, signals_with_descriptions):
        super().__init__()
        self.sheets_with_robot = sheets_with_robot
        self.workbook = workbook
        self.sheet_to_add_name = ""
        self.signals_with_descriptions = signals_with_descriptions

        self.setWindowTitle(title)
        self.setWindowIcon(QIcon('kuka.png'))
        self.resize(400, 170)

        DialogButton = QDialogButtonBox.Ok | QDialogButtonBox.Cancel

        self.ButtonBox = QDialogButtonBox(DialogButton)
        self.ButtonBox.accepted.connect(self.accept)
        self.ButtonBox.rejected.connect(self.reject)

        self.MainLayout = QVBoxLayout()
        self.MainLayout.setSpacing(20)

        Message = QLabel(message)
        font = Message.font()
        font.setPointSize(9)
        Message.setFont(font)
        self.MainLayout.addWidget(Message)

        self.SheetsComboBox = QComboBox()
        font = self.SheetsComboBox.font()
        font.setPointSize(9)
        self.SheetsComboBox.setFont(font)

        self.SheetsComboBox.addItems([""] + self.sheets_with_robot)

        self.SheetsComboBox.currentIndexChanged[str].connect(
            self.get_sheet_to_add)
        self.MainLayout.addWidget(self.SheetsComboBox)

        self.MainLayout.addWidget(self.ButtonBox)

        self.setLayout(self.MainLayout)

    def get_sheet_to_add(self, sheet_to_add_name):
        self.sheet_to_add_name = sheet_to_add_name

    def get_robot_plc_signals(self):

        sheet = self.workbook[self.sheet_to_add_name]

        start_plc_signals_row = 7
        end_plc_signals_row = 31

        signal_number_column = 11

        start_outputs_column = 12
        end_outputs_column = 15
        start_inputs_colum = 16
        end_inputs_column = 19

        for row in range(start_plc_signals_row, end_plc_signals_row):

            signal_number = sheet.cell(row, signal_number_column).value
            output_signal_description = ""
            input_signal_description = ""

            for column in range(start_outputs_column, end_outputs_column + 1):

                actual_cell_value = sheet.cell(row, column).value

                if actual_cell_value:
                    output_signal_description += str(actual_cell_value) + " "
                else:
                    break

            for column in range(start_inputs_colum, end_inputs_column + 1):

                actual_cell_value = sheet.cell(row, column).value

                if actual_cell_value:
                    input_signal_description += str(actual_cell_value) + " "
                else:
                    break

            if(output_signal_description != ""):

                signal = 'A'+str(signal_number)
                self.signals_with_descriptions[signal] = output_signal_description

            if(input_signal_description != ""):

                signal = 'E'+str(signal_number)

                self.signals_with_descriptions[signal] = input_signal_description

        return self.signals_with_descriptions

    def get_robot_collisions_signals(self):

        sheet = self.workbook[self.sheet_to_add_name]

        start_collisions_signals_row = 7
        end_collisions_signals_row = 22

        signal_column_number = 22

        start_collisions_signals_column = 23
        end_collisions_signals_column = 38

        for column in range(start_collisions_signals_column, end_collisions_signals_column + 1):
            robot_name = sheet.cell(
                start_collisions_signals_row-1, column).value
            if robot_name:
                for row in range(start_collisions_signals_row, end_collisions_signals_row + 1):
                    if sheet.cell(row, column).value == "X":
                        collision_signal = sheet.cell(
                            row, signal_column_number).value

                        self.signals_with_descriptions.update(
                            {
                                f'E{collision_signal}': f"Roboterfreigabe {int(collision_signal)-40} Rob < {robot_name}",
                                f'E{int(collision_signal)+40}': f"Quitt. Verriegelung {int(collision_signal)-40} Rob > {robot_name}",
                                f'A{int(collision_signal)+40}': f"Anford. Verriegelung {int(collision_signal)-40} Rob > {robot_name}",
                                f'A{collision_signal}': f"Roboterverriegelung {int(collision_signal)-40} Rob > {robot_name}",

                            }
                        )

        return self.signals_with_descriptions
