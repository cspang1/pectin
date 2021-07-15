from PyQt5.QtGui import (
    QFont,
    QIcon,
    QPainter,
    QPen
)
from PyQt5.QtCore import (
    QAbstractAnimation,
    QParallelAnimationGroup,
    QPoint,
    QPropertyAnimation,
    QSize,
    Qt,
    pyqtSignal,
    pyqtSlot
)
from PyQt5.QtWidgets import (
    QLabel,
    QPushButton,
    QSizePolicy,
    QWidget
)
from enum import (
    IntEnum,
    unique
)
import resources  # noqa: F401


@unique
class BtnSource(IntEnum):
    HUNDREDS = 0
    TENS = 1
    ONES = 2


class Overlay(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_NoSystemBackground)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.raise_()

    def paintEvent(self, event):
        painter = QPainter(self)
        super().paintEvent(event)
        painter.setRenderHint(QPainter.Antialiasing)
        pen = QPen(Qt.red)
        pen.setWidth(5)
        painter.setPen(pen)
        painter.drawLine(0, 55, 340, 55)
        painter.drawLine(0, 105, 340, 105)
        painter.end()


class AngleButton(QPushButton):
    pressed = pyqtSignal(int)

    def __init__(self, value, parent=None):
        super().__init__(str(value), parent)
        self.setFont(QFont("Consolas", 16, 3))
        self.setFixedSize(100, 50)
        self.index = value
        self.activated = False
        self.clicked.connect(lambda: self.pressed.emit(self.index))
        self.setStyleSheet("""
            AngleButton {background-color: none}
            AngleButton:pressed {
                background-color: cyan
            }
        """)

    def activate(self, active):
        if active:
            self.setStyleSheet("""
                AngleButton {background-color: lime}
                AngleButton:pressed {
                    background-color: cyan
                }
            """)
            self.activated = True
        else:
            self.setStyleSheet("""
                AngleButton {background-color: none}
                AngleButton:pressed {
                    background-color: cyan
                }
            """)
            self.activated = False

    @pyqtSlot(QAbstractAnimation.State)
    def disable(self, state):
        if state == QAbstractAnimation.Running:
            self.setEnabled(False)
        elif state == QAbstractAnimation.Stopped:
            self.setEnabled(True)
            self.activate(self.activated)


class AngleSet(QWidget):
    acted = pyqtSignal(int, BtnSource)

    def __init__(self, source, parent=None):
        super().__init__(parent)
        self.source = source
        self.active = 0
        self.setFixedSize(100, 550)
        self.anim_gp = QParallelAnimationGroup()
        self.limit = 4 if self.source is BtnSource.HUNDREDS else 10
        y_offset = 55
        self.digits = []
        self.digits_pos = [idx for idx in range(self.limit)]
        for digit in range(self.limit):
            tmp_btn = AngleButton(digit, self)
            tmp_btn.move(0, y_offset)
            y_offset = y_offset + 50
            tmp_btn.pressed.connect(self.switch_active)
            self.anim_gp.stateChanged.connect(tmp_btn.disable)
            self.digits.append(tmp_btn)

    @pyqtSlot(int)
    def switch_active(self, target=None):
        if target is None:
            target = -1
            for index in range(len(self.digits)):
                self.active = target
                self.digits[index].activate(False)
                return

        for index in range(len(self.digits)):
            cur = self.digits[index]
            if cur.index == self.active:
                cur.activate(False)
            if cur.index == target:
                cur.activate(True)

        self.active = target
        self.acted.emit(self.active, self.source)
        self.anim_set(target)

    def anim_set(self, target):
        self.anims = []
        self.anim_gp.clear()
        diff = self.digits_pos.index(target)
        if not diff:
            return
        positions = self.digits_pos[diff:] + self.digits_pos[:diff]
        duration = diff * 50 * .8
        print(duration)

        for digit in self.digits:
            new_pos = positions.index(digit.index)
            if new_pos > self.digits_pos.index(digit.index):
                pass  # Wrapped
            else:
                anim = QPropertyAnimation(digit, b"pos", digit)
                anim.setDuration(duration)
                anim.setStartValue(digit.pos())
                anim.setEndValue(
                    QPoint(
                        digit.pos().x(), digit.pos().y() - diff * 50
                    )
                )
                self.anims.append(anim)

        for anim in self.anims:
            self.anim_gp.addAnimation(anim)
        self.anim_gp.start()

        self.digits_pos = positions

    def reset(self):
        for digit in self.digits:
            digit.activate(False)


class ExactAngle(QWidget):
    angle_event = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(450, 550)
        self.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)

        self.selected = {
            BtnSource.HUNDREDS: (False, None),
            BtnSource.TENS: (False, None),
            BtnSource.ONES: (False, None)
        }

        self.hundreds = AngleSet(BtnSource.HUNDREDS, self)
        self.tens = AngleSet(BtnSource.TENS, self)
        self.ones = AngleSet(BtnSource.ONES, self)
        self.angle_sets = [
            self.hundreds,
            self.tens,
            self.ones
        ]
        self.hundreds.move(10, 0)
        self.tens.move(120, 0)
        self.ones.move(230, 0)
        for set in [self.hundreds, self.tens, self.ones]:
            set.acted.connect(self.digit_pressed)

        deg_sym = QLabel("°", self)
        deg_sym.setFont(QFont("Consolas", 32, 3))
        deg_sym.move(350, 40)

        self.go_btn = QPushButton(QIcon(":/icons/tick_red.png"), "", self)
        self.go_btn.setEnabled(False)
        self.go_btn.move(385, 55)
        self.go_btn.setFixedSize(50, 50)
        self.go_btn.setIconSize(QSize(50, 50))
        self.go_btn.pressed.connect(self.log_angle)

        overlay = Overlay(self)
        overlay.setGeometry(self.geometry())

    @pyqtSlot()
    def log_angle(self):
        self.angle_event.emit(
            self.selected[BtnSource.HUNDREDS][1] * 100 +
            self.selected[BtnSource.TENS][1] * 10 +
            self.selected[BtnSource.ONES][1]
        )

    @pyqtSlot(int, BtnSource)
    def digit_pressed(self, value, source):
        self.selected[source] = True, value
        if all(val[0] is True for val in self.selected.values()):
            self.go_btn.setEnabled(True)

    @pyqtSlot()
    def clear_state(self):
        for angle_set in self.angle_sets:
            angle_set.reset()

    @pyqtSlot(int)
    def set_dark_mode(self, enable):
        labels = self.findChildren(QLabel)
        for label in labels:
            if enable:
                label.setStyleSheet("color: white")
            else:
                label.setStyleSheet("color: none")
