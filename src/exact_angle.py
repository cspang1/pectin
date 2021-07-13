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


class AngleContainer(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.hundreds = AngleSet()
        self.tens = AngleSet()
        self.ones = AngleSet()
        layout = QHBoxLayout()
        layout.addWidget(self.hundreds)
        layout.addWidget(self.tens)
        layout.addWidget(self.ones)
        self.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)
        overlay = Overlay(self)
        overlay.setGeometry(self.geometry())


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
    acted = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.active = 0
        self.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
        self.layout = QVBoxLayout()
        self.layout.setSpacing(0)
        for digit in range(10):
            tmp_btn = AngleButton(digit)
            tmp_btn.pressed.connect(self.switch_active)
            self.layout.addWidget(tmp_btn)
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
            self.acted.emit(self.active)


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
