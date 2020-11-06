import re
import subprocess
import time
from PyQt5.QtWidgets import (
    QCheckBox, QDialog,
    QFormLayout,
    QDialogButtonBox, QHBoxLayout,
    QLabel,
    QComboBox,
    QPushButton, QSpinBox,
    QSizePolicy, QLayout
)
from PyQt5.QtCore import Qt, QSettings, pyqtSignal, pyqtSlot


class PrefsPage(QDialog):
    apply = pyqtSignal(int, int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Preferences")
        self.prefs = QSettings()

        self.prefs.beginGroup("/General")
        self.dark_mode = self.prefs.value("/DarkMode")
        self.timeout = self.prefs.value("/Timeout")
        self.prefs.endGroup()

        timeout_layout = QHBoxLayout()
        self.dark_mode_set = QCheckBox()
        self.dark_mode_set.setChecked(self.dark_mode)
        self.dark_mode_set.stateChanged.connect(self.set_dark_mode)
        self.timeout_set = QSpinBox()
        self.timeout_set.setRange(1, 10)
        self.timeout_set.valueChanged.connect(self.set_timeout)
        self.timeout_set.setValue(self.timeout)
        timeout_layout.addWidget(self.timeout_set)
        timeout_layout.addWidget(QLabel("seconds"))

        self.actions = QDialogButtonBox(
            QDialogButtonBox.Ok
            | QDialogButtonBox.Apply
            | QDialogButtonBox.Cancel
        )
        self.actions.clicked.connect(self.handlePrefsBtns)

        settings_form = QFormLayout()
        settings_form.addRow("Dark Mode:", self.dark_mode_set)
        settings_form.addRow("Event Timeout:", timeout_layout)
        settings_form.addWidget(self.actions)
        settings_form.setSizeConstraint(QLayout.SetFixedSize)
        self.setLayout(settings_form)

    @pyqtSlot(int)
    def set_dark_mode(self, enabled):
        self.dark_mode = enabled

    @pyqtSlot(int)
    def set_timeout(self, seconds):
        self.timeout = seconds

    def handlePrefsBtns(self, button):
        if button is self.actions.button(QDialogButtonBox.Cancel):
            self.reject()
        elif button is self.actions.button(QDialogButtonBox.Apply):
            self.apply.emit(self.dark_mode, self.timeout)
        elif button is self.actions.button(QDialogButtonBox.Ok):
            self.accept()
