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


class missionSetup(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowTitle("Mission Setup")
        self.setModal(True)

        # Instantiate dialog elements
        time_label = QLabel("Time:")
        zulu_label = QLabel("ZULU")
        date_label = QLabel("Date:")
        dl_label = QLabel("DL-")
        sys_label = QLabel("System:")
        cfg_label = QLabel("Config:")
        self.time_edit = QTimeEdit()
        self.hack_btn = QPushButton("Hack")
        self.sys_time_btn = QPushButton("Use System Time")
        self.date_edit = QDateEdit()
        self.dl_edit = QSpinBox()
        self.sys_select = QComboBox()
        self.path_edit = QLineEdit()
        self.browse_btn = QPushButton("Browse...")
        time_btn_layout = QHBoxLayout()
        time_btn_layout.addWidget(self.hack_btn)
        time_btn_layout.addWidget(self.sys_time_btn)
        cfg_set_layout = QHBoxLayout()
        cfg_set_layout.addWidget(self.path_edit)
        cfg_set_layout.addWidget(self.browse_btn)

        # Populate dialog; Row 1
        main_layout = QGridLayout()
        main_layout.addWidget(time_label, 0, 0)
        main_layout.addWidget(self.time_edit, 0, 1)
        main_layout.addWidget(zulu_label, 0, 2)
        main_layout.addLayout(time_btn_layout, 0, 3)
        main_layout.addWidget(date_label, 0, 4)
        main_layout.addWidget(self.date_edit, 0, 5)

        # Row 2
        main_layout.addWidget(dl_label, 1, 0)
        main_layout.addWidget(self.dl_edit, 1, 1)
        main_layout.addWidget(sys_label, 1, 2)
        main_layout.addWidget(self.sys_select, 1, 3)
        main_layout.addWidget(cfg_label, 1, 4)
        main_layout.addLayout(cfg_set_layout, 1, 5)

        # Button box
        self.button_box = QDialogButtonBox()
        self.back_btn = QPushButton("< Back")
        self.next_btn = QPushButton("Next >")
        self.next_btn.setDefault(True)
        self.cancel_btn = QPushButton("Cancel")
        self.button_box.addButton(self.back_btn, QDialogButtonBox.ActionRole)
        self.button_box.addButton(self.next_btn, QDialogButtonBox.ActionRole)
        self.button_box.addButton(self.cancel_btn, QDialogButtonBox.RejectRole)

        main_layout.addWidget(self.button_box, 2, 0, -1, -1)
        self.setLayout(main_layout)
