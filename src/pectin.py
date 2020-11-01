from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import (
    QMainWindow
)
from missionPage import missionPage
from landingPage import landingPage


class pectin(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setupWindow()

    def setupWindow(self):
        self.setWindowTitle("Pectin")
        self.landing_page = landingPage()
        self.landing_page.mission_ready.connect(self.setup_mission)
        self.setCentralWidget(self.landing_page)

    @pyqtSlot(dict)
    def setup_mission(self, config):
        self.mission_page = missionPage()
        self.mission_page.load_mission(config)
        self.setCentralWidget(self.mission_page)
