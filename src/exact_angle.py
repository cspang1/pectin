from PyQt5.QtGui import (
    QFont,
    QPainter,
    QPen
)
from PyQt5.QtCore import (
    Qt,
    pyqtSignal,
    pyqtSlot
)
from PyQt5.QtWidgets import (
    QLabel,
    QPushButton,
    QSizePolicy,
    QWidget
)
from enum import (
    IntEnum,
    unique
)


@unique
class BtnSource(IntEnum):
    HUNDREDS = 0
    TENS = 1
    ONES = 2


class Overlay(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_NoSystemBackground)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.raise_()

    def paintEvent(self, event):
        painter = QPainter(self)
        super().paintEvent(event)
        painter.setRenderHint(QPainter.Antialiasing)
        pen = QPen(Qt.red)
        pen.setWidth(5)
        painter.setPen(pen)
        painter.drawLine(0, 490, 340, 490)
        painter.drawLine(0, 540, 340, 540)
        painter.end()


class AngleButton(QPushButton):
    pressed = pyqtSignal(int)

    def __init__(self, value, parent=None):
        super().__init__(str(value), parent)
        self.setFont(QFont("Consolas", 16, 3))
        self.setFixedSize(100, 50)
        self.index = value
        self.clicked.connect(lambda: self.pressed.emit(self.index))
        self.setStyleSheet("""
            AngleButton {background-color: none}
            AngleButton:pressed {
                background-color: cyan
            }
        """)

    def activate(self, active):
        if active:
            self.setStyleSheet("""
                AngleButton {background-color: lime}
                AngleButton:pressed {
                    background-color: cyan
                }
            """)
        else:
            self.setStyleSheet("""
                AngleButton {background-color: none}
                AngleButton:pressed {
                    background-color: cyan
                }
            """)


class AngleSet(QWidget):
    acted = pyqtSignal(int, BtnSource)

    def __init__(self, source, parent=None):
        super().__init__(parent)
        self.source = source
        self.active = 0
        self.setFixedSize(100, 1000)
        limit = 4 if self.source is BtnSource.HUNDREDS else 10
        y_offset = 490
        self.digits = []
        for digit in range(limit):
            tmp_btn = AngleButton(digit, self)
            tmp_btn.move(0, y_offset)
            y_offset = y_offset + 50
            tmp_btn.pressed.connect(self.switch_active)
            self.digits.append(tmp_btn)

    @pyqtSlot(int)
    def switch_active(self, target=None):
        if target is None:
            target = -1
            for index in range(len(self.digits)):
                self.digits[index].activate(False)
        for index in range(len(self.digits)):
            cur = self.digits[index]
            if cur.index == self.active:
                cur.activate(False)
            if cur.index == target:
                cur.activate(True)
        self.active = target
        if target != -1:
            self.acted.emit(self.active, self.source)


class ExactAngle(QWidget):
    angle_event = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(450, 1000)
        self.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
        self.hundreds = AngleSet(BtnSource.HUNDREDS, self)
        self.tens = AngleSet(BtnSource.TENS, self)
        self.ones = AngleSet(BtnSource.ONES, self)
        self.hundreds.move(10, 0)
        self.tens.move(120, 0)
        self.ones.move(230, 0)
        for set in [self.hundreds, self.tens, self.ones]:
            set.acted.connect(self.digit_pressed)
        overlay = Overlay(self)
        overlay.setGeometry(self.geometry())
        deg_sym = QLabel("°", self)
        deg_sym.setFont(QFont("Consolas", 32, 3))
        deg_sym.move(350, 470)

    @pyqtSlot(int, BtnSource)
    def digit_pressed(self, value, source):
        if source is BtnSource.HUNDREDS:
            pass
        if source is BtnSource.TENS:
            pass
        if source is BtnSource.ONES:
            pass

    @pyqtSlot(int)
    def set_dark_mode(self, enable):
        labels = self.findChildren(QLabel)
        for label in labels:
            if enable:
                label.setStyleSheet("color: white")
            else:
                label.setStyleSheet("color: none")
