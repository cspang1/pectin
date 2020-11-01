from PyQt5.QtCore import pyqtSlot
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (
    QMainWindow,
    QMessageBox
)
from missionPage import missionPage
from landingPage import landingPage


class pectin(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Pectin")
        self.landing_page = landingPage()
        self.landing_page.mission_ready.connect(self.setup_mission)
        self.landing_page.config_ready.connect(self.save_config)
        self.setWindowIcon(QIcon(":/icons/pectin.png"))
        self.setCentralWidget(self.landing_page)

    @pyqtSlot(dict)
    def setup_mission(self, config):
        self.mission_page = missionPage()
        self.mission_page.load_mission(config)
        self.setCentralWidget(self.mission_page)

    @pyqtSlot(str)
    def save_config(self, config_file):
        load_msn = QMessageBox.question(
            self,
            "Config Created",
            "New configuration successfully created. Would you like to load it into a new mission?"
        )

        if load_msn == QMessageBox.Yes:
            self.landing_page.open_new_msn_diag(config_file)
