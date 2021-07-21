from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from pectin import pectin
import sys

if __name__ == "__main__":
    if hasattr(Qt, 'AA_EnableHighDpiScaling'):
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    app = QApplication(sys.argv)
    window = pectin()
    window.resize(1920, 1080)
    window.showMaximized()
    app.exec_()
