import sys
from PyQt5.QtWidgets import QApplication
from Editor import Editor


def main():

    app = QApplication(sys.argv)

    mainWindow = Editor()
    mainWindow.show()

    app.exec()


if __name__ == '__main__':
    main()
