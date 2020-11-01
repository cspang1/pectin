from PyQt5.QtWidgets import (
    QHBoxLayout, QPushButton, QVBoxLayout, QWidget,
)

class missionPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.main_layout = QHBoxLayout()
        self.sys_layout = QVBoxLayout()
        self.event_layout = QVBoxLayout()
        self.main_layout.addLayout(self.sys_layout)
        self.main_layout.addLayout(self.event_layout)

        self.setLayout(self.main_layout)

    def load_mission(self, config):
        for system in config['systems']:
            temp_btn = QPushButton(system)
            self.sys_layout.addWidget(temp_btn)
        for event in config['events']:
            temp_btn = QPushButton(event)
            self.event_layout.addWidget(temp_btn)
