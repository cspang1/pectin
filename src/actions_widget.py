from PyQt5.QtCore import (
    pyqtSignal,
    pyqtSlot
)
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QApplication,
    QGridLayout,
    QPushButton,
    QSizePolicy,
    QWidget
)
import math


class LogButton(QPushButton):
    pressed = pyqtSignal(int)

    def __init__(self, text, source, parent=None):
        super().__init__(text, parent)
        self.source = source
        self.setFont(QFont("Consolas", 24, 3))
        self.index = None
        self.clicked.connect(lambda: self.pressed.emit(self.index))

    def set_index(self, index):
        self.index = index

    def activate(self, active):
        if active:
            self.setStyleSheet("""
                LogButton {background-color: lime}
                LogButton:pressed {
                    background-color: cyan
                }
            """)
        else:
            self.setStyleSheet("""
                LogButton {background-color: none}
                LogButton:pressed {
                    background-color: none
                }
            """)


class ActionsWidget(QWidget):
    acted = pyqtSignal(int)

    def __init__(self, source, parent=None):
        super().__init__(parent)
        self.source = source
        self.columns = 1
        self.btns = []
        self.main_layout = QGridLayout()
        self.setLayout(self.main_layout)
        self.active = None

    def add_actions(self, actions):
        for action in actions:
            temp_btn = LogButton(action, self.source)
            temp_btn.setSizePolicy(
                QSizePolicy.Preferred,
                QSizePolicy.Minimum
            )
            self.btns.append(temp_btn)
            temp_btn.set_index(len(self.btns) - 1)
            temp_btn.pressed.connect(self.switch_active)

        self.resize(QApplication.primaryScreen().size().height())

    def get_action(self, index):
        return self.btns[index].text()

    @pyqtSlot(int)
    @pyqtSlot()
    def switch_active(self, target=None):
        if target is None:
            target = -1
            for btn in self.btns:
                btn.activate(False)
        for btn in self.btns:
            if btn.index == self.active:
                btn.activate(False)
            if btn.index == target:
                btn.activate(True)
        self.active = target
        if target != -1:
            self.acted.emit(self.active)

    def resize(self, height):
        max_height = height * .75
        _, top, _, bottom = self.main_layout.getContentsMargins()
        height = (
            len(self.btns) * (
                self.btns[0].sizeHint().height() +
                top +
                bottom
            )
        )
        n_cols = math.ceil(height / max_height)

        row = col = 0
        for btn in self.btns:
            self.main_layout.addWidget(btn, row, col)
            col += 1
            if col > n_cols - 1:
                col = 0
                row += 1
