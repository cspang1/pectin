from pathlib import Path
import os
import json
from PyQt5.QtWidgets import (
    QComboBox,
    QFileDialog,
    QInputDialog,
    QLineEdit,
    QPushButton,
    QGridLayout,
    QHBoxLayout,
    QSizePolicy,
    QTimeEdit,
    QLabel,
    QFrame,
    QMessageBox,
    QDateEdit,
    QWidget
)
from PyQt5.QtCore import (
    QDate,
    QTime,
    QTimer,
    Qt,
    pyqtSignal,
    pyqtSlot
)


class baseFrame(QFrame):
    field_valid = pyqtSignal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameStyle(QFrame.Panel)
        self.layout = QHBoxLayout()
        self.layout.setAlignment(Qt.AlignCenter)


class timeFrame(baseFrame):
    time_hacked = pyqtSignal()

    def __init__(self, is_mission, parent=None):
        super().__init__(parent)

        # Setup frame
        time_label = QLabel("Time:")
        zulu_label = QLabel("ZULU")
        zulu_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.time_edit = QTimeEdit()
        self.time_edit.setDisplayFormat("HH:mm:ss")
        self.hack_btn = QPushButton("Hack")
        self.hack_btn.setAutoDefault(False)
        if is_mission:
            self.hack_btn.setStyleSheet("background-color: red; color: white;")
        else:
            self.hack_btn.setStyleSheet("background-color: gray; color: white;")
        self.sys_time_btn = QPushButton("Use System Time")
        self.sys_time_btn.setAutoDefault(False)

        if not is_mission:
            self.time_edit.setEnabled(False)
            self.hack_btn.setEnabled(False)
            self.sys_time_btn.setEnabled(False)

        self.layout.addWidget(time_label)
        self.layout.addWidget(self.time_edit)
        self.layout.addWidget(zulu_label)
        self.layout.addWidget(self.hack_btn)
        self.layout.addWidget(self.sys_time_btn)
        self.setLayout(self.layout)

        # Setup behavior
        self.time = QTime()
        self.hack_timer = QTimer()
        self.hack_timer.setTimerType(Qt.VeryCoarseTimer)
        self.hack_timer.setInterval(1000)
        self.hack_timer.timeout.connect(self.inc_time)
        self.hack_btn.clicked.connect(self.hack_time)
        self.sys_time_btn.clicked.connect(self.set_sys_time)

    @pyqtSlot()
    def hack_time(self, sys_time=None):
        if not self.hack_timer.isActive():
            self.time = self.time_edit.time() if not sys_time else sys_time
            self.hack_timer.start()
            self.time_edit.setTime(self.time)
            self.hack_btn.setStyleSheet(
                "background-color: green; color: white;"
            )
            self.hack_btn.setText("Hacked!")
            self.time_edit.setEnabled(False)
            self.sys_time_btn.setEnabled(False)
        else:
            self.hack_btn.setStyleSheet("background-color: red; color: white;")
            self.hack_btn.setText("Hack")
            self.hack_timer.stop()
            self.time_edit.setEnabled(True)
            self.sys_time_btn.setEnabled(True)
        self.time_hacked.emit()

    @pyqtSlot()
    def set_sys_time(self):
        self.hack_time(QTime().currentTime())

    @pyqtSlot()
    def inc_time(self):
        self.time = self.time.addSecs(1)
        self.time_edit.setTime(self.time)


