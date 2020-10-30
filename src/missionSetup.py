from pathlib import Path
import os
import json
from PyQt5.QtWidgets import (
    QComboBox, QFileDialog,
    QInputDialog,
    QLineEdit,
    QDialog,
    QDialogButtonBox,
    QPushButton,
    QGridLayout,
    QHBoxLayout,
    QSizePolicy,
    QTimeEdit,
    QSpinBox,
    QLabel,
    QFrame,
    QMessageBox,
    QDateEdit
)
from PyQt5.QtCore import (
    QDate,
    QTime,
    QTimer,
    Qt, pyqtSignal,
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

    def __init__(self, parent=None):
        super().__init__(parent)

        # Setup frame
        time_label = QLabel("Time:")
        zulu_label = QLabel("ZULU")
        zulu_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.time_edit = QTimeEdit()
        self.time_edit.setDisplayFormat("HH:mm:ss")
        self.hack_btn = QPushButton("Hack")
        self.hack_btn.setAutoDefault(False)
        self.hack_btn.setStyleSheet("background-color: red; color: white;")
        self.sys_time_btn = QPushButton("Use System Time")
        self.sys_time_btn.setAutoDefault(False)
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


class sysFrame(baseFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        sys_label = QLabel("System:")
        self.sys_select = QComboBox()
        self.layout.addWidget(sys_label)
        self.layout.addWidget(self.sys_select)
        self.setLayout(self.layout)

        self.sys_list_path = Path(__file__).parents[1] / "res" / "systems.json"
        os.makedirs(os.path.dirname(self.sys_list_path), exist_ok=True)
        if not self.sys_list_path.exists():
            self.new_sys_file(self.sys_list_path)

        self.cur_systems = None
        self.load_systems()
        # Un-comment to allow user to add systems
        # self.sys_select.activated.connect(self.sys_selected)

    def load_systems(self, active=None):
        self.sys_select.clear()
        with open(self.sys_list_path, 'r') as sys_list:
            try:
                self.cur_systems = json.load(sys_list)
            except Exception:
                self.new_sys_file(self.sys_list_path)
                # How can we handle this kind of recursive try?
                self.cur_systems = json.load(sys_list)

        self.sys_select.setPlaceholderText('...')
        self.sys_select.addItems(self.cur_systems['systems'])
        # Un-comment to allow user to add systems
        # self.sys_select.addItem('+ Add new')

        if active:
            self.sys_select.setCurrentIndex(self.sys_select.findText(active))

    def add_system(self, system):
        self.cur_systems['systems'].append(system)
        self.cur_systems['systems'] = sorted(
            self.cur_systems['systems'],
            key=str.casefold
        )
        with open(self.sys_list_path, 'w') as sys_list:
            sys_list.write(json.dumps(self.cur_systems))

    @pyqtSlot(int)
    def sys_selected(self, index):
        if index == self.sys_select.count() - 1:
            named = False
            selected = None
            while not named:
                selected = QInputDialog.getText(
                    self,
                    'Add New System',
                    'System:'
                )
                if not selected[1]:
                    return
                elif not str.strip(selected[0]):
                    QMessageBox(
                        QMessageBox.Critical,
                        "Error",
                        "System name cannot be blank",
                    ).exec()
                elif selected[0] in [
                    self.sys_select.itemText(i) for i in range(
                        self.sys_select.count()
                    )
                ]:
                    QMessageBox(
                        QMessageBox.Critical,
                        "Error",
                        "System already exists",
                    ).exec()
                else:
                    named = True
            system = selected[0]
            self.add_system(system)
            self.load_systems(system)

    def new_sys_file(self, sys_list_path):
        default = json.dumps({'systems': ['XXA', 'XXB']})
        with open(sys_list_path, 'w') as sys_list:
            sys_list.write(default)


class cfgFrame(baseFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
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
    def load_cfg(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "Select Pectin Config File",
            "",
            "Pectin Config File (*.pcfg)"
        )
        self.path_edit.setText(file_name)


class missionSetup(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowTitle("Mission Setup")
        self.setModal(True)

        # Setup frame objects
        self.time_setup = timeFrame()
        self.date_setup = dateFrame()
        self.dl_setup = dlFrame()
        self.sys_setup = sysFrame()
        self.cfg_setup = cfgFrame()

        # Setup frame signals/slots
        self.time_setup.time_hacked.connect(self.validate)
        self.dl_setup.dl_edit.textEdited.connect(self.validate)
        self.sys_setup.sys_select.activated.connect(self.validate)

        # Populate dialog; Row 1
        main_layout = QGridLayout()
        main_layout.addWidget(self.time_setup, 0, 0, 1, 4)
        main_layout.addWidget(self.date_setup, 0, 4, 1, 2)

        # Row 2
        main_layout.addWidget(self.dl_setup, 1, 0, 1, 2)
        main_layout.addWidget(self.sys_setup, 1, 2, 1, 2)
        main_layout.addWidget(self.cfg_setup, 1, 4, 1, 2)

        # Button box
        self.button_box = QDialogButtonBox()
        self.back_btn = QPushButton("< Back")
        self.back_btn.setEnabled(False)
        self.next_btn = QPushButton("Next >")
        self.next_btn.setEnabled(False)
        self.next_btn.setDefault(True)
        self.cancel_btn = QPushButton("Cancel")
        self.button_box.addButton(self.back_btn, QDialogButtonBox.ActionRole)
        self.button_box.addButton(self.next_btn, QDialogButtonBox.ActionRole)
        self.button_box.addButton(self.cancel_btn, QDialogButtonBox.RejectRole)

        main_layout.addWidget(self.button_box, 2, 0, -1, -1)
        self.setLayout(main_layout)
        self.setFixedSize(main_layout.sizeHint())

    @pyqtSlot()
    def validate(self):
        time_valid = self.time_setup.hack_timer.isActive()
        dl_valid = len(str.strip(self.dl_setup.dl_edit.text())) > 0
        sys_valid = self.sys_setup.sys_select.currentIndex() >= 0
        self.next_btn.setEnabled(time_valid and dl_valid and sys_valid)