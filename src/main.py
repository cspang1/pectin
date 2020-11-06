import sys
from PyQt5.QtWidgets import QApplication
from pectin import pectin

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = pectin()
    window.resize(800, 600)
    window.showMaximized()
    app.exec_()
