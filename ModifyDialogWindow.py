from PyQt5.QtWidgets import QDialog, QDialogButtonBox, QVBoxLayout, QLabel, QComboBox
from PyQt5.QtGui import QIcon


class ModifyDialogWindow(QDialog):
    def __init__(self, applications_table, title, Message):
        super().__init__()
        self.applications_table = applications_table
        self.application_to_modify = ""

        self.setWindowTitle(title)
        self.setWindowIcon(QIcon('kuka.png'))
        self.resize(400, 170)

        self.ButtonBox = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.ButtonBox.accepted.connect(self.accept)
        self.ButtonBox.rejected.connect(self.reject)

        self.MainLayout = QVBoxLayout()
        self.MainLayout.setSpacing(20)

        Message = QLabel(Message)
        font = Message.font()
        font.setPointSize(9)
        Message.setFont(font)
        self.MainLayout.addWidget(Message)

        self.ApplicationComboBox = QComboBox()
        font = self.ApplicationComboBox.font()
        font.setPointSize(9)
        self.ApplicationComboBox.setFont(font)

        self.ApplicationComboBox.addItems([""] + self.applications_table)
        self.ApplicationComboBox.currentIndexChanged[str].connect(
            self.get_application_name)
        self.MainLayout.addWidget(self.ApplicationComboBox)

        self.MainLayout.addWidget(self.ButtonBox)

        self.setLayout(self.MainLayout)

    def get_application_name(self, application_to_modify):
        self.application_to_modify = application_to_modify
