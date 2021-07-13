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
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
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

    def paintEvent(self, event):
        painter = QPainter(self)
        super().paintEvent(event)
        painter.setRenderHint(QPainter.Antialiasing)
        pen = QPen(Qt.red)
        pen.setWidth(5)
        painter.setPen(pen)
        painter.drawLine(0, 10, self.parent().width() * 3, 10)
        painter.drawLine(0, 59, self.parent().width() * 3, 59)
        painter.end()


class AngleButton(QPushButton):
    pressed = pyqtSignal(int)

    def __init__(self, value, parent=None):
        super().__init__(str(value), parent)
        self.setFont(QFont("Consolas", 16, 3))
        self.setFixedSize(100, 50)
        self.index = value
        self.clicked.connect(lambda: self.pressed.emit(self.index))

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
                    background-color: none
                }
            """)


class AngleSet(QWidget):
    acted = pyqtSignal(int, BtnSource)

    def __init__(self, source, parent=None):
        super().__init__(parent)
        self.source = source
        self.active = 0
        self.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
        self.layout = QVBoxLayout()
        self.layout.setSpacing(0)
        limit = 4 if self.source is BtnSource.HUNDREDS else 10
        for digit in range(limit):
            tmp_btn = AngleButton(digit)
            tmp_btn.pressed.connect(self.switch_active)
            self.layout.addWidget(tmp_btn)
        # self.layout.setAlignment(Qt.AlignTop)
        # self.layout.addStretch()
        self.setLayout(self.layout)

    @pyqtSlot(int)
    def switch_active(self, target=None):
        if target is None:
            target = -1
            for index in range(self.layout.count()):
                self.layout.itemAt(index).widget().activate(False)
        for index in range(self.layout.count()):
            cur = self.layout.itemAt(index).widget()
            if cur.index == self.active:
                cur.activate(False)
            if cur.index == target:
                cur.activate(True)
        self.active = target
        if target != -1:
            self.acted.emit(self.active, self.source)


class AngleContainer(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.hundreds = AngleSet(BtnSource.HUNDREDS)
        self.tens = AngleSet(BtnSource.TENS)
        self.ones = AngleSet(BtnSource.ONES)
        for set in [self.hundreds, self.tens, self.ones]:
            set.acted.connect(self.digit_pressed)
        layout = QHBoxLayout()
        layout.addWidget(self.hundreds)
        layout.addWidget(self.tens)
        layout.addWidget(self.ones)
        layout.setAlignment(self.hundreds, Qt.AlignTop)
        self.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)
        overlay = Overlay(self)
        overlay.setGeometry(self.geometry())

    @pyqtSlot(int, BtnSource)
    def digit_pressed(self, value, source):
        if source is BtnSource.HUNDREDS:
            pass
        if source is BtnSource.TENS:
            pass
        if source is BtnSource.ONES:
            pass


class ExactAngle(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.angle_container = AngleContainer()
        layout = QHBoxLayout()
        layout.addStretch()
        layout.addWidget(self.angle_container)
        layout.addStretch()
        self.setLayout(layout)

    @pyqtSlot(int)
    def set_dark_mode(self, enable):
        labels = self.findChildren(QLabel)
        for label in labels:
            if enable:
                label.setStyleSheet("color: white")
            else:
                label.setStyleSheet("color: none")
