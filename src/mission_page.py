from PyQt5.QtCore import (
    QDate, QState,
    QStateMachine,
    QTimer,
    Qt,
    pyqtSignal,
    QSettings,
    pyqtSlot
)
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QFileDialog, QFrame, QGridLayout,
    QHBoxLayout,
    QLabel, QMessageBox,
    QPushButton,
    QSizePolicy,
    QSplitter,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget
)
from compass_widget import Compass
from log_sources import LogSource
from angles import Angle
import resources  # noqa: E401
import csv
import os
from pathlib import Path


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
    mission_ended = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self.record = -1
        prefs = QSettings()
        prefs.beginGroup("/General")
        timeout = prefs.value("/Timeout")
        dark_mode = prefs.value("/DarkMode")
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

        header_layout = QHBoxLayout()
        self.zulu_time_label = QLabel()
        self.assessor_label = QLabel()
        self.date_label = QLabel()
        self.dl_label = QLabel()
        self.mnemonic_label = QLabel()
        header_layout.addWidget(self.zulu_time_label)
        header_layout.addWidget(self.assessor_label)
        header_layout.addWidget(self.date_label)
        header_layout.addWidget(self.dl_label)
        header_layout.addWidget(self.mnemonic_label)
        for index in range(header_layout.count()):
            widget = header_layout.itemAt(index).widget()
            widget.setSizePolicy(
                QSizePolicy.Preferred, QSizePolicy.Maximum
            )
            widget.setFont(QFont("Consolas", 16, 2))
            widget.setAlignment(Qt.AlignCenter)

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
        self.log_area = QTableWidget(0, 3)
        self.log_area.setHorizontalHeaderLabels(
            ["Time", "System", "Events"]
        )
        self.log_area.horizontalHeader().setStretchLastSection(True)
        self.set_dark_mode(dark_mode)
        end_msn_btn = QPushButton("END MISSION")
        end_msn_btn.clicked.connect(self.end_mission)
        end_msn_btn.setFont(QFont("Consolas", 32, 5))
        end_msn_btn.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        end_msn_btn.setStyleSheet("background-color: red; color: white")
        bottom_layout = QGridLayout()
        bottom_widget = QWidget()
        bottom_widget.setLayout(bottom_layout)
        bottom_layout.addWidget(self.log_area, 0, 0, 1, 7)
        bottom_layout.addWidget(end_msn_btn, 0, 8, 1, 1)
        main_splitter.addWidget(actions_splitter)
        main_splitter.addWidget(bottom_widget)
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
        main_layout.addLayout(header_layout)
        main_layout.addWidget(main_splitter)
        self.setLayout(main_layout)

    @pyqtSlot(Angle)
    @pyqtSlot(int)
    def log_event(self, data):
        self.timeout_timer.start()
        src = self.sender()
        if type(src) is ActionsWidget:
            if src.source is LogSource.SYSTEM:
                self.save_log(True)
                self.record = self.record + 1
                event_time = self.time.toString("HH:mm:ss")
                system = src.get_action(data)
                self.log_area.insertRow(self.record)
                self.log_area.setItem(
                    self.record,
                    0,
                    QTableWidgetItem(event_time)
                )
                self.log_area.setItem(
                    self.record,
                    1,
                    QTableWidgetItem(system)
                )
                self.log_area.setItem(
                    self.record,
                    2,
                    QTableWidgetItem("")
                )
            if src.source is LogSource.EVENT:
                event = src.get_action(data)
                current = self.log_area.item(self.record, 2).text()
                if len(current) > 0:
                    current = current + "; "
                current = current + event
                self.log_area.setItem(
                    self.record,
                    2,
                    QTableWidgetItem(current)
                )
        elif type(src) is Compass:
            angle = Angle.to_string(data)
            current = self.log_area.item(self.record, 2).text()
            current = current + angle
            self.log_area.setItem(
                self.record,
                2,
                QTableWidgetItem(current)
            )

    def load_mission(self, config, timer, time):
        for system in config['systems']:
            self.systems.add_action(system)
        for event in config['events']:
            self.events.add_action(event)
        self.timer = timer
        self.timer.timeout.connect(self.inc_time)
        self.time = time
        self.assessor = config['assessor']
        self.assessor_label.setText("Assessor: " + self.assessor)
        self.date = config['date']
        self.date_label.setText("Date: " + self.date)
        self.dl = config['dl']
        self.dl_label.setText("Mission: DL-" + self.dl)
        self.mnemonic = config['mnemonic']
        self.mnemonic_label.setText("Mnemonic: " + self.mnemonic)

    @pyqtSlot()
    def inc_time(self):
        self.time = self.time.addSecs(1)
        self.zulu_time_label.setText(
            "Time: {} ZULU".format(self.time.toString("HH:mm:ss"))
        )

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
        pre_system.entered.connect(lambda: self.save_log(True))
        pre_system.entered.connect(self.events.switch_active)
        pre_system.entered.connect(self.systems.switch_active)
        pre_event.entered.connect(self.events.switch_active)
        post_event.exited.connect(self.compass.clear_state)
        self.log_state.setRunning(True)

    @pyqtSlot()
    def end_mission(self):
        quit_prompt = QMessageBox.question(
                    self,
                    "End mission?",
                    "If you choose to end this mission, the time hack will end and logging will stop. Really end?"
                )
        if quit_prompt == QMessageBox.Yes:
            if self.save_log():
                QMessageBox.information(
                        self,
                        "Mission Ended",
                        "Mission has been ended and your logs have been saved."
                    )
                self.mission_ended.emit()

    def save_log(self, temp=False):
        date = QDate.fromString(self.date, "dd/MM/yyyy").toString("yyyyMMdd")
        file_name = ("DL-{0} {1} {2}").format(
            self.dl,
            self.mnemonic,
            date
        )
        path = None
        if temp:
            path = Path(__file__).parents[1] / "temp" / "{}.csv".format(
                file_name
            )
            os.makedirs(os.path.dirname(path), exist_ok=True)
        else:
            path, _ = QFileDialog.getSaveFileName(
                    self, 'Save File', file_name, 'CSV(*.csv)'
                )
        if path:
            with open(path, 'w', newline='') as outfile:
                writer = csv.writer(outfile)
                for row in range(self.log_area.rowCount()):
                    rowdata = []
                    for column in range(self.log_area.columnCount()):
                        item = self.log_area.item(row, column)
                        if item is not None:
                            rowdata.append(
                                item.text()
                            )
                        else:
                            rowdata.append('')
                    writer.writerow(rowdata)
            return True and not temp
        return False

    """def load_log(self):
        path = QFileDialog.getOpenFileName(
                self, 'Open File', '', 'CSV(*.csv)')
        if not path.isEmpty():
            with open(unicode(path), 'rb') as stream:
                self.log_area.setRowCount(0)
                self.log_area.setColumnCount(0)
                for rowdata in csv.reader(stream):
                    row = self.log_area.rowCount()
                    self.log_area.insertRow(row)
                    self.log_area.setColumnCount(len(rowdata))
                    for column, data in enumerate(rowdata):
                        item = QTableWidgetItem(data.decode('utf8'))
                        self.log_area.setItem(row, column, item)"""

    @pyqtSlot(int)
    def set_timeout(self, timeout):
        self.timeout_timer.setInterval(timeout * 1000)

    @pyqtSlot(int)
    def set_dark_mode(self, enable):
        if enable:
            self.log_area.setStyleSheet("QTableWidget::item { color: white }")
        else:
            self.log_area.setStyleSheet("QTableWidget::item { color: none }")
