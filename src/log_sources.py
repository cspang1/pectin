from enum import IntEnum, unique


@unique
class LogSource(IntEnum):
    SYSTEM = 0
    EVENT = 1

    def get_text(source):
        if source is LogSource.SYSTEM:
            return "system"
        elif source is LogSource.EVENT:
            return "event"
