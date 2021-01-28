from enum import Enum
from datetime import datetime

I_PATH = None
i_file = None

R_PATH = None
R_CONSOLE = True
r_file = None

def clear():
    if I_PATH is not None:
        with open(I_PATH, "w"):
            pass
    if R_PATH is not None:
        with open(R_PATH, "w"):
            pass

def iLog(func):
    def wrapper(*args, **kwargs):
        global i_file
        if args[0].logging: # args[0] should be self
            if i_file is None:
                i_file = open(I_PATH, "w+")
            i_file.write("{};{};{}\n".format(func.__name__, args, kwargs))
        return func(*args, **kwargs)
    return wrapper


class LogLevel(Enum):
    DEBUG = 0
    INFO = 1
    WARNING = 2
    CRITICAL = 3


DISPLAY_LEVEL = LogLevel.DEBUG

def rLog(level, info):
    global r_file
    if r_file is None and R_PATH is not None:
        r_file = open(R_PATH, "w+")
    if level.value >= DISPLAY_LEVEL.value:
        time = datetime.now().strftime("%H:%M:%S")
        s = f"[{time}] [{level.name}] {info}"
        if R_PATH is not None:
            r_file.write(s)
        if R_CONSOLE:
            print(s)