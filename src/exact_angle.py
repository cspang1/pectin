from PyQt5.QtGui import (
    QFont,
    QIcon,
    QPainter,
    QPen
)
from PyQt5.QtCore import (
    QEasingCurve,
    QParallelAnimationGroup,
    QPoint,
    QPropertyAnimation,
    QSize,
    Qt,
    pyqtSignal,
    pyqtSlot
)
from PyQt5.QtWidgets import (
    QGraphicsOpacityEffect,
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


class DummyButton(QPushButton):

    def __init__(self, value, max, parent=None):
        super().__init__(str(value), parent)
        self.setFont(QFont("Consolas", 16, 3))
        self.setFixedSize(100, 50)
        self.done = False
        self.index = value
        self.max = max
        self.effect = QGraphicsOpacityEffect()
        self.setGraphicsEffect(self.effect)
        self.fade_anim = QPropertyAnimation(self.effect, b"opacity")
        self.effect.setOpacity(1)
        self.fade_anim.setDuration(150)
        self.fade_anim.setStartValue(0)
        self.fade_anim.setEndValue(1)
        self.fade_anim.setEasingCurve(QEasingCurve.InQuad)
        self.fade_anim.finished.connect(self.finish)

    def finish(self):
        self.done = True

    def moveEvent(self, event):
        super().moveEvent(event)
        if self.pos().y() < 110 + self.max * 50 and not self.done:
            self.fade_anim.start()


class AngleButton(QPushButton):
    pressed = pyqtSignal(int)

    def __init__(self, value, parent=None):
        super().__init__(str(value), parent)
        self.setFont(QFont("Consolas", 16, 3))
        self.setFixedSize(100, 50)
        self.index = value
        self.activated = False
        self.clicked.connect(lambda: self.pressed.emit(self.index))
        self.activate(False)
        self.setup_fade()

    def moveEvent(self, event):
        super().moveEvent(event)
        if self.pos().y() < 55 and not self.faded:
            self.faded = True
            self.fade_anim.start()

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

    def disable(self, state):
        if state:
            self.setEnabled(False)
        else:
            self.setEnabled(True)
            self.activate(self.activated)
            self.setup_fade()

    def setup_fade(self):
        self.effect = QGraphicsOpacityEffect()
        self.setGraphicsEffect(self.effect)
        self.effect.setOpacity(1)
        self.fade_anim = QPropertyAnimation(self.effect, b"opacity")
        self.fade_anim.setDuration(80)
        self.fade_anim.setStartValue(1)
        self.fade_anim.setEndValue(0)
        self.fade_anim.setEasingCurve(QEasingCurve.OutQuad)
        self.faded = False


class AngleSet(QWidget):
    acted = pyqtSignal(int, BtnSource)

    def __init__(self, source, parent=None):
        super().__init__(parent)
        self.source = source
        self.active = 0
        self.is_limited = False
        self.limit = 4 if self.source is BtnSource.HUNDREDS else 10
        self.setMinimumSize(100, 105 + self.limit * 50)
        self.anim_gp = QParallelAnimationGroup()
        self.anim_gp.finished.connect(self.post_animation)
        y_offset = 55
        self.digits = []
        self.digits_pos = [idx for idx in range(self.limit)]
        for digit in range(self.limit):
            tmp_btn = AngleButton(digit, self)
            tmp_btn.move(0, y_offset)
            y_offset = y_offset + 50
            tmp_btn.pressed.connect(self.switch_active)
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
        duration = diff * 50 * 1.5

        self.loopers = []
        y_offset = 55 + self.limit * 50
        for position in positions:
            digit = self.digits[position]
            new_pos = positions.index(digit.index)
            cur_pos = self.digits_pos.index(digit.index)
            if new_pos > cur_pos:
                dummy = DummyButton(digit.index, self.limit, self)
                dummy.move(0, y_offset)
                y_offset = y_offset + 50
                dummy.show()
                self.loopers.append(dummy)
                anim = QPropertyAnimation(dummy, b"pos", dummy)
                anim.setStartValue(dummy.pos())
                anim.setEndValue(
                    QPoint(
                        dummy.pos().x(), dummy.pos().y() - diff * 50
                    )
                )
                self.anims.append(anim)

            anim = QPropertyAnimation(digit, b"pos", digit)
            anim.setStartValue(digit.pos())
            anim.setEndValue(
                QPoint(
                    digit.pos().x(), digit.pos().y() - diff * 50
                )
            )
            self.anims.append(anim)
            digit.disable(True)

        for anim in self.anims:
            anim.setDuration(duration)
            anim.setEasingCurve(QEasingCurve.OutQuad)
            self.anim_gp.addAnimation(anim)
        self.anim_gp.start()

        self.digits_pos = positions

    @pyqtSlot()
    def post_animation(self):
        for looper in self.loopers:
            self.digits[looper.index].move(looper.pos())
            looper.setParent(None)
        for digit in self.digits:
            digit.disable(False)
        self.parent().rectify()

    def reset(self):
        for digit in self.digits:
            digit.activate(False)
        self.active = -1
        self.anim_set(0)


class ExactAngle(QWidget):
    angle_event = pyqtSignal(int)
    btn_event = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(450, 605)
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

        self.go_btn = QPushButton(QIcon(":/icons/add.png"), "", self)
        self.go_btn.setEnabled(False)
        self.go_btn.move(385, 55)
        self.go_btn.setFixedSize(50, 50)
        self.go_btn.setIconSize(QSize(50, 50))
        self.go_btn.pressed.connect(lambda: self.log_angle(True))

        overlay = Overlay(self)
        overlay.setGeometry(self.geometry())

    @pyqtSlot(bool)
    def log_angle(self, clear):
        if self.is_valid():
            self.angle_event.emit(self.calc_angle())
        self.go_btn.setEnabled(False)
        if clear:
            self.clear_state()

    @pyqtSlot(int, BtnSource)
    def digit_pressed(self, value, source):
        self.btn_event.emit()
        self.selected[source] = True, value
        if all(val[0] is True for val in self.selected.values()):
            self.go_btn.setEnabled(True)

    def rectify(self):
        for angle_set in self.angle_sets:
            for digit in angle_set.digits:
                digit.setEnabled(True)
        if self.hundreds.active == 3:
            for digit in self.tens.digits[7:]:
                digit.setEnabled(False)
            if self.tens.active == 6:
                for digit in self.ones.digits[1:]:
                    digit.setEnabled(False)
            if self.ones.active > 0:
                self.tens.digits[6].setEnabled(False)
        if self.tens.active > 6:
            self.hundreds.digits[3].setEnabled(False)
        if self.tens.active == 6 and self.ones.active > 0:
            self.hundreds.digits[3].setEnabled(False)

    @pyqtSlot()
    def clear_state(self):
        for angle_set in self.angle_sets:
            angle_set.reset()
        for key in self.selected:
            self.selected[key] = False, None

    def has_valid(self):
        return any(val[0] is True for val in self.selected.values())

    def is_valid(self):
        return all(val[0] is True for val in self.selected.values())

    def calc_angle(self):
        return self.selected[BtnSource.HUNDREDS][1] * 100 + \
            self.selected[BtnSource.TENS][1] * 10 + \
            self.selected[BtnSource.ONES][1]

    @pyqtSlot(int)
    def set_dark_mode(self, enable):
        labels = self.findChildren(QLabel)
        for label in labels:
            if enable:
                label.setStyleSheet("color: white")
            else:
                label.setStyleSheet("color: none")
