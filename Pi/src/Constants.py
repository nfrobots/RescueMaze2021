from enum import Enum

class Direction(Enum):
    NORTH = 0
    WEST = 1
    SOUTH = 2
    EAST = 3

class RelDirection(Enum):
    FORWARD = 0
    RIGHT = 1
    BACKWARD = 2
    LEFT = 3

VICTIM = "VICTIM"
RAMP = "RAMP"
BLACK = "BLACK"