from PyQt5.QtCore import QPoint, QSize, Qt
from PyQt5.QtGui import (
    QBrush, QColor, QFont,
    QPainter,
    QPen
)
from PyQt5.QtWidgets import (
    QDialog,
    QGridLayout, QLabel, QSizePolicy,
    QWidget
)
from math import (
    hypot,
    floor,
    atan2,
    pi,
    sin,
    cos,
    radians
)


class compassWedge(QWidget):
    def __init__(self, start_angle, w, h, o, parent=None):
        super().__init__(parent)
        self.start = start_angle
        self.setFixedSize(w, h)
        self.offset = o
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
        painter.drawPie(
            self.offset,
            self.offset,
            self.width() - self.offset * 2,
            self.height() - self.offset * 2,
            self.start,
            45 * 16
        )
        painter.end()

    def activate(self, is_active):
        self.active = is_active
        self.update()


class compassApplet(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.span = 600
        self.offset = 75
        self.center = QPoint(self.span/2, self.span/2)
        self.setFixedSize(self.span, self.span)
        self.setMouseTracking(True)

        self.wedges = []
        for start in range(0, 360 * 16, 45 * 16):
            self.wedges.append(
                compassWedge(
                    start,
                    self.span,
                    self.span,
                    self.offset,
                    self
                )
            )

        deg_font = QFont("Consolas", 18, 2)
        for deg in range(8):
            temp = QLabel(self)
            angle = deg * 45
            temp.setText(str(angle) + '°')
            temp.setFont(deg_font)
            temp.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
            tw = temp.fontMetrics().boundingRect(temp.text()).width()
            th = temp.fontMetrics().boundingRect(temp.text()).height()
            temp.move(self.deg_lbl_pos((180 - angle) % 360, QSize(tw, th)))

    def deg_lbl_pos(self, angle, size):
        x_0 = self.center.x()
        y_0 = self.center.y()
        size_x = size.width()
        size_y = size.height()
        off_x = 0
        off_y = 0
        dist = self.span/2 - self.offset + 10
        if angle == 0:
            off_x = -size_x/2
        if angle == 90:
            off_y = -size_y/2
        if angle == 135:
            off_y = -size_y
        if angle == 180:
            off_x = -size_x/2
            off_y = -size_y
        if angle == 225:
            off_y = -size_y
            off_x = -size_x
        if angle == 270:
            off_y = -size_y/2
            off_x = -size_x
        if angle == 315:
            off_x = -size_x

        theta_rad = pi/2 - radians(angle)
        return QPoint(
            round(x_0 + dist*cos(theta_rad) + off_x),
            round(y_0 + dist*sin(theta_rad) + off_y)
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
