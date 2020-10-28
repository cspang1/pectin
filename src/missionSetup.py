from PyQt5.QtWidgets import (
    QComboBox,
    QLineEdit,
    QWidget,
    QDialog,
    QDialogButtonBox,
    QPushButton,
    QGridLayout,
    QHBoxLayout,
    QVBoxLayout,
    QTimeEdit,
    QSpinBox,
    QLabel,
    QSizePolicy,
    QFrame,
    QAbstractSpinBox,
    QLCDNumber,
    QMessageBox,
    QDateEdit
)
from PyQt5.QtCore import (
    pyqtSlot,
    pyqtSignal,
    QDateTime,
    QTimer,
    QDate,
    QTime,
    Qt
)


class baseFrame(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameStyle(QFrame.Panel)
        self.layout = QHBoxLayout()
        self.layout.setAlignment(Qt.AlignHCenter)


class timeFrame(baseFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        time_label = QLabel("Time:")
        zulu_label = QLabel("ZULU")
        zulu_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.time_edit = QTimeEdit()
        self.time_edit.setDisplayFormat("HH:mm:ss")
        self.hack_btn = QPushButton("Hack")
        self.hack_btn.setAutoDefault(False)
        self.sys_time_btn = QPushButton("Use System Time")
        self.sys_time_btn.setAutoDefault(False)
        self.layout.addWidget(time_label)
        self.layout.addWidget(self.time_edit)
        self.layout.addWidget(zulu_label)
        self.layout.addWidget(self.hack_btn)
        self.layout.addWidget(self.sys_time_btn)
        self.setLayout(self.layout)


class dateFrame(baseFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        date_label = QLabel("Date:")
        self.date_edit = QDateEdit(QDate.currentDate())
        self.date_edit.setCalendarPopup(True)
        self.layout.addWidget(date_label)
        self.layout.addWidget(self.date_edit)
        self.setLayout(self.layout)


class dlFrame(baseFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        dl_label = QLabel("DL-")
        self.dl_edit = QSpinBox()
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


class cfgFrame(baseFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        cfg_label = QLabel("Config:")
        self.path_edit = QLineEdit()
        self.browse_btn = QPushButton("Browse...")
        self.browse_btn.setAutoDefault(False)
        self.layout.addWidget(cfg_label)
        self.layout.addWidget(self.path_edit)
        self.layout.addWidget(self.browse_btn)
        self.setLayout(self.layout)


class missionSetup(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowTitle("Mission Setup")
        self.setModal(True)

        self.time_setup = timeFrame()
        self.date_setup = dateFrame()
        self.dl_setup = dlFrame()
        self.sys_setup = sysFrame()
        self.cfg_setup = cfgFrame()

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
        self.next_btn.setDefault(True)
        self.cancel_btn = QPushButton("Cancel")
        self.button_box.addButton(self.back_btn, QDialogButtonBox.ActionRole)
        self.button_box.addButton(self.next_btn, QDialogButtonBox.ActionRole)
        self.button_box.addButton(self.cancel_btn, QDialogButtonBox.RejectRole)

        main_layout.addWidget(self.button_box, 2, 0, -1, -1)
        self.setLayout(main_layout)
        self.setFixedSize(main_layout.sizeHint())
