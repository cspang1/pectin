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
