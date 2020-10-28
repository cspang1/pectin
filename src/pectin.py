from PyQt5.QtWidgets import (
    QWidget,
    QMainWindow,
    QSplitter,
    QPushButton,
    QHBoxLayout,
    QVBoxLayout,
    QTextEdit,
)
from PyQt5.QtCore import (
    Qt
)
from hack import hack
from missionSetup import missionSetup


class pectin(QMainWindow):

    def __init__(self):
        super().__init__()
        msn_setup_diag = missionSetup(self)
        msn_setup_diag.show()
        # self.setupWindow()

    def setupWindow(self):
        self.setWindowTitle("Pectin")
        central_widget = QWidget()
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)
        hack_widget = hack(self)
        main_layout.addWidget(hack_widget)

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

        main_layout.addWidget(main_split)
        self.setCentralWidget(central_widget)
