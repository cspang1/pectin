from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (
    QInputDialog, QListWidget,
    QListWidgetItem, QMessageBox,
    QPushButton,
    QGridLayout,
    QVBoxLayout,
    QWidget
)
from PyQt5.QtCore import (
    pyqtSignal,
    pyqtSlot
)
import resources  # noqa: E401


class sysPage(QWidget):
    systems_valid = pyqtSignal(int, bool)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.system_list = QListWidget()
        self.system_list.addItem("QQA")
        self.system_list.addItem("QQB")
        self.system_list.addItem("QBG")

        info_layout = QGridLayout()
        sys_btn_layout = QVBoxLayout()

        self.up_btn = QPushButton(QIcon(":/icons/up.png"), "")
        self.add_btn = QPushButton(QIcon(":/icons/add.png"), "")
        self.rem_btn = QPushButton(QIcon(":/icons/remove.png"), "")
        self.down_btn = QPushButton(QIcon(":/icons/down.png"), "")
        self.rem_btn.setEnabled(False)
        self.up_btn.setEnabled(False)
        self.down_btn.setEnabled(False)
        self.rem_btn.clicked.connect(self.rem_system)
        self.add_btn.clicked.connect(self.add_system)
        self.up_btn.clicked.connect(self.move_up)
        self.down_btn.clicked.connect(self.move_down)
        sys_btn_layout.addWidget(self.up_btn)
        sys_btn_layout.addWidget(self.add_btn)
        sys_btn_layout.addWidget(self.rem_btn)
        sys_btn_layout.addWidget(self.down_btn)

        self.system_list.itemClicked.connect(self.item_selected)
        info_layout.addWidget(self.system_list, 0, 0, 4, 3)
        info_layout.addLayout(sys_btn_layout, 0, 3, 4, 1)
        self.setLayout(info_layout)

        # Load list here from .pcfg
        # Check if list populated, and emit systems_valid accordingly

    @pyqtSlot(list)
    def load_from_file(self, systems):
        self.system_list.clear()
        for system in systems:
            self.system_list.addItem(system)
        self.validate()

    @pyqtSlot(QListWidgetItem)
    def item_selected(self, item):
        self.cur_item = item
        self.rem_btn.setEnabled(True)
        self.up_btn.setEnabled(True)
        self.down_btn.setEnabled(True)
        if self.system_list.currentRow() == 0:
            self.up_btn.setEnabled(False)
        if self.system_list.currentRow() == self.system_list.count() - 1:
            self.down_btn.setEnabled(False)

    @pyqtSlot()
    def rem_system(self):
        self.system_list.takeItem(self.system_list.currentRow())
        if not self.system_list.count():
            self.rem_btn.setEnabled(False)
            self.up_btn.setEnabled(False)
            self.down_btn.setEnabled(False)
            self.systems_valid.emit(1, False)
        if self.system_list.currentRow() == 0:
            self.up_btn.setEnabled(False)
        if self.system_list.currentRow() == self.system_list.count() - 1:
            self.down_btn.setEnabled(False)

    @pyqtSlot()
    def add_system(self):
        valid = False
        new_sys = None
        while not valid:
            new_sys = QInputDialog.getText(
                self,
                'Add New System',
                'System:'
            )
            if not new_sys[1]:
                return
            if not str.strip(new_sys[0]):
                QMessageBox(
                        QMessageBox.Critical,
                        "Error",
                        "System name cannot be blank",
                    ).exec()
            elif new_sys[0] in [
                self.system_list.item(i).text() for i in range(
                    self.system_list.count()
                )
            ]:
                QMessageBox(
                    QMessageBox.Critical,
                    "Error",
                    "System already exists",
                ).exec()
            else:
                valid = True

        self.system_list.addItem(new_sys[0])
        self.system_list.setCurrentRow(self.system_list.count() - 1)
        self.systems_valid.emit(1, True)

    @pyqtSlot()
    def move_up(self):
        self.down_btn.setEnabled(True)
        cur_index = self.system_list.currentRow()
        cur_item = self.system_list.takeItem(cur_index)
        self.system_list.insertItem(cur_index - 1, cur_item)
        self.system_list.setCurrentRow(cur_index - 1)
        if self.system_list.currentRow() == 0:
            self.up_btn.setEnabled(False)

    @pyqtSlot()
    def move_down(self):
        self.up_btn.setEnabled(True)
        cur_index = self.system_list.currentRow()
        cur_item = self.system_list.takeItem(cur_index)
        self.system_list.insertItem(cur_index + 1, cur_item)
        self.system_list.setCurrentRow(cur_index + 1)
        if self.system_list.currentRow() == self.system_list.count() - 1:
            self.down_btn.setEnabled(False)

    def validate(self):
        self.systems_valid.emit(1, self.system_list.count() > 0)
