from PyQt5.QtCore import (
    QPoint,
    QSize,
    Qt, pyqtSignal
)
from PyQt5.QtGui import (
    QBrush,
    QColor,
    QFont,
    QPainter,
    QPen
)
from PyQt5.QtWidgets import (
    QLabel,
    QSizePolicy,
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
from angles import Angle


class CompassWedge(QWidget):
    def __init__(
            self,
            start_angle,
            w_width,
            w_height,
            w_offset,
            id,
            parent=None):
        super().__init__(parent)
        self.setFixedSize(w_width, w_height)
        self.setMouseTracking(True)
        self.start = start_angle
        self.offset = w_offset
        self.active = False
        self.id = id
        self.marked = False

    def paintEvent(self, event):
        painter = QPainter(self)
        super().paintEvent(event)
        painter.setRenderHint(QPainter.Antialiasing)
        brush = None
        if not self.parent().isEnabled():
            brush = QBrush(QColor(Qt.lightGray))
        elif self.active:
            brush = QBrush(QColor(Qt.red))
        elif self.marked:
            brush = QBrush(QColor(Qt.green))
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

    def mark(self, marked):
        self.marked = marked
        self.update()


class Compass(QWidget):
    angle_event = pyqtSignal(Angle)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.offset = 75
        self.span = self.offset + 525
        self.center = QPoint(self.span/2, self.span/2)
        self.setMinimumSize(self.span, self.span)
        self.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
        self.setMouseTracking(True)

        self.wedges = []
        for start in range(0, 360 * 16, 45 * 16):
            self.wedges.append(
                CompassWedge(
                    start,
                    self.span,
                    self.span,
                    self.offset,
                    Angle(floor(((360 - start/16 + 45) % 360)/45)),
                    self
                )
            )

        deg_font = QFont("Consolas", 22, 2)
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
        elif angle == 90:
            off_y = -size_y/2
        elif angle == 135:
            off_y = -size_y
        elif angle == 180:
            off_x = -size_x/2
            off_y = -size_y
        elif angle == 225:
            off_y = -size_y
            off_x = -size_x
        elif angle == 270:
            off_y = -size_y/2
            off_x = -size_x
        elif angle == 315:
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
        if dist <= floor(self.span/2) - self.offset:
            if 0 <= angle < (2*pi)/8:
                self.activate_wedge(2)
            elif (2*pi)/8 <= angle < 2*(2*pi)/8:
                self.activate_wedge(3)
            elif 2*(2*pi)/8 <= angle < 3*(2*pi)/8:
                self.activate_wedge(4)
            elif 3*(2*pi)/8 <= angle < 4*(2*pi)/8:
                self.activate_wedge(5)
            elif 0 > angle >= -(2*pi)/8:
                self.activate_wedge(1)
            elif -(2*pi)/8 > angle >= -2*(2*pi)/8:
                self.activate_wedge(0)
            elif -2*(2*pi)/8 > angle >= -3*(2*pi)/8:
                self.activate_wedge(7)
            elif -3*(2*pi)/8 > angle >= -4*(2*pi)/8:
                self.activate_wedge(6)
        else:
            self.activate_wedge(-1)

    def mouseReleaseEvent(self, event):
        for wedge in self.wedges:
            if wedge.active:
                self.angle_event.emit(wedge.id)
                wedge.mark(True)

    def activate_wedge(self, active):
        for index in range(self.wedges.__len__()):
            self.wedges[index].activate(True if index == active else False)

    def clear_state(self):
        for wedge in self.wedges:
            wedge.mark(False)
