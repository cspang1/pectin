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
from missionSetup import missionSetup
import json


class pectin(QMainWindow):

    def __init__(self):
        super().__init__()
        # msn_setup_diag = missionSetup(self)
        # if msn_setup_diag.exec():
        #     config = msn_setup_diag.get_config()

        # DEBUG
        config = json.loads("{\"date\": \"PyQt5.QtCore.QDate(1993, 3, 22)\", \"dl\": \"420\", \"mnemonic\": \"XXA\", \"systems\": [\"QQA\", \"QQB\", \"BQS\", \"ZZT\", \"LOL\", \"WTF\"], \"events\": [\"Checked in\", \"Checked out\", \"Saw activity\", \"Did its job\", \"Made everyone proud\", \"Broke something\", \"Saw a bird\", \"Saw a plane\", \"Got blocked\", \"Made a fast escape\"], \"applets\": [\"direction\"]}")
        # DEBUG

        self.setupWindow()

    def setupWindow(self):
        self.setWindowTitle("Pectin")
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
