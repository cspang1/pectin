from enum import IntEnum, unique


@unique
class Angle(IntEnum):
    FROM_0_TO_44 = 0
    FROM_45_TO_89 = 1
    FROM_90_TO_134 = 2
    FROM_135_TO_179 = 3
    FROM_180_TO_224 = 4
    FROM_225_TO_269 = 5
    FROM_270_TO_314 = 6
    FROM_315_TO_359 = 7

    def to_string(angle):
        if angle is Angle.FROM_0_TO_44:
            return(" between 0° and 44°")
        elif angle is Angle.FROM_45_TO_89:
            return(" between 45° and 89°")
        elif angle is Angle.FROM_90_TO_134:
            return(" between 90° and 134°")
        elif angle is Angle.FROM_135_TO_179:
            return(" between 135° and 179°")
        elif angle is Angle.FROM_180_TO_224:
            return(" between 180° and 224°")
        elif angle is Angle.FROM_225_TO_269:
            return(" between 225° and 269°")
        elif angle is Angle.FROM_270_TO_314:
            return(" between 270° and 314°")
        elif angle is Angle.FROM_315_TO_359:
            return(" between 315° and 359°")
