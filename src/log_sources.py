from enum import IntEnum, unique


@unique
class LogSource(IntEnum):
    SYSTEM = 0
    EVENT = 1
