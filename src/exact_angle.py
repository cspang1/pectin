from PyQt5.QtGui import (
    QFont,
    QPainter,
    QPen
)
from PyQt5.QtCore import (
    Qt,
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


class AngleSet(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
        layout = QVBoxLayout()
        layout.setSpacing(0)
        for digit in range(10):
            tmp_btn = QPushButton(str(digit))
            tmp_btn.setFixedSize(100, 50)
            tmp_btn.setFont(QFont('Consolas', 16))
            tmp_btn.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
            layout.addWidget(tmp_btn)
        self.setLayout(layout)


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
