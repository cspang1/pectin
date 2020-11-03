from PyQt5.QtWidgets import (
    QHBoxLayout,
    QPushButton,
    QSizePolicy,
    QTextEdit,
    QVBoxLayout,
    QWidget
)
from compass_widget import Compass
from log_sources import LogSource
from angles import Angle


class LogButton(QPushButton):
    def __init__(self, text, source, parent=None):
        super().__init__(text, parent)
        self.source = source


class MissionPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.main_layout = QVBoxLayout()
        self.interactive_layout = QHBoxLayout()
        self.sys_layout = QVBoxLayout()
        self.event_layout = QVBoxLayout()
        self.interactive_layout.addLayout(self.sys_layout)
        self.interactive_layout.addLayout(self.event_layout)
        self.compass = Compass()
        self.compass.angle_event.connect(self.log_event)
        self.log_area = QTextEdit()
        self.log_area.setAcceptRichText(True)
        self.main_layout.addLayout(self.interactive_layout)
        self.main_layout.addWidget(self.log_area)

        self.setLayout(self.main_layout)

    def load_mission(self, config):
        for system in config['systems']:
            temp_btn = LogButton(system, LogSource.SYSTEM)
            temp_btn.setSizePolicy(
                QSizePolicy.Preferred,
                QSizePolicy.Minimum
            )
            temp_btn.clicked.connect(self.log_event)
            self.sys_layout.addWidget(temp_btn)
        for event in config['events']:
            temp_btn = LogButton(event, LogSource.EVENT)
            temp_btn.setSizePolicy(
                QSizePolicy.Preferred,
                QSizePolicy.Minimum
            )
            temp_btn.clicked.connect(self.log_event)
            self.event_layout.addWidget(temp_btn)
        self.interactive_layout.addWidget(self.compass)

    def log_event(self, angle=None):
        src = self.sender()
        if type(src) is LogButton:
            if src.source is LogSource.EVENT:
                self.compass.setEnabled(True)
                self.log_area.insertPlainText(" " + src.text())
            elif src.source is LogSource.SYSTEM:
                self.compass.setEnabled(False)
                self.log_area.insertPlainText("\n")
                self.log_area.insertPlainText(src.text())
        elif type(src) is Compass:
            self.log_area.insertPlainText(Angle.to_string(angle))
