from PyQt5.QtCore import QPoint, Qt
from PyQt5.QtGui import (
    QBrush, QColor,
    QPainter,
    QPen
)
from PyQt5.QtWidgets import (
    QDialog,
    QGridLayout,
    QWidget
)
from math import (
    hypot,
    floor,
    atan2,
    pi
)


class compassWedge(QWidget):
    def __init__(self, start_angle, w, h, parent=None):
        super().__init__(parent)
        self.start = start_angle
        self.setFixedSize(w, h)
        self.setMouseTracking(True)
        self.active = False

    def paintEvent(self, event):
        painter = QPainter(self)
        super().paintEvent(event)
        painter.setRenderHint(QPainter.Antialiasing)
        brush = None
        if self.active:
            brush = QBrush(QColor(Qt.red))
        else:
            brush = QBrush(QColor(Qt.white))
        pen = QPen(Qt.black)
        pen.setWidth(5)
        painter.setBrush(brush)
        painter.setPen(pen)
        painter.drawPie(50, 50, 500, 500, self.start, 45 * 16)
        painter.end()

    def activate(self, is_active):
        self.active = is_active
        self.update()


class compassApplet(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.w_width = 600
        self.w_height = 600
        self.center = QPoint(self.w_width/2, self.w_height/2)
        self.setFixedSize(self.w_width, self.w_height)
        self.setMouseTracking(True)

        self.wedges = []
        for start in range(0, 360 * 16, 45 * 16):
            self.wedges.append(
                compassWedge(
                    start,
                    self.w_width,
                    self.w_height,
                    self
                )
            )

    def mouseMoveEvent(self, event):
        x_1 = event.pos().x()
        y_1 = event.pos().y()
        x_2 = self.center.x()
        y_2 = self.center.y()
        dist = floor(hypot(x_2 - x_1, y_2 - y_1))
        angle = atan2(x_2 - x_1, y_2 - y_1)
        if dist <= 250:
            if 0 <= angle < (2*pi)/8:
                self.activate_wedge(2)
            if (2*pi)/8 <= angle < 2*(2*pi)/8:
                self.activate_wedge(3)
            if 2*(2*pi)/8 <= angle < 3*(2*pi)/8:
                self.activate_wedge(4)
            if 3*(2*pi)/8 <= angle < 4*(2*pi)/8:
                self.activate_wedge(5)
            if 0 > angle >= -(2*pi)/8:
                self.activate_wedge(1)
            if -(2*pi)/8 > angle >= -2*(2*pi)/8:
                self.activate_wedge(0)
            if -2*(2*pi)/8 > angle >= -3*(2*pi)/8:
                self.activate_wedge(7)
            if -3*(2*pi)/8 > angle >= -4*(2*pi)/8:
                self.activate_wedge(6)
        else:
            self.activate_wedge(-1)

    def activate_wedge(self, active):
        for index, wedge in enumerate(self.wedges):
            self.wedges[index].activate(True if index == active else False)


class test(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        ca = compassApplet()
        la = QGridLayout()
        la.addWidget(ca, 1, 1)
        self.setLayout(la)
