from PyQt5.QtWidgets import (
    QWidget,
    QMainWindow,
    QSplitter,
    QPushButton,
    QHBoxLayout,
    QVBoxLayout,
    QTimeEdit,
    QTextEdit,
    QMessageBox
)
from PyQt5.QtCore import (
    pyqtSlot,
    QDateTime,
    QTimer,
    Qt
)


class pectin(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setupWindow()

    def setupWindow(self):
        self.setWindowTitle("Pectin")
        central_widget = QWidget()
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)
        hack_widget = hack()
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


class hack(QWidget):

    def __init__(self):
        super().__init__()
        self.main_layout = QHBoxLayout()
        self.hack_time_in = QTimeEdit()
        self.hack_time_in.setDisplayFormat("HH:mm:ss")
        self.main_layout.addWidget(self.hack_time_in)
        self.setLayout(self.main_layout)
        self.hack_button = QPushButton("Hack!")
        self.reset_button = QPushButton("Reset")
        self.reset_button.setEnabled(False)
        self.hack_button.setStyleSheet("background-color: red; color: white;")
        self.main_layout.addWidget(self.hack_button)
        self.main_layout.addWidget(self.reset_button)
        self.hack_button.clicked.connect(self.hackTime)
        self.reset_button.clicked.connect(self.resetTime)
        self.hack_timer = QTimer()
        self.hack_timer.setTimerType(Qt.VeryCoarseTimer)
        self.hack_timer.setInterval(1000)
        self.hack_timer.timeout.connect(self.incTime)

    @pyqtSlot()
    def hackTime(self):
        sys_time = QDateTime.currentDateTime().toUTC().time()
        self.hack_time = self.hack_time_in.time()
        self.time_diff = sys_time.secsTo(self.hack_time)
        self.hack_time_in.setReadOnly(True)
        self.hack_timer.start()
        self.hack_button.setStyleSheet(
            "background-color: green; color: white;"
        )
        self.hack_button.setText("Hacked!")
        self.hack_button.setEnabled(False)
        self.reset_button.setEnabled(True)

    @pyqtSlot()
    def incTime(self):
        self.hack_time = self.hack_time.addSecs(1)
        self.hack_time_in.setTime(self.hack_time)

    def resetTime(self):
        verify = QMessageBox(
            QMessageBox.Critical,
            "Reset time hack?",
            "Are you sure you want to reset the time hack? Any active logging will need to be re-hacked!",
            QMessageBox.Yes | QMessageBox.No
        )
        reset = verify.exec()
        if reset != QMessageBox.Yes:
            return

        self.hack_timer.stop()
        self.hack_button.setStyleSheet("background-color: red; color: white;")
        self.hack_button.setText("Hack!")
        self.hack_time_in.setReadOnly(False)
        self.hack_button.setEnabled(True)
        self.reset_button.setEnabled(False)
