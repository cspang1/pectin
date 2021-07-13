from PyQt5.QtCore import (
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


class AngleSet(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
        layout = QVBoxLayout()
        for digit in range(10):
            tmp_btn = QPushButton(str(digit))
            tmp_btn.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
            layout.addWidget(tmp_btn)
        self.setLayout(layout)


class ExactAngle(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.hundreds = AngleSet()
        self.tens = AngleSet()
        self.ones = AngleSet()
        layout = QHBoxLayout()
        layout.addStretch()
        layout.addWidget(self.hundreds)
        layout.addWidget(self.tens)
        layout.addWidget(self.ones)
        layout.addStretch()
        self.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
        self.setLayout(layout)

    @pyqtSlot(int)
    def set_dark_mode(self, enable):
        labels = self.findChildren(QLabel)
        for label in labels:
            if enable:
                label.setStyleSheet("color: white")
            else:
                label.setStyleSheet("color: none")
