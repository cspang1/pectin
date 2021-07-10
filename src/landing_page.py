from PyQt5.QtGui import (
    QFont,
    QIcon
)
from PyQt5.QtWidgets import (
    QGridLayout,
    QLabel,
    QSizePolicy,
    QWidget,
    QPushButton,
    QHBoxLayout,
)
from PyQt5.QtCore import (
    QSize, QTime, QTimer,
    Qt,
    pyqtSignal
)
from setup_dialog import SetupDiag
import resources  # noqa: F401


class LandingPage(QWidget):
    mission_ready = pyqtSignal(dict, QTimer, QTime)
    config_ready = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        btn_layout = QHBoxLayout()
        label_layout = QHBoxLayout()
        main_layout = QGridLayout()

        # Setup buttons
        self.new_cfg_btn = QPushButton(QIcon(":/icons/new_config.png"), "")
        self.new_msn_btn = QPushButton(QIcon(":/icons/new_mission.png"), "")
        self.new_cfg_btn.enterEvent = self.cfg_btn_active
        self.new_msn_btn.enterEvent = self.msn_btn_active
        self.new_cfg_btn.leaveEvent = self.cfg_btn_inactive
        self.new_msn_btn.leaveEvent = self.msn_btn_inactive
        self.cfg_btn_inactive()
        self.msn_btn_inactive()
        self.new_cfg_btn.setIconSize(QSize(512, 512))
        self.new_msn_btn.setIconSize(QSize(512, 512))
        self.new_cfg_btn.setSizePolicy(
            QSizePolicy.Preferred,
            QSizePolicy.Minimum
        )
        self.new_msn_btn.setSizePolicy(
            QSizePolicy.Preferred,
            QSizePolicy.Minimum
        )
        self.new_msn_btn.clicked.connect(self.open_new_msn_diag)
        self.new_cfg_btn.clicked.connect(self.open_new_cfg_diag)
        btn_layout.addWidget(self.new_cfg_btn)
        btn_layout.addWidget(self.new_msn_btn)

        # Setup labels
        new_cfg_label = QLabel("Create New Config")
        new_msn_label = QLabel("Start New Mission")
        font = QFont("Lucida Console", 64, 5, False)
        new_cfg_label.setFont(font)
        new_msn_label.setFont(font)
        new_cfg_label.setAlignment(Qt.AlignCenter)
        new_msn_label.setAlignment(Qt.AlignCenter)

        # Setup layouts
        label_layout.addWidget(new_cfg_label)
        label_layout.addWidget(new_msn_label)
        main_layout.addLayout(btn_layout, 0, 0, 3, -1)
        main_layout.addLayout(label_layout, 3, 0, 1, -1)
        self.setLayout(main_layout)

    def open_new_msn_diag(self, config=None):
        msn_setup_diag = SetupDiag(True, config, self)
        if msn_setup_diag.exec():
            config = msn_setup_diag.get_config()
            timer, time = msn_setup_diag.get_timing()
            del msn_setup_diag
            self.mission_ready.emit(config, timer, time)

    def open_new_cfg_diag(self, config=None):
        cfg_setup_diag = SetupDiag(False, config, self)
        if cfg_setup_diag.exec():
            config = cfg_setup_diag.get_config_file()
            del cfg_setup_diag
            self.config_ready.emit(config)

    def cfg_btn_active(self, event=None):
        self.new_cfg_btn.setStyleSheet(
                "background-color: #76FF8B"
            )

    def cfg_btn_inactive(self, event=None):
        self.new_cfg_btn.setStyleSheet(
                "background-color: #2EC845"
            )

    def msn_btn_active(self, event=None):
        self.new_msn_btn.setStyleSheet(
                "background-color: #FF7575"
            )

    def msn_btn_inactive(self, event=None):
        self.new_msn_btn.setStyleSheet(
                "background-color: #F13131"
            )
