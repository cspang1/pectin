from PyQt5.QtCore import (
    QCoreApplication, QSettings, QTime,
    QTimer, Qt, pyqtSignal,
    pyqtSlot
)
from PyQt5.QtGui import QColor, QIcon, QPalette
from PyQt5.QtWidgets import (
    QAction, QApplication, QMainWindow,
    QMessageBox
)
from mission_page import MissionPage
from landing_page import LandingPage
from prefs_page import PrefsPage


class pectin(QMainWindow):
    dark_mode_set = pyqtSignal(int)
    timeout_set = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Pectin")
        self.setWindowIcon(QIcon(":/icons/pectin.png"))
        self.setup_actions()
        self.set_landing_page()

        QCoreApplication.setOrganizationName("Connor Spangler")
        QCoreApplication.setOrganizationDomain("https://github.com/cspang1")
        QCoreApplication.setApplicationName("Pectin")
        self.prefs = QSettings()
        self.dark_mode_set.connect(self.set_dark_mode)
        self.init_prefs()

    def setup_actions(self):
        # Exit
        exit_act = QAction("&Exit", self)
        exit_act.setShortcut("Ctrl+Q")
        exit_act.setStatusTip("Exit application")
        exit_act.triggered.connect(self.verify_quit)

        # Open preferences
        open_prefs = QAction("&Preferences", self)
        open_prefs.setStatusTip("Edit preferences")
        open_prefs.triggered.connect(self.open_prefs)

        self.menu_bar = self.menuBar()
        file_menu = self.menu_bar.addMenu("&File")
        file_menu.addAction(open_prefs)
        file_menu.addAction(exit_act)

    @pyqtSlot()
    def open_prefs(self):
        prefs = PrefsPage()
        prefs.apply.connect(self.apply_prefs)
        if prefs.exec():
            self.apply_prefs(prefs.dark_mode, prefs.timeout)

    @pyqtSlot(dict, QTimer, QTime)
    def setup_mission(self, config, timer, time):
        mission_page = MissionPage()
        mission_page.load_mission(config, timer, time)
        mission_page.mission_ended.connect(self.set_landing_page)
        self.timeout_set.connect(mission_page.set_timeout)
        self.dark_mode_set.connect(mission_page.compass.set_dark_mode)
        self.dark_mode_set.connect(mission_page.set_dark_mode)
        self.setCentralWidget(mission_page)

    @pyqtSlot(str)
    def save_config(self, config_file):
        load_msn = QMessageBox.question(
            self,
            "Config Created",
            "New configuration successfully created. Would you like to load it into a new mission?"
        )

        if load_msn == QMessageBox.Yes:
            self.landing_page.open_new_msn_diag(config_file)

    @pyqtSlot(int, int)
    def apply_prefs(self, dark_mode, timeout):
        self.prefs.beginGroup("/General")
        self.prefs.setValue("/DarkMode", dark_mode)
        self.prefs.setValue("/Timeout", timeout)
        self.prefs.endGroup()

        self.dark_mode_set.emit(dark_mode)
        self.timeout_set.emit(timeout)

    @pyqtSlot()
    def set_landing_page(self):
        self.landing_page = LandingPage()
        self.landing_page.mission_ready.connect(self.setup_mission)
        self.landing_page.config_ready.connect(self.save_config)
        self.setCentralWidget(self.landing_page)

    @pyqtSlot(int)
    def set_dark_mode(self, enabled):
        app = QApplication.instance()
        if enabled:
            palette = QPalette()
            self.menu_bar.setStyleSheet("QMenu::item {color: white}")
            palette.setColor(QPalette.Window, QColor(53, 53, 53))
            palette.setColor(QPalette.WindowText, Qt.white)
            palette.setColor(QPalette.Base, QColor(25, 25, 25))
            palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
            palette.setColor(QPalette.ToolTipBase, Qt.black)
            palette.setColor(QPalette.ToolTipText, Qt.white)
            palette.setColor(QPalette.Button, QColor(53, 53, 53))
            palette.setColor(QPalette.BrightText, Qt.red)
            palette.setColor(QPalette.Link, QColor(42, 130, 218))
            palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
            palette.setColor(QPalette.HighlightedText, Qt.black)
            app.setPalette(palette)
        else:
            self.menu_bar.setStyleSheet("QMenu::item {color: none}")
            app.setPalette(app.style().standardPalette())
        self.setStyleSheet("""
            QMessageBox {
                background-color: #333333;
            }

            QMessageBox QLabel {
                color: #aaa;
            }
        """)

    def init_prefs(self):
        self.prefs.beginGroup("/General")
        dark_mode = self.prefs.value("/DarkMode", 1)
        timeout = self.prefs.value("/Timeout", 5)
        self.prefs.endGroup()
        self.dark_mode_set.emit(dark_mode)
        self.timeout_set.emit(timeout)

    @pyqtSlot()
    def verify_quit(self):
        if hasattr(self, 'mission_page'):
            quit_prompt = QMessageBox.question(
                        self,
                        "Really quit?",
                        "You currently have a mission in progress. Are you sure you want to quit?"
                    )
            if quit_prompt == QMessageBox.Yes:
                QApplication.quit()
        else:
            QApplication.quit()
