from PyQt5.QtGui import (
    QFont, QIcon
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
    QSize,
    Qt,
    pyqtSignal
)
from missionSetup import missionSetup
import resources
import json


class landingPage(QWidget):
    mission_ready = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        btn_layout = QHBoxLayout()
        label_layout = QHBoxLayout()
        main_layout = QGridLayout()

        # Setup buttons
        self.new_cfg_btn = QPushButton(QIcon(":/icons/new_config.png"), "")
        self.new_msn_btn = QPushButton(QIcon(":/icons/new_mission.png"), "")
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
        btn_layout.addWidget(self.new_cfg_btn)
        btn_layout.addWidget(self.new_msn_btn)

        # Setup labels
        new_cfg_label = QLabel("Create New Confguration")
        new_msn_label = QLabel("Start New Mission")
        new_cfg_label.setFont(QFont("Helvetica", 72, 5, False))
        new_msn_label.setFont(QFont("Helvetica", 72, 5, False))
        self.new_cfg_btn.setStyleSheet(
                "background-color: #76FF8B"
            )
        self.new_msn_btn.setStyleSheet(
                "background-color: #FF7575"
            )
        new_cfg_label.setAlignment(Qt.AlignCenter)
        new_msn_label.setAlignment(Qt.AlignCenter)

        # Setup layouts
        label_layout.addWidget(new_cfg_label)
        label_layout.addWidget(new_msn_label)
        main_layout.addLayout(btn_layout, 0, 0, 3, -1)
        main_layout.addLayout(label_layout, 3, 0, 1, -1)
        self.setLayout(main_layout)

    def open_new_msn_diag(self):
        # DEBUG
        config = json.loads("{\"date\": \"22/03/1993\", \"dl\": \"420\", \"mnemonic\": \"XXA\", \"systems\": [\"QQA\", \"QQB\", \"BQS\", \"ZZT\", \"LOL\", \"WTF\"], \"events\": [\"Checked in\", \"Checked out\", \"Saw activity\", \"Did its job\", \"Made everyone proud\", \"Broke something\", \"Saw a bird\", \"Saw a plane\", \"Got blocked\", \"Made a fast escape\"], \"applets\": [\"direction\"]}")
        self.mission_ready.emit(config)
        return
        # DEBUG
        msn_setup_diag = missionSetup(self)
        if msn_setup_diag.exec():
            config = msn_setup_diag.get_config()
            del msn_setup_diag
            self.mission_ready.emit(config)
