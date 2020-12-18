from PyQt5.QtCore import (
    pyqtSlot
)
from PyQt5.QtWidgets import (
    QGridLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QWidget
)


class Angles(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
        self.setMouseTracking(True)

        main_layout = QGridLayout()
        for row in range(24):
            for col in range(15):
                temp_btn = QPushButton(str(col + row * 15) + '°')
                temp_btn.setStyleSheet("padding: 10px")
                main_layout.addWidget(temp_btn, row, col)

        self.setLayout(main_layout)

    @pyqtSlot(int)
    def set_dark_mode(self, enable):
        labels = self.findChildren(QLabel)
        for label in labels:
            if enable:
                label.setStyleSheet("color: white")
            else:
                label.setStyleSheet("color: none")
