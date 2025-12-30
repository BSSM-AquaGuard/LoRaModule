from enum import Enum

class LoraMode(Enum):
    SLEEP  = (1, 1)
    NORMAL = (0, 0)
    CONFIG = (1, 0)
    WAKEUP = (0, 1)