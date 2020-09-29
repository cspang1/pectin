from PyQt5.QtWidgets import (
    QMainWindow,
    QSplitter,
    QFrame
)
from PyQt5.QtCore import (
    Qt
)


class pectin(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setupWindow()

    def setupWindow(self):
        self.setWindowTitle("Pectin")
        main_split = QSplitter(Qt.Vertical)
        top = QFrame()
        top.setFrameShape(QFrame.StyledPanel)
        bottom = QFrame()
        bottom.setFrameShape(QFrame.StyledPanel)
        main_split.addWidget(top)
        main_split.addWidget(bottom)
        self.setCentralWidget(main_split)