class dateFrame(baseFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        date_label = QLabel("Date:")
        self.date_edit = QDateEdit(QDate.currentDate())
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.layout.addWidget(date_label)
        self.layout.addWidget(self.date_edit)
        self.setLayout(self.layout)


class dlFrame(baseFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        dl_label = QLabel("DL-")
        self.dl_edit = QLineEdit()
        self.dl_edit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.layout.addWidget(dl_label)
        self.layout.addWidget(self.dl_edit)
        self.setLayout(self.layout)


class mnemonicFrame(baseFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        mnem_label = QLabel("Mnemonic:")
        self.mnem_select = QComboBox()
        self.mnem_select.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Fixed
        )
        self.layout.addWidget(mnem_label)
        self.layout.addWidget(self.mnem_select)
        self.setLayout(self.layout)

        self.mnem_list_path = Path(__file__).parents[1] / "res" / "mnemonics.json"
        os.makedirs(os.path.dirname(self.mnem_list_path), exist_ok=True)
        if not self.mnem_list_path.exists():
            self.mnem_list_path(self.mnem_list_path)

        self.cur_mnemonics = None
        self.load_mnemonics()
        # Un-comment to allow user to add mnemonics
        # self.mnem_select.activated.connect(self.mnem_selected)

    def load_mnemonics(self, active=None):
        self.mnem_select.clear()
        with open(self.mnem_list_path, 'r') as mnem_list:
            try:
                self.cur_mnemonics = json.load(mnem_list)
            except Exception:
                self.new_mnem_file()(self.mnem_list_path)
                # How can we handle this kind of recursive try?
                self.cur_mnemonics = json.load(mnem_list)

        self.mnem_select.setPlaceholderText('...')
        self.mnem_select.addItems(self.cur_mnemonics['mnemonics'])
        # Un-comment to allow user to add mnemonics
        # self.mnem_select.addItem('+ Add new')

        if active:
            self.mnem_select.setCurrentIndex(self.mnem_select.findText(active))

    def add_mnemonic(self, mnemonic):
        self.cur_mnemonics['mnemonics'].append(mnemonic)
        self.cur_mnemonics['mnemonics'] = sorted(
            self.cur_mnemonics['mnemonics'],
            key=str.casefold
        )
        with open(self.mnem_list_path, 'w') as mnen_list:
            mnen_list.write(json.dumps(self.cur_mnemonics))

    @pyqtSlot(int)
    def mnem_selected(self, index):
        if index == self.mnem_select.count() - 1:
            named = False
            selected = None
            while not named:
                selected = QInputDialog.getText(
                    self,
                    'Add New Mnemonic',
                    'Mnemonic:'
                )
                if not selected[1]:
                    return
                elif not str.strip(selected[0]):
                    QMessageBox(
                        QMessageBox.Critical,
                        "Error",
                        "Mnemonic cannot be blank",
                    ).exec()
                elif selected[0] in [
                    self.mnem_select.itemText(i) for i in range(
                        self.mnem_select.count()
                    )
                ]:
                    QMessageBox(
                        QMessageBox.Critical,
                        "Error",
                        "Mnemonic already exists",
                    ).exec()
                else:
                    named = True
            mnemonic = selected[0]
            self.add_mnemonic()(mnemonic)
            self.load_mnemonics()(mnemonic)

    def new_mnem_file(self, mnem_list_path):
        default = json.dumps({'mnemonics': ['XXA', 'XXB']})
        with open(mnem_list_path, 'w') as mnem_list:
            mnem_list.write(default)


class cfgFrame(baseFrame):
    info_loaded = pyqtSignal(QDate, str, str)
    systems_loaded = pyqtSignal(list)
    events_loaded = pyqtSignal(list)
    applets_loaded = pyqtSignal(list)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.cfg = None
        cfg_label = QLabel("Config:")
        self.path_edit = QLineEdit()
        self.path_edit.setEnabled(False)
        self.browse_btn = QPushButton("Browse...")
        self.browse_btn.setAutoDefault(False)
        self.browse_btn.clicked.connect(self.load_cfg)
        self.layout.addWidget(cfg_label)
        self.layout.addWidget(self.path_edit)
        self.layout.addWidget(self.browse_btn)
        self.setLayout(self.layout)

    @pyqtSlot()
    def load_cfg(self, file_name=None):
        if not file_name:
            file_name, _ = QFileDialog.getOpenFileName(
                self,
                "Select Pectin Config File",
                "",
                "Pectin Config File (*.pcfg)"
            )
            if file_name:
                self.cfg = file_name
                self.path_edit.setText(self.cfg)
            else:
                return
        else:
            self.cfg = file_name
            self.path_edit.setText(self.cfg)

        config = None
        with open(file_name, 'r') as config_file:
            try:
                config = json.load(config_file)
            except Exception as e:
                QMessageBox(
                    QMessageBox.Critical,
                    "Error",
                    "Unable to load config file: {}".format(e),
                ).exec()
                return

        # Extract data
        date = QDate.fromString(config['date'], "dd/MM/yyyy")
        dl = config['dl']
        mnemonic = config['mnemonic']
        systems = config['systems']
        events = config['events']
        applets = config['applets']

        self.info_loaded.emit(date, dl, mnemonic)
        self.systems_loaded.emit(systems)
        self.events_loaded.emit(events)
        self.applets_loaded.emit(applets)


class infoPage(QWidget):
    info_valid = pyqtSignal(int, bool)

    def __init__(self, is_mission, parent=None):
        super().__init__(parent)
        self.is_mission = is_mission

        self.time_setup = timeFrame(self.is_mission)
        self.date_setup = dateFrame()
        self.dl_setup = dlFrame()
        self.mnem_setup = mnemonicFrame()
        self.cfg_setup = cfgFrame()

        # Setup frame signals/slots
        self.time_setup.time_hacked.connect(self.validate)
        self.dl_setup.dl_edit.textEdited.connect(self.validate)
        self.mnem_setup.mnem_select.activated.connect(self.validate)
        self.cfg_setup.info_loaded.connect(self.load_from_file)

        # Populate dialog; Row 1
        info_layout = QGridLayout()
        info_layout.addWidget(self.time_setup, 0, 0, 1, 4)
        info_layout.addWidget(self.date_setup, 0, 4, 1, 2)

        # Row 2
        info_layout.addWidget(self.dl_setup, 1, 0, 1, 2)
        info_layout.addWidget(self.mnem_setup, 1, 2, 1, 2)
        info_layout.addWidget(self.cfg_setup, 1, 4, 1, 2)

        self.setLayout(info_layout)

    @pyqtSlot(QDate, str, str)
    def load_from_file(self, date, dl, mnemonic):
        self.date_setup.date_edit.setDate(date)
        self.dl_setup.dl_edit.setText(dl)
        self.mnem_setup.mnem_select.setCurrentText(mnemonic)
        self.validate()

    def preload_cfg(self, config):
        self.cfg_setup.load_cfg(config)

    @pyqtSlot()
    def validate(self):
        time_valid = self.time_setup.hack_timer.isActive()
        dl_valid = len(str.strip(self.dl_setup.dl_edit.text())) > 0
        mnem_valid = self.mnem_setup.mnem_select.currentIndex() >= 0

        if not self.is_mission:
            self.info_valid.emit(0, dl_valid and mnem_valid)
        else:
            self.info_valid.emit(0, time_valid and dl_valid and mnem_valid)
