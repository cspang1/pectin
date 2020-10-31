from PyQt5.QtWidgets import (
    QInputDialog, QListWidget,
    QListWidgetItem, QMessageBox,
    QPushButton,
    QGridLayout,
    QVBoxLayout,
    QWidget
)
from PyQt5.QtCore import (
    Qt, pyqtSlot,
)


class sysPage(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.system_list = QListWidget()
        self.system_list.addItem("QQA")
        self.system_list.addItem("QQB")
        self.system_list.addItem("QBG")

        info_layout = QGridLayout()
        sys_btn_layout = QVBoxLayout()

        self.up_btn = QPushButton("^")
        self.add_btn = QPushButton("+")
        self.rem_btn = QPushButton("-")
        self.down_btn = QPushButton("v")
        self.rem_btn.setEnabled(False)
        self.up_btn.setEnabled(False)
        self.down_btn.setEnabled(False)
        self.rem_btn.clicked.connect(self.rem_system)
        self.add_btn.clicked.connect(self.add_system)
        sys_btn_layout.addWidget(self.up_btn)
        sys_btn_layout.addWidget(self.add_btn)
        sys_btn_layout.addWidget(self.rem_btn)
        sys_btn_layout.addWidget(self.down_btn)

        self.system_list.itemClicked.connect(self.item_selected)
        info_layout.addWidget(self.system_list, 0, 0, 4, 3)
        info_layout.addLayout(sys_btn_layout, 0, 3, 4, 1)
        self.setLayout(info_layout)

    @pyqtSlot(QListWidgetItem)
    def item_selected(self, item):
        self.cur_item = item
        self.rem_btn.setEnabled(True)
        self.up_btn.setEnabled(True)
        self.down_btn.setEnabled(True)

    @pyqtSlot()
    def rem_system(self):
        self.system_list.takeItem(self.system_list.currentRow())
        if not self.system_list.count():
            self.rem_btn.setEnabled(False)
            self.up_btn.setEnabled(False)
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
