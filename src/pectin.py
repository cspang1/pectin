from PyQt5.QtWidgets import (
    QWidget,
    QMainWindow,
    QSplitter,
    QPushButton,
    QHBoxLayout,
    QTextEdit
)
from PyQt5.QtCore import (
    Qt
)


class pectin(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setupWindow()

    def setupWindow(self):
        self.setWindowTitle("Pectin")
        main_split = QSplitter(Qt.Vertical)

        intfc_area = QWidget()
        log_area = QTextEdit()
        test_btn_1 = QPushButton("ABC")
        test_btn_2 = QPushButton("DEF")
        btn_layout = QHBoxLayout()
        btn_layout.addWidget(test_btn_1)
        btn_layout.addWidget(test_btn_2)
        intfc_area.setLayout(btn_layout)
        main_split.addWidget(intfc_area)
        main_split.addWidget(log_area)

        self.setCentralWidget(main_split)
