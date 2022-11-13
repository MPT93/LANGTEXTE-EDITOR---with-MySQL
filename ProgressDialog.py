from PyQt5.QtWidgets import QApplication,  QProgressDialog
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt


class ProgressDialog():
    def __init__(self, size, window_title, label_text,  cancel_button_text=None):

        self.size = size
        self.progressDialog = QProgressDialog(
            label_text, cancel_button_text, 0, self.size)

        # self.progressDialog.setCancelButton(None)
        self.progressDialog.setWindowFlags(Qt.WindowCloseButtonHint)
        self.progressDialog.setWindowTitle(window_title)
        self.progressDialog.setWindowIcon(QIcon('kuka.png'))
        self.progressDialog.setWindowModality(Qt.ApplicationModal)
        self.progressDialog.setMinimumHeight(100)
        self.progressDialog.setMinimumWidth(500)
        self.progressDialog.setAutoClose(True)

        self.progressDialog.show()

    def set_value(self, value):
        self.progressDialog.setValue(value)
        QApplication.processEvents()
