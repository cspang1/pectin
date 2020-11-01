
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QLabel,
    QLayout,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
)
from PyQt5.QtCore import (
    pyqtSlot,
)
from infoPage import infoPage
from sysPage import sysPage
from eventsPage import eventsPage
import json

class setupDiag(QDialog):
    def __init__(self, is_mission, config, parent):
        super().__init__(parent)
        self.is_mission = is_mission
        if not self.is_mission:
            self.setWindowTitle("Config Setup")
        else:
            self.setWindowTitle("Mission Setup")

        self.setModal(True)

        # Button box
        self.button_box = QDialogButtonBox()
        self.back_btn = QPushButton("< Back")
        self.back_btn.setEnabled(False)
        self.back_btn.clicked.connect(self.prev_page)
        self.next_btn = QPushButton("Next >")
        self.next_btn.setEnabled(False)
        self.next_btn.setDefault(True)
        self.next_btn.clicked.connect(self.next_page)
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        self.button_box.addButton(self.back_btn, QDialogButtonBox.ActionRole)
        self.button_box.addButton(self.next_btn, QDialogButtonBox.ActionRole)
        self.button_box.addButton(self.cancel_btn, QDialogButtonBox.RejectRole)

        # Setup frame objects
        self.multi_page = QStackedWidget()
        self.main_layout = QVBoxLayout()
        self.info_page = infoPage(self.is_mission)
        self.systems_page = sysPage()
        self.events_page = eventsPage()
        self.multi_page.currentChanged.connect(self.page_changed)
        self.info_page.info_valid.connect(self.enable_next)
        self.systems_page.systems_valid.connect(self.enable_next)
        self.events_page.events_valid.connect(self.enable_next)
        self.info_page.cfg_setup.systems_loaded.connect(
            self.systems_page.load_from_file
        )
        self.info_page.cfg_setup.events_loaded.connect(
            self.events_page.load_from_file
        )
        header_font = QFont("Consolas", 12, -1)
        self.header = QLabel("Mission Info:")
        self.header.setFont(header_font)
        self.multi_page.addWidget(self.info_page)
        self.multi_page.addWidget(self.systems_page)
        self.multi_page.addWidget(self.events_page)
        self.main_layout.addWidget(self.header)
        self.main_layout.addWidget(self.multi_page)
        self.main_layout.addWidget(self.button_box)
        self.main_layout.setSizeConstraint(QLayout.SetFixedSize)

        if config:
            self.info_page.preload_cfg(config)
        self.new_config = None

        self.setLayout(self.main_layout)

    def next_page(self):
        if self.multi_page.currentIndex() == 2:
            if self.is_mission:
                self.accept()
            else:
                save_cfg_path, _ = QFileDialog.getSaveFileName(
                    self,
                    "Save Config File",
                    "",
                    "Pectin Config File (*.pcfg)"
                )
                if save_cfg_path:
                    with open(save_cfg_path, 'w') as save_cfg_file:
                        save_cfg_file.write(json.dumps(self.get_config()))
                    self.new_config = save_cfg_path
                    self.accept()
                else:
                    return

        self.multi_page.setCurrentIndex(self.multi_page.currentIndex() + 1)
        if self.multi_page.currentIndex() == 2:
            if self.is_mission:
                self.next_btn.setText("Ok")
            else:
                self.next_btn.setText("Save")
        self.back_btn.setEnabled(True)
        self.set_page_header()

    def prev_page(self):
        new_index = self.multi_page.currentIndex() - 1
        self.multi_page.setCurrentIndex(new_index)
        self.next_btn.setText("Next >")

        if new_index == 0:
            self.back_btn.setEnabled(False)

        self.set_page_header()

    def set_page_header(self):
        if self.multi_page.currentIndex() == 0:
            self.header.setText("Mission Info:")
        elif self.multi_page.currentIndex() == 1:
            self.header.setText("Systems List:")
        elif self.multi_page.currentIndex() == 2:
            self.header.setText("Events List:")

    @pyqtSlot(int, bool)
    def enable_next(self, page, enable):
        if page == self.multi_page.currentIndex():
            self.next_btn.setEnabled(enable)

    @pyqtSlot(int)
    def page_changed(self, index):
        if index == 0:
            self.info_page.validate()
        elif index == 1:
            self.systems_page.validate()
        elif index == 2:
            self.events_page.validate()

    def get_config(self):
        config = {}
        info = self.info_page
        systems = self.systems_page
        events = self.events_page
        config['date'] = info.date_setup.date_edit.date().toString(
            "dd/MM/yyyy"
        )
        config['dl'] = info.dl_setup.dl_edit.text()
        config['mnemonic'] = info.mnem_setup.mnem_select.currentText()
        system_list = []
        for index in range(systems.system_list.count()):
            system_list.append(systems.system_list.item(index).text())
        config['systems'] = system_list
        events_list = []
        for index in range(events.event_list.count()):
            events_list.append(events.event_list.item(index).text())
        config['events'] = events_list
        config['applets'] = ["direction"]
        return config

    def get_config_file(self):
        return self.new_config
