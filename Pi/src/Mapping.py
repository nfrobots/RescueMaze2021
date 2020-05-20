import copy

from Constants import *


class Position:
    """Position in 2 dimensional space"""
    def __init__(self, x, y):
        """Initializes Position

        Args:
            x (int): x coordinate
            y (int): y coordinate
        """
        self.x = x
        self.y = y

    def __eq__(self, other):
        """Compares two positions

        Args:
            other (Position): other position

        Returns:
            bool: True if x and y values are the same, otherwise False
        """
        return self.x == other.x and self.y == other.y

def distance(a, b):
    """Calculates manhattan distance between two positons

    Args:
        a (Position): first positon
        b (Position): second position

    Returns:
        int: manhattan distance between first and second position
    """
    return abs(a.x - b.x) + abs(a.y - b.y)


class _Vctr:
    """Internal class used to express position and rotation"""
    def __init__(self, x, y, rotation):
        """initzializes values

        Args:
            x (int): x coordinate
            y (int): y coordinate
            rotation (Contstants.Direction): rotation
        """
        self.x = x
        self.y = y
        self.rotation = rotation


MAZE_TILE_TEMPLATE =  {
    Direction.NORTH: False,
    Direction.SOUTH: False,
    Direction.WEST: False,
    Direction.EAST: False,
    VICTIM: False,
    RAMP: False,
    BLACK: False
}

class MazeTile:
    """Represents tile in maze. Supports custom attributes"""

    def __init__(self, template = MAZE_TILE_TEMPLATE):
        """Initializes MazeTile

        Args:
            template (dict, optional): dict containing attributes of MazeTile. Defaults to MAZE_TILE_TEMPLATE.
        """
        self._data = copy.deepcopy(template)

    def __getitem__(self, key):
        """Gets attribute from MazeTile

        Args:
            key (dict_key_type): attribute of MazeTile to get

        Raises:
            KeyError: if key ist not a attribute specified in MazeTile template

        Returns:
            Any: Value of specified attribute
        """
        if key in self._data:
            return self._data[key]
        else:
            raise KeyError("'{}' is not an attribute".format(key))

    def __setitem__(self, key, value):
        """Sets attribute of MazeTile

        Args:
            key (dict_key_type): attribute of MazeTile to set
            value (Any): value to set specified attribute to

        Raises:
            KeyError: if key is not a attribute specified in MazeTile template

        Returns:
            None
        """
        if key in self._data:
            self._data[key] = value
            return True
        else:
            raise KeyError("'{}' is not an attribute".format(key))

    def __repr__(self):
        """Returns representation string

        Returns:
            string: representation containing values of attributes
        """
        return "MazeTile with attributes:\n\t" + "\n\t".join("{}: {}".format(key, self._data[key]) for key in self._data)


class Map:
    """Map consisting of MazeTiles and a robot"""
    def __init__(self):
        """initializes Map with single default MazeTile and Robot facing north"""
        self.map = [[MazeTile()]]
        self.sizeX = 1
        self.sizeY = 1
        self.robot = _Vctr(0, 0, Direction.NORTH)

    def get(self, x, y):
        """Gets MazeTile at specified position

        Args:
            x (int): x coordinate of MazeTile
            y (int): y coordinate of MazeTile

        Returns:
            MazeTile / None: MazeTile at specified position, None if it does not exist
        """
        if x < self.sizeX and y < self.sizeY:
            return self.map[y][x]

    def set(self, x, y, value):
        """Sets MazeTile at specified position

        Args:
            x (int): x coordinate
            y (int): y coordinate
            value (MazeTile): MazeTile to set at specified posiotion

        Returns:
            bool: True if successfull, otherwise False
        """
        if x < self.sizeX and y < self.sizeY:
            self.map[y][x] = value
            return True
        else:
            return False

    def expand(self, direction):
        """Expands map in specified direction

        Args:
            direction (Constants.Direction): direction in which to expand the map
        """
        if direction == Direction.NORTH:
            newMap = [[MazeTile() for _ in range(self.sizeX)] for _ in range(self.sizeY + 1)]
            newSizeX = self.sizeX
            newSizeY = self.sizeY + 1
            xOffset = 0
            yOffset = 1
        elif direction == Direction.SOUTH:
            newMap = [[MazeTile() for _ in range(self.sizeX)] for _ in range(self.sizeY + 1)]
            newSizeX = self.sizeX
            newSizeY = self.sizeY + 1
            xOffset = 0
            yOffset = 0
        elif direction == Direction.WEST:
            newMap = [[MazeTile() for _ in range(self.sizeX + 1)] for _ in range(self.sizeY)]
            newSizeX = self.sizeX + 1
            newSizeY = self.sizeY
            xOffset = 1
            yOffset = 0
        elif direction == Direction.EAST:
            newMap = [[MazeTile() for _ in range(self.sizeX + 1)] for _ in range(self.sizeY)]
            newSizeX = self.sizeX + 1
            newSizeY = self.sizeY
            xOffset = 0
            yOffset = 0

        for y in range(self.sizeY):
            for x in range(self.sizeX):
                newMap[y + yOffset][x + xOffset] = self.map[y][x]

        self.map = newMap
        self.sizeX = newSizeX
        self.sizeY = newSizeY

def printShape(mp):
    for row in mp:
        for elem in row:
            print("x", end = ' ')
        print()