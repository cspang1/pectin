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


class eventsPage(QWidget):
    events_valid = pyqtSignal(int, bool)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.event_list = QListWidget()
        info_layout = QGridLayout()
        event_btn_layout = QVBoxLayout()

        self.up_btn = QPushButton(QIcon(":/icons/up.png"), "")
        self.add_btn = QPushButton(QIcon(":/icons/add.png"), "")
        self.rem_btn = QPushButton(QIcon(":/icons/remove.png"), "")
        self.down_btn = QPushButton(QIcon(":/icons/down.png"), "")
        self.rem_btn.setEnabled(False)
        self.up_btn.setEnabled(False)
        self.down_btn.setEnabled(False)
        self.rem_btn.clicked.connect(self.rem_event)
        self.add_btn.clicked.connect(self.add_event)
        self.up_btn.clicked.connect(self.move_up)
        self.down_btn.clicked.connect(self.move_down)
        event_btn_layout.addWidget(self.up_btn)
        event_btn_layout.addWidget(self.add_btn)
        event_btn_layout.addWidget(self.rem_btn)
        event_btn_layout.addWidget(self.down_btn)

        self.event_list.itemClicked.connect(self.item_selected)
        info_layout.addWidget(self.event_list, 0, 0, 4, 3)
        info_layout.addLayout(event_btn_layout, 0, 3, 4, 1)
        self.setLayout(info_layout)

    @pyqtSlot(list)
    def load_from_file(self, events):
        self.event_list.clear()
        for event in events:
            self.event_list.addItem(event)
        self.validate()

    @pyqtSlot(QListWidgetItem)
    def item_selected(self, item):
        self.cur_item = item
        self.rem_btn.setEnabled(True)
        self.up_btn.setEnabled(True)
        self.down_btn.setEnabled(True)
        if self.event_list.currentRow() == 0:
            self.up_btn.setEnabled(False)
        if self.event_list.currentRow() == self.event_list.count() - 1:
            self.down_btn.setEnabled(False)

    @pyqtSlot()
    def rem_event(self):
        self.event_list.takeItem(self.event_list.currentRow())
        if not self.event_list.count():
            self.rem_btn.setEnabled(False)
            self.up_btn.setEnabled(False)
            self.down_btn.setEnabled(False)
            self.events_valid.emit(2, False)
        if self.event_list.currentRow() == 0:
            self.up_btn.setEnabled(False)
        if self.event_list.currentRow() == self.event_list.count() - 1:
            self.down_btn.setEnabled(False)

    @pyqtSlot()
    def add_event(self):
        valid = False
        new_event = None
        while not valid:
            new_event = QInputDialog.getText(
                self,
                'Add New Event',
                'Event:'
            )
            if not new_event[1]:
                return
            if not str.strip(new_event[0]):
                QMessageBox(
                        QMessageBox.Critical,
                        "Error",
                        "Event cannot be blank",
                    ).exec()
            elif new_event[0] in [
                self.event_list.item(i).text() for i in range(
                    self.event_list.count()
                )
            ]:
                QMessageBox(
                    QMessageBox.Critical,
                    "Error",
                    "Event already exists",
                ).exec()
            else:
                valid = True

        self.event_list.addItem(new_event[0])
        self.event_list.setCurrentRow(self.event_list.count() - 1)
        self.events_valid.emit(2, True)

    @pyqtSlot()
    def move_up(self):
        self.down_btn.setEnabled(True)
        cur_index = self.event_list.currentRow()
        cur_item = self.event_list.takeItem(cur_index)
        self.event_list.insertItem(cur_index - 1, cur_item)
        self.event_list.setCurrentRow(cur_index - 1)
        if self.event_list.currentRow() == 0:
            self.up_btn.setEnabled(False)

    @pyqtSlot()
    def move_down(self):
        self.up_btn.setEnabled(True)
        cur_index = self.event_list.currentRow()
        cur_item = self.event_list.takeItem(cur_index)
        self.event_list.insertItem(cur_index + 1, cur_item)
        self.event_list.setCurrentRow(cur_index + 1)
        if self.event_list.currentRow() == self.event_list.count() - 1:
            self.down_btn.setEnabled(False)

    def validate(self):
        self.events_valid.emit(2, self.event_list.count() > 0)
