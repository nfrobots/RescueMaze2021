import copy
import json

import Constants


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
    
    def __repr__(self):
        """Generates representation string for

        Returns:
            str: representation string for this position
        """
        return "<Position: x={}, y={}>".format(self.x, self.y)

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
    Constants.Direction.NORTH: False,
    Constants.Direction.SOUTH: False,
    Constants.Direction.WEST: False,
    Constants.Direction.EAST: False,
    Constants.VICTIM: False,
    Constants.RAMP: False,
    Constants.BLACK: False
}

class MazeTile:
    """Represents tile in maze. Supports custom attributes"""

    def __init__(self, template = MAZE_TILE_TEMPLATE, _cpy = copy.deepcopy):
        """Initializes MazeTile

        Args:
            template (dict, optional): dict containing attributes of MazeTile. Defaults to MAZE_TILE_TEMPLATE.
            _cpy (function, optional): function used to copy template. Defaults to copy.deepcopy.
        """
        self._data = _cpy(template)

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
            str: representation containing values of attributes
        """
        return "<MazeTile with attributes:\n\t" + "\n\t".join("{}: {}".format(key, self._data[key]) for key in self._data) + ">"


class Map:
    """Map consisting of MazeTiles and a robot"""
    def __init__(self, tile = MazeTile()):
        
        self.map = [[tile]]
        self.sizeX = 1
        self.sizeY = 1
        self.robot = _Vctr(0, 0, Constants.Direction.NORTH)

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

        Raises:
            TypeError: if direction is not of type Constants.Direction
        """
        if not isinstance(direction, Constants.Direction):
            raise TypeError("given argument is not of type Constants.RelDirection")

        if direction == Constants.Direction.NORTH:
            newMap = [[None for _ in range(self.sizeX)] for _ in range(self.sizeY + 1)]
            newMap[0] = [MazeTile() for x in range(self.sizeX)]
            newSizeX = self.sizeX
            newSizeY = self.sizeY + 1
            xOffset = 0
            yOffset = 1
        elif direction == Constants.Direction.SOUTH:
            newMap = [[None for _ in range(self.sizeX)] for _ in range(self.sizeY + 1)]
            newMap[self.sizeY] = [MazeTile() for x in range(self.sizeX)]
            newSizeX = self.sizeX
            newSizeY = self.sizeY + 1
            xOffset = 0
            yOffset = 0
        elif direction == Constants.Direction.WEST:
            newMap = [[None for _ in range(self.sizeX + 1)] for _ in range(self.sizeY)]
            for y in range(self.sizeY):
                newMap[y][0] = MazeTile()
            newSizeX = self.sizeX + 1
            newSizeY = self.sizeY
            xOffset = 1
            yOffset = 0
        elif direction == Constants.Direction.EAST:
            newMap = [[None for _ in range(self.sizeX + 1)] for _ in range(self.sizeY)]
            for y in range(self.sizeY):
                newMap[y][self.sizeX] = MazeTile()
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

    def relDirectionToDirection(self, relDirection):
        """Converts relative direction to absolute direction from robot perspective

        Args:
            relDirection (Constants.RelDirection): direction to convert

        Returns:
            Constants.Direction: absolute direction

        Raises:
            TypeError: if relDirection is not of type Constants.RelDirection
        """
        if not isinstance(relDirection, Constants.RelDirection):
            raise TypeError("given argument is not of type Constants.RelDirection")

        return Constants.Direction((self.robot.rotation.value + relDirection.value) % 4)

    def rotateRobot(self, relDirection):
        """Rotates robot by given relative rotation

        Args:
            relDirection (Constants.RelDirection): direction to rotate robot by
        
        Raises:
            TypeError: if relDirection is not of type Constants.RelDirection
        """
        if not isinstance(relDirection, Constants.RelDirection):
            raise TypeError("given argument is not of type Constants.RelDirection")

        self.robot.rotation = self.relDirectionToDirection(relDirection)

    def getRobotPosition(self):
        """Gets robot position

        Returns:
            Position: position of robot
        """
        return Position(self.robot.x, self.robot.y)

    def getRobotDirection(self):
        """Gets robot direction

        Returns:
            Constants.Direction: direction of robot
        """
        return self.robot.rotation

    def save(self, path):
        obj = {
            "sizeX": self.sizeX,
            "sizeY": self.sizeY,
            "robotX": self.robot.x,
            "robotY": self.robot.y,
            "robotDirection": str(self.robot.rotation),
            "Map": {}
        }
        for y in range(self.sizeY):
            for x in range(self.sizeX):
                obj["Map"][str(x) + "," + str(y)] = {}
                for key in self.map[y][x]._data:
                    obj["Map"][str(x) + "," + str(y)][str(key)] = self.map[y][x][key]

        with open(path, 'w') as f:
            json.dump(obj, f)

def printShape(mp):
    for row in mp:
        for _ in row:
            print("x", end = ' ')
        print()