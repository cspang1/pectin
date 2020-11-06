from PyQt5.QtCore import (
    QState,
    QStateMachine, QTimer,
    Qt,
    pyqtSignal,
    QSettings,
    pyqtSlot
)
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QFrame, QHBoxLayout, QPushButton,
    QSizePolicy, QSplitter,
    QTextEdit,
    QVBoxLayout,
    QWidget
)
from compass_widget import Compass
from log_sources import LogSource
from angles import Angle
import resources


class LogButton(QPushButton):
    pressed = pyqtSignal(int)

    def __init__(self, text, source, parent=None):
        super().__init__(text, parent)
        self.source = source
        self.setFont(QFont("Consolas", 24, 3))
        self.index = None
        self.clicked.connect(lambda: self.pressed.emit(self.index))

    def set_index(self, index):
        self.index = index

    def activate(self, active):
        if active:
            self.setStyleSheet("""
                LogButton {background-color: lime}
                LogButton:pressed {
                    background-color: cyan
                }
            """)
        else:
            self.setStyleSheet("""
                LogButton {background-color: none}
                LogButton:pressed {
                    background-color: none
                }
            """)


class ActionsWidget(QWidget):
    acted = pyqtSignal(int)

    def __init__(self, source, parent=None):
        super().__init__(parent)
        self.source = source
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)
        self.active = None

    def add_action(self, action):
        temp_btn = LogButton(action, self.source)
        temp_btn.setSizePolicy(
            QSizePolicy.Preferred,
            QSizePolicy.Minimum
        )
        self.main_layout.addWidget(temp_btn)
        temp_btn.set_index(self.main_layout.count() - 1)
        temp_btn.pressed.connect(self.switch_active)
        return temp_btn

    def get_action(self, index):
        return self.main_layout.itemAt(index).widget().text()

    @pyqtSlot(int)
    @pyqtSlot()
    def switch_active(self, target=None):
        if target is None:
            target = -1
            for index in range(self.main_layout.count()):
                self.main_layout.itemAt(index).widget().activate(False)
        for index in range(self.main_layout.count()):
            cur = self.main_layout.itemAt(index).widget()
            if cur.index == self.active:
                cur.activate(False)
            if cur.index == target:
                cur.activate(True)
        self.active = target
        if target != -1:
            self.acted.emit(self.active)


class MissionPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        prefs = QSettings()
        prefs.beginGroup("/General")
        timeout = prefs.value("/Timeout")
        prefs.endGroup()

        # Instantiate core objects
        self.timeout_timer = QTimer()
        self.timeout_timer.setTimerType(Qt.VeryCoarseTimer)
        self.timeout_timer.setInterval(timeout * 1000)
        self.timeout_timer.setSingleShot(True)
        self.systems = ActionsWidget(LogSource.SYSTEM)
        self.systems.acted.connect(self.log_event)
        self.events = ActionsWidget(LogSource.EVENT)
        self.events.acted.connect(self.log_event)
        self.compass = Compass()
        self.compass_widget = QWidget()
        compass_layout = QHBoxLayout()
        self.compass_widget.setLayout(compass_layout)
        compass_layout.addWidget(self.compass)
        self.compass.angle_event.connect(self.log_event)

        # Setup logging state machine
        self.init_log_sm()

        # Setup splitters
        actions_splitter = QSplitter(
            Qt.Horizontal,
            frameShape=QFrame.StyledPanel,
            frameShadow=QFrame.Plain
        )
        actions_splitter.addWidget(self.systems)
        actions_splitter.addWidget(self.events)
        actions_splitter.addWidget(self.compass_widget)
        actions_splitter.setChildrenCollapsible(False)
        main_splitter = QSplitter(
            Qt.Vertical,
            frameShape=QFrame.StyledPanel,
            frameShadow=QFrame.Plain
        )
        self.log_area = QTextEdit()
        self.log_area.setAcceptRichText(True)
        main_splitter.addWidget(actions_splitter)
        main_splitter.addWidget(self.log_area)
        main_splitter.setChildrenCollapsible(False)
        handle_css = """
            QSplitter::handle {
                background-image: url(:/imgs/dot_pattern.png);
                background-repeat: repeat-xy;
                background-color: none;
                border: 1px solid gray;
            }
            QSplitter::handle:pressed {
                background-image: url(:/imgs/pressed.png);
            }
        """
        actions_splitter.setStyleSheet(handle_css)
        main_splitter.setStyleSheet(handle_css)

        # Finalize layout
        main_layout = QVBoxLayout()
        main_layout.addWidget(main_splitter)
        self.setLayout(main_layout)

    @pyqtSlot(Angle)
    @pyqtSlot(int)
    def log_event(self, data):
        self.timeout_timer.start()
        src = self.sender()
        if type(src) is ActionsWidget:
            if src.source is LogSource.SYSTEM:
                print("System: ", src.get_action(data))
            if src.source is LogSource.EVENT:
                print("Event: ", src.get_action(data))
        elif type(src) is Compass:
            self.log_area.insertPlainText(Angle.to_string(data))

    def load_mission(self, config, timer, time):
        for system in config['systems']:
            self.systems.add_action(system)
        for event in config['events']:
            self.events.add_action(event)
        self.timer = timer
        self.timer.timeout.connect(self.inc_time)
        self.time = time

    @pyqtSlot()
    def inc_time(self):
        self.time = self.time.addSecs(1)

    def init_log_sm(self):
        self.log_state = QStateMachine()
        pre_system = QState()
        pre_event = QState()
        post_event = QState()
        self.log_state.addState(pre_system)
        self.log_state.addState(pre_event)
        self.log_state.addState(post_event)
        self.log_state.setInitialState(pre_system)
        pre_system.assignProperty(self.events, "enabled", False)
        pre_system.assignProperty(self.compass, "enabled", False)
        pre_event.assignProperty(self.events, "enabled", True)
        pre_event.assignProperty(self.compass, "enabled", False)
        post_event.assignProperty(self.compass, "enabled", True)
        pre_system.addTransition(
            self.systems.acted, pre_event
        )
        pre_system.addTransition(self.timeout_timer.timeout, pre_system)
        pre_event.addTransition(self.timeout_timer.timeout, pre_system)
        post_event.addTransition(self.timeout_timer.timeout, pre_system)
        pre_event.addTransition(
            self.systems.acted, pre_event
        )
        post_event.addTransition(
            self.systems.acted, pre_event
        )
        post_event.addTransition(
            self.events.acted, post_event
        )
        pre_event.addTransition(
            self.events.acted, post_event
        )
        pre_system.entered.connect(self.events.switch_active)
        pre_system.entered.connect(self.systems.switch_active)
        pre_event.entered.connect(self.events.switch_active)
        post_event.exited.connect(self.compass.clear_state)
        pre_event.entered.connect(lambda: print('wtf'))
        self.log_state.setRunning(True)

    @pyqtSlot(int)
    def set_timeout(self, timeout):
        self.timeout_timer.setInterval(timeout * 1000)
