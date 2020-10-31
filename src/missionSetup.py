from PyQt5.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
)
from PyQt5.QtCore import (
    pyqtSlot,
)
from infoPage import infoPage
from sysPage import sysPage


class missionSetup(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
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
        self.button_box.addButton(self.back_btn, QDialogButtonBox.ActionRole)
        self.button_box.addButton(self.next_btn, QDialogButtonBox.ActionRole)
        self.button_box.addButton(self.cancel_btn, QDialogButtonBox.RejectRole)

        # Setup frame objects
        self.multi_page = QStackedWidget()
        self.main_layout = QVBoxLayout()
        self.info_page = infoPage()
        self.systems_page = sysPage()
        self.multi_page.currentChanged.connect(self.page_changed)
        self.info_page.info_valid.connect(self.enable_next)
        self.systems_page.systems_valid.connect(self.enable_next)
        self.multi_page.addWidget(self.info_page)
        self.multi_page.addWidget(self.systems_page)

        self.main_layout.addWidget(self.multi_page)
        self.main_layout.addWidget(self.button_box)

        self.setLayout(self.main_layout)

    def next_page(self):
        self.multi_page.setCurrentIndex(self.multi_page.currentIndex() + 1)
        self.back_btn.setEnabled(True)

    def prev_page(self):
        new_index = self.multi_page.currentIndex() - 1
        self.multi_page.setCurrentIndex(new_index)

        if new_index == 0:
            self.back_btn.setEnabled(False)

    @pyqtSlot(bool)
    def enable_next(self, enable):
        self.next_btn.setEnabled(enable)

    @pyqtSlot(int)
    def page_changed(self, index):
        if index == 0:
            self.info_page.validate()
        elif index == 1:
            self.systems_page.validate()
