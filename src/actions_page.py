from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (
    QInputDialog, QLabel,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QGridLayout,
    QVBoxLayout,
    QWidget
)
from PyQt5.QtCore import (
    pyqtSignal,
    pyqtSlot
)
from log_sources import LogSource
import resources  # noqa: E401


class ActionsPage(QWidget):
    actions_valid = pyqtSignal(int, bool)

    def __init__(self, source, parent=None):
        super().__init__(parent)
        self.source = source
        self.text = LogSource.get_text(self.source).title()

        self.action_list = QListWidget()
        info_layout = QGridLayout()
        sys_btn_layout = QVBoxLayout()

        self.action_list.setStyleSheet("QListWidget::item {color: white;}")
        self.up_btn = QPushButton(QIcon(":/icons/up.png"), "")
        self.add_btn = QPushButton(QIcon(":/icons/add.png"), "")
        self.rem_btn = QPushButton(QIcon(":/icons/remove.png"), "")
        self.down_btn = QPushButton(QIcon(":/icons/down.png"), "")
        self.rem_btn.setEnabled(False)
        self.up_btn.setEnabled(False)
        self.down_btn.setEnabled(False)
        self.rem_btn.clicked.connect(self.rem_action)
        self.add_btn.clicked.connect(self.add_action)
        self.up_btn.clicked.connect(self.move_up)
        self.down_btn.clicked.connect(self.move_down)
        sys_btn_layout.addWidget(self.up_btn)
        sys_btn_layout.addWidget(self.add_btn)
        sys_btn_layout.addWidget(self.rem_btn)
        sys_btn_layout.addWidget(self.down_btn)
        field_title = QLabel(
            "<font color=\"red\">*</font> " + self.text + ":"
        )

        self.action_list.itemClicked.connect(self.item_selected)
        info_layout.addWidget(field_title, 0, 0, 1, -1)
        info_layout.addWidget(self.action_list, 1, 0, 4, 3)
        info_layout.addLayout(sys_btn_layout, 1, 3, 4, 1)
        self.setLayout(info_layout)

    @pyqtSlot(list)
    def load_from_file(self, actions):
        self.action_list.clear()
        for action in actions:
            self.action_list.addItem(action)
        self.validate()

    @pyqtSlot(QListWidgetItem)
    def item_selected(self, item):
        self.cur_item = item
        self.rem_btn.setEnabled(True)
        self.up_btn.setEnabled(True)
        self.down_btn.setEnabled(True)
        if self.action_list.currentRow() == 0:
            self.up_btn.setEnabled(False)
        if self.action_list.currentRow() == self.action_list.count() - 1:
            self.down_btn.setEnabled(False)

    @pyqtSlot()
    def rem_action(self):
        self.action_list.takeItem(self.action_list.currentRow())
        if not self.action_list.count():
            self.rem_btn.setEnabled(False)
            self.up_btn.setEnabled(False)
            self.down_btn.setEnabled(False)
            self.actions_valid.emit(1, False)
        if self.action_list.currentRow() == 0:
            self.up_btn.setEnabled(False)
        if self.action_list.currentRow() == self.action_list.count() - 1:
            self.down_btn.setEnabled(False)

    @pyqtSlot()
    def add_action(self):
        valid = False
        new_sys = None
        while not valid:
            new_sys = QInputDialog.getText(
                self,
                'Add New ' + self.text,
                self.text + ':'
            )
            if not new_sys[1]:
                return
            if not str.strip(new_sys[0]):
                QMessageBox(
                        QMessageBox.Critical,
                        "Error",
                        self.text + " name cannot be blank",
                    ).exec()
            elif new_sys[0] in [
                self.action_list.item(i).text() for i in range(
                    self.action_list.count()
                )
            ]:
                QMessageBox(
                    QMessageBox.Critical,
                    "Error",
                    self.text + " already exists",
                ).exec()
            else:
                valid = True

        self.action_list.addItem(new_sys[0])
        self.action_list.setCurrentRow(self.action_list.count() - 1)
        self.actions_valid.emit(1, True)

    @pyqtSlot()
    def move_up(self):
        self.down_btn.setEnabled(True)
        cur_index = self.action_list.currentRow()
        cur_item = self.saction_list.takeItem(cur_index)
        self.action_list.insertItem(cur_index - 1, cur_item)
        self.action_list.setCurrentRow(cur_index - 1)
        if self.action_list.currentRow() == 0:
            self.up_btn.setEnabled(False)

    @pyqtSlot()
    def move_down(self):
        self.up_btn.setEnabled(True)
        cur_index = self.action_list.currentRow()
        cur_item = self.action_list.takeItem(cur_index)
        self.action_list.insertItem(cur_index + 1, cur_item)
        self.action_list.setCurrentRow(cur_index + 1)
        if self.action_list.currentRow() == self.action_list.count() - 1:
            self.down_btn.setEnabled(False)

    def validate(self):
        self.actions_valid.emit(1, self.action_list.count() > 0)
