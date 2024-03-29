from enum import Enum

class Direction(int, Enum):
    NORTH = 0
    EAST = 1
    SOUTH = 2
    WEST = 3

class RelDirection(int, Enum):
    FORWARD = 0
    RIGHT = 1
    BACKWARD = 2
    LEFT = 3

KNOWN = "KNOWN"
VICTIM = "VICTIM"
RAMP = "RAMP"
BLACK = "BLACK"