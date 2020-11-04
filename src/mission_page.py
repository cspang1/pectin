from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtWidgets import (
    QPushButton,
    QSizePolicy, QSplitter,
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


class ActionsWidget(QWidget):
    def __init__(self, source, parent=None):
        super().__init__(parent)
        self.source = source
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)

    def addAction(self, action):
        temp_btn = LogButton(action, self.source)
        temp_btn.setSizePolicy(
            QSizePolicy.Preferred,
            QSizePolicy.Minimum
        )
        self.main_layout.addWidget(temp_btn)
        return temp_btn


class MissionPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        main_layout = QVBoxLayout()
        self.systems = ActionsWidget(LogSource.SYSTEM)
        self.events = ActionsWidget(LogSource.EVENT)
        self.compass = Compass()
        self.compass.angle_event.connect(self.log_event)
        actions_splitter = QSplitter(Qt.Horizontal)
        actions_splitter.addWidget(self.systems)
        actions_splitter.addWidget(self.events)
        actions_splitter.addWidget(self.compass)
        actions_splitter.setChildrenCollapsible(False)
        main_splitter = QSplitter(Qt.Vertical)
        self.log_area = QTextEdit()
        self.log_area.setAcceptRichText(True)
        main_splitter.addWidget(actions_splitter)
        main_splitter.addWidget(self.log_area)
        main_splitter.setChildrenCollapsible(False)
        main_layout.addWidget(main_splitter)
        self.setLayout(main_layout)

    def load_mission(self, config, timer, time):
        for system in config['systems']:
            self.systems.addAction(system).clicked.connect(self.log_event)
        for event in config['events']:
            self.events.addAction(event).clicked.connect(self.log_event)
        self.timer = timer
        self.timer.timeout.connect(self.inc_time)
        self.time = time

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

    @pyqtSlot()
    def inc_time(self):
        self.time = self.time.addSecs(1)
