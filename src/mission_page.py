from PyQt5.QtCore import (
    QDate,
    QSize,
    QState,
    QStateMachine,
    QTimer,
    Qt,
    pyqtSignal,
    QSettings,
    pyqtSlot
)
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QFileDialog,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QSplitter,
    QTabWidget,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget
)
from compass_widget import Compass
from exact_angle import ExactAngle
from log_sources import LogSource
from angles import Angle
from actions_widget import ActionsWidget
import resources  # noqa: F401
import csv
import os
import json
from pathlib import Path


class MissionPage(QWidget):
    mission_ended = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self.record = -1
        self.inspected = None
        self.oob_update = False
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
        self.timeout_timer.timeout.connect(self.update_temp_log)
        self.systems = ActionsWidget(LogSource.SYSTEM)
        self.systems.acted.connect(self.log_item)
        self.events = ActionsWidget(LogSource.EVENT)
        self.events.acted.connect(self.log_item)

        self.compass = Compass()
        self.compass_widget = QWidget()
        compass_layout = QHBoxLayout()
        self.compass_widget.setLayout(compass_layout)
        compass_layout.addWidget(self.compass)
        self.compass.angle_event.connect(self.log_item)

        self.exact_angle = ExactAngle()
        self.exact_angle_widget = QWidget()
        exact_angle_layout = QHBoxLayout()
        self.exact_angle_widget.setLayout(exact_angle_layout)
        exact_angle_layout.addWidget(self.exact_angle)
        self.exact_angle.btn_event.connect(self.reset_timer)
        self.exact_angle.angle_event.connect(self.log_item)

        tab_widget = QTabWidget()
        tab_bar = tab_widget.tabBar()
        tab_bar.setFont(QFont('Consolas', 12, 3))
        tab_widget.addTab(self.compass_widget, "Compass")
        tab_widget.addTab(self.exact_angle_widget, "Precise Angle")
        tab_widget.setStyleSheet("""
                QTabWidget::pane {
                    border-top: 2px solid #C2C7CB;
                }
                /* Style the tab using the tab sub-control. Note that
                    it reads QTabBar _not_ QTabWidget */
                QTabBar::tab {
                    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                stop: 0 #E1E1E1, stop: 0.4 #DDDDDD,
                                stop: 0.5 #D8D8D8, stop: 1.0 #D3D3D3);
                    border: 2px solid #C4C4C3;
                    border-bottom-color: #C2C7CB; /* same as the pane color */
                    border-top-left-radius: 4px;
                    border-top-right-radius: 4px;
                    min-width: 8ex;
                    padding: 2px;
                    color: black;
                }

                QTabBar::tab:selected, QTabBar::tab:hover {
                    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                stop: 0 #fafafa, stop: 0.4 #f4f4f4,
                                stop: 0.5 #e7e7e7, stop: 1.0 #fafafa);
                }

                QTabBar::tab:selected {
                    border-color: #ff0000;
                    border-bottom-color: #C2C7CB; /* same as pane color */
                }

                QTabBar::tab:!selected {
                    margin-top: 2px; /* make non-selected tabs look smaller */
                }
            """)

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
        actions_splitter.addWidget(tab_widget)
        actions_splitter.setChildrenCollapsible(False)
        main_splitter = QSplitter(
            Qt.Vertical,
            frameShape=QFrame.StyledPanel,
            frameShadow=QFrame.Plain
        )
        self.log_area = QTableWidget(0, 3)
        self.log_area.cellDoubleClicked.connect(self.entry_inspected)
        self.log_area.cellChanged.connect(self.entry_changed)
        self.log_area.setHorizontalHeaderLabels(
            ["Time", "System", "Events"]
        )
        self.log_area.horizontalHeader().setStretchLastSection(True)
        self.set_dark_mode(dark_mode)
        end_msn_btn = QPushButton("END\r\nMISSION")
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

    def load_mission(self, config, timer, time, recovered=None):
        cfg_systems = []
        cfg_events = []
        for system in config['systems']:
            cfg_systems.append(system)
        for event in config['events']:
            cfg_events.append(event)
        self.systems.add_actions(cfg_systems)
        self.events.add_actions(cfg_events)
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
        date = QDate.fromString(self.date, "dd/MM/yyyy").toString("yyyyMMdd")
        self.file_name = f"DL-{self.dl} {self.mnemonic} {date}"
        temp_path = Path(__file__).parents[1] / "temp"
        temp_cfg = temp_path / f"{self.file_name}.cfg"
        os.makedirs(os.path.dirname(temp_cfg), exist_ok=True)
        self.temp_log = temp_path / f"{self.file_name}.csv"
        os.makedirs(os.path.dirname(self.temp_log), exist_ok=True)
        if temp_cfg:
            with open(temp_cfg, 'w') as save_cfg_file:
                save_cfg_file.write(json.dumps(config))
        else:
            QMessageBox(
                QMessageBox.Critical,
                "Error",
                f"Unable to load recovered config file: {temp_cfg}"
            ).exec()
            return
        if recovered:
            self.recover_log(recovered)

    def recover_log(self, log):
        with open(log, 'r', newline='') as infile:
            reader = csv.reader(infile, delimiter=',')
            for row in reader:
                self.record = self.record + 1
                self.log_area.insertRow(self.record)
                self.log_area.setItem(
                    self.record,
                    0,
                    QTableWidgetItem(row[0])
                )
                self.log_area.setItem(
                    self.record,
                    1,
                    QTableWidgetItem(row[1])
                )
                self.log_area.setItem(
                    self.record,
                    2,
                    QTableWidgetItem(row[2])
                )
        # TODO: This isn't working...
        self.log_area.scrollToBottom()

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
        pre_system.assignProperty(self.exact_angle, "enabled", False)
        pre_event.assignProperty(self.events, "enabled", True)
        pre_event.assignProperty(self.compass, "enabled", False)
        pre_event.assignProperty(self.exact_angle, "enabled", False)
        post_event.assignProperty(self.compass, "enabled", True)
        post_event.assignProperty(self.exact_angle, "enabled", True)
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
        post_event.exited.connect(lambda: self.exact_angle.log_angle(False))
        self.log_state.setRunning(True)

    def log_system(self, system):
        self.record = self.record + 1
        event_time = self.time.toString("HH:mm:ss")
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
        self.log_area.scrollToBottom()

    def log_event(self, event):
        current = self.log_area.item(self.record, 2).text()
        if len(current) > 0:
            current = current + "; "
        current = current + event
        self.log_area.setItem(
            self.record,
            2,
            QTableWidgetItem(current)
        )

    def log_compass(self, range):
        current = self.log_area.item(self.record, 2).text()
        current = current + range
        self.log_area.setItem(
            self.record,
            2,
            QTableWidgetItem(current)
        )

    def log_angle(self, angle):
        current = self.log_area.item(self.record, 2).text()
        current = f"{current} at {angle}°"
        self.log_area.setItem(
            self.record,
            2,
            QTableWidgetItem(current)
        )

    @pyqtSlot(Angle)
    @pyqtSlot(int)
    def log_item(self, data):
        last_unlogged = self.timeout_timer.isActive()
        self.timeout_timer.start()
        src = self.sender()
        if type(src) is ActionsWidget:
            if self.exact_angle.has_valid():
                if self.exact_angle.is_valid():
                    self.log_angle(self.exact_angle.calc_angle())
                self.exact_angle.clear_state()
            if src.source is LogSource.SYSTEM:
                self.log_system(src.get_action(data))
                if last_unlogged:
                    self.update_temp_log()
            elif src.source is LogSource.EVENT:
                self.log_event(src.get_action(data))
        elif type(src) is Compass:
            self.log_compass(Angle.to_string(data))
        elif type(src) is ExactAngle:
            self.log_angle(str(data))

    @pyqtSlot(int, int)
    def entry_inspected(self, row, col):
        self.inspected = row, col

    @pyqtSlot(int, int)
    def entry_changed(self, row, col):
        if (row, col) == self.inspected:
            if not self.timeout_timer.isActive():
                self.update_temp_log(False)
            elif row == self.record - 1:
                self.oob_update = True

    def update_temp_log(self, append=True):
        if self.oob_update:
            append = False
            self.oob_update = False
        if self.temp_log:
            if append:
                with open(self.temp_log, 'a', newline='') as outfile:
                    writer = csv.writer(outfile)
                    rowdata = []
                    row = self.log_area.rowCount() - 1
                    for column in range(self.log_area.columnCount()):
                        item = self.log_area.item(row, column)
                        if item is not None:
                            rowdata.append(
                                item.text()
                            )
                        else:
                            rowdata.append('')
                    writer.writerow(rowdata)
            else:
                with open(self.temp_log, 'w', newline='') as outfile:
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

    def save_log(self):
        path, _ = QFileDialog.getSaveFileName(
                self, 'Save File', self.file_name, 'CSV(*.csv)'
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
            return True
        return False

    @pyqtSlot()
    def end_mission(self):
        quit_prompt = QMessageBox.question(
                    self,
                    "End mission?",
                    "If you choose to end this mission, the time hack will end and logging will stop. Really end?"  # noqa: E501
                )
        if quit_prompt == QMessageBox.Yes:
            if self.save_log():
                QMessageBox.information(
                        self,
                        "Mission Ended",
                        "Mission has been ended and your logs have been saved."
                    )
                temp_path = Path(__file__).parents[1] / "temp"
                log_files = [
                    file for file in temp_path.rglob("*.csv") if file.is_file()
                ]
                cfg_files = [
                    file for file in temp_path.rglob("*.cfg") if file.is_file()
                ]
                if log_files and cfg_files:
                    try:
                        for file in log_files + cfg_files:
                            file.unlink()
                    except OSError as e:
                        QMessageBox.critical(
                            self,
                            "Error",
                            f"Error encountered attempting to delete temp files: { e.strerror }"  # noqa: E501
                        )
                self.mission_ended.emit()

    @pyqtSlot()
    def reset_timer(self):
        self.timeout_timer.start()

    @pyqtSlot(int)
    def set_timeout(self, timeout):
        self.timeout_timer.setInterval(timeout * 1000)

    @pyqtSlot(QSize)
    def window_resized(self, size):
        self.events.resize(size.height())
        self.systems.resize(size.height())

    @pyqtSlot(int)
    def set_dark_mode(self, enable):
        if enable:
            self.log_area.setStyleSheet("QTableWidget::item { color: white }")
        else:
            self.log_area.setStyleSheet("QTableWidget::item { color: none }")
