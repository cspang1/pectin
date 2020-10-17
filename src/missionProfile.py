from PyQt5.QtWidgets import (
    QWidget,
    QPushButton,
    QHBoxLayout,
    QTimeEdit,
    QSpinBox,
    QLabel,
    QSizePolicy,
    QFrame,
    QAbstractSpinBox,
    QLCDNumber,
    QMessageBox
)
from PyQt5.QtCore import (
    pyqtSlot,
    pyqtSignal,
    QDateTime,
    QTimer,
    Qt
)


class missionProfile(QFrame):

    def __init__(self):
        super().__init__()
        self.setFrameShape(QFrame.StyledPanel)
        self.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
