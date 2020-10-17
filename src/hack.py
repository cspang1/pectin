from PyQt5.QtWidgets import (
    QWidget,
    QPushButton,
    QHBoxLayout,
    QVBoxLayout,
    QTimeEdit,
    QSpinBox,
    QLabel,
    QSizePolicy,
    QFrame,
    QAbstractSpinBox,
    QLCDNumber,
    QMessageBox,
    QDateEdit
)
from PyQt5.QtCore import (
    pyqtSlot,
    pyqtSignal,
    QDateTime,
    QTimer,
    QDate,
    QTime,
    Qt
)


class zulu(QWidget):

    class milSpinBox(QSpinBox):
        def __init__(self, *args):
            QSpinBox.__init__(self, *args)

        def textFromValue(self, value):
            return "%02d" % value

    class timer(QLCDNumber):

        def __init__(self, parent):
            super().__init__(8, parent)
            self.showTime()

        def showTime(self):
            time = QTime.currentTime().toString("HH:mm:ss")
            self.display(time)

    class inputs(QWidget):

        def __init__(self, parent):
            super().__init__(parent)
            self.hr_in = zulu.milSpinBox()
            self.hr_in.setButtonSymbols(QAbstractSpinBox.NoButtons)
            self.hr_in.setRange(0, 23)
            self.min_in = zulu.milSpinBox()
            self.min_in.setButtonSymbols(QAbstractSpinBox.NoButtons)
            self.min_in.setRange(0, 59)
            self.sec_in = zulu.milSpinBox()
            self.sec_in.setButtonSymbols(QAbstractSpinBox.NoButtons)
            self.sec_in.setRange(0, 59)
            hr_lbl = QLabel("HH")
            min_lbl = QLabel("mm")
            sec_lbl = QLabel("ss")
            zulu_lbl = QLabel("ZULU")
            timer_layout = QHBoxLayout()
            timer_layout.addWidget(self.hr_in)
            timer_layout.addWidget(hr_lbl)
            timer_layout.addWidget(self.min_in)
            timer_layout.addWidget(min_lbl)
            timer_layout.addWidget(self.sec_in)
            timer_layout.addWidget(sec_lbl)
            timer_layout.addWidget(zulu_lbl)
            timer_layout.setContentsMargins(0, 0, 0, 0)
            self.setLayout(timer_layout)

    def __init__(self, parent):
        super().__init__(parent)
        self.zulu_layout = QHBoxLayout()
        self.zulu_inputs = self.inputs(self)
        self.zulu_timer = self.timer(self)
        self.zulu_timer.setFixedSize(150, 50)
        self.zulu_layout.addWidget(self.zulu_inputs)
        self.zulu_layout.addWidget(self.zulu_timer)
        self.zulu_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.zulu_layout)
        self.zulu_timer.setVisible(False)

    @pyqtSlot(bool)
    def showTimer(self, hacked):
        self.zulu_inputs.setVisible(not hacked)
        self.zulu_timer.setVisible(hacked)

        if hacked:
            self.hr = self.zulu_inputs.hr_in.value()
            self.min = self.zulu_inputs.min_in.value()
            self.sec = self.zulu_inputs.sec_in.value()


class hack(QFrame):
    hacked = pyqtSignal(bool)

    def __init__(self, parent):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.setFrameShape(QFrame.StyledPanel)
        self.main_layout = QVBoxLayout()
        self.hack_layout = QHBoxLayout()
        self.date_layout = QHBoxLayout()
        self.hack_time_in = QTimeEdit()
        self.hack_time_in.setDisplayFormat("HH:mm:ss")
        self.time_set = zulu(self)
        self.hacked.connect(self.time_set.showTimer)
        self.date = QDateEdit(QDate.currentDate())
        self.date.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
        self.date.setCalendarPopup(True)
        self.date_layout.addWidget(QLabel("Mission Date:"))
        self.date_layout.setAlignment(Qt.AlignHCenter)
        self.date_layout.addWidget(self.date)
        self.main_layout.addLayout(self.date_layout)
        self.main_layout.addLayout(self.hack_layout)
        self.setLayout(self.main_layout)
        self.hack_button = QPushButton("Hack!")
        self.reset_button = QPushButton("Reset")
        self.reset_button.setEnabled(False)
        self.hack_button.setStyleSheet("background-color: red; color: white;")
        self.hack_layout.addWidget(self.reset_button)
        self.hack_layout.addWidget(self.hack_button)
        self.hack_layout.addWidget(self.time_set)
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
        self.hacked.emit(True)

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
        self.hacked.emit(False)
