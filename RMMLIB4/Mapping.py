import copy
import json
import numpy as np

from RMMLIB4 import Constants, Logger
from RMMLIB4.Constants import * # needed for eval() call

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
        self.direction = rotation


MAZE_TILE_TEMPLATE =  {
    Constants.KNOWN: False,             # tile is known
    Constants.Direction.NORTH: False,   # north wall existing
    Constants.Direction.SOUTH: False,   # south wall existing
    Constants.Direction.WEST: False,    # west wall existing
    Constants.Direction.EAST: False,    # east wall existing
    Constants.RAMP: False,              # ramp existing
    Constants.VICTIM: False,            # victim existing
    Constants.BLACK: False              # black tile existing
}

class MazeTile:
    """Represents tile in maze"""

    def __init__(self, template = MAZE_TILE_TEMPLATE):
        """Initializes MazeTile

        Args:
            template (dict, optional): dict containing attributes of MazeTile. Defaults to MAZE_TILE_TEMPLATE.
        """
        self._data = template.copy()

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
    def __init__(self, tile = MazeTile, sizeX=1, sizeY=1, initialize=True):
        self.map = np.zeros((sizeY,sizeX), MazeTile)
        self.sizeX = sizeX
        self.sizeY = sizeY
        if initialize:
            for x in range(sizeX):
                for y in range(sizeY):
                    self.map[y,x] = tile()

        self.robot = _Vctr(0, 0, Constants.Direction.NORTH)

    def get(self, x, y):
        """Gets MazeTile at specified position

        Args:
            x (int): x coordinate of MazeTile
            y (int): y coordinate of MazeTile

        Returns:
            MazeTile / None: MazeTile at specified position, None if it does not exist
        """
        if x < self.sizeX and y < self.sizeY and x >= 0 and y >= 0:
            return self.map[y, x]

    def getAtRobot(self):
        return self.get(self.robot.x, self.robot.y)

    def set(self, x, y, value):
        """Sets MazeTile at specified position

        Args:
            x (int): x coordinate
            y (int): y coordinate
            value (MazeTile): MazeTile to set at specified posiotion

        Returns:
            bool: True if successfull, otherwise False
        """
        if x < self.sizeX and y < self.sizeY and x >= 0 and y >= 0:
            self.map[y, x] = value
            return True
        else:
            return False

    @Logger.iLog
    def setAttribute(self, x, y, attribute, value):
        if x < self.sizeX and y < self.sizeY and x >= 0 and y >= 0:
            self.map[y, x][attribute] = value
            return True
        else:
            return False

    def setAttributeAtRobot(self, attribute, value):
        robotPosition = self.getRobotPosition()
        self.setAttribute(robotPosition.x, robotPosition.y, attribute, value)

    def _expand(self, direction):
        """Expands map in specified direction

        Args:
            direction (Constants.Direction): direction in which to expand the map

        Raises:
            TypeError: if direction is not of type Constants.Direction
        """
        if not isinstance(direction, Constants.Direction):
            raise TypeError("given argument is not of type Constants.RelDirection")

        # prevent possibly unbount warning
        newMap = None
        yOffset = None
        xOffset = None
        newSizeX = None
        newSizeY = None

        if direction == Constants.Direction.NORTH:
            newMap = np.zeros((self.sizeY + 1, self.sizeX), MazeTile)
            for x in range(self.sizeX):
                newMap[0, x] = MazeTile()
            newSizeX = self.sizeX
            newSizeY = self.sizeY + 1
            xOffset = 0
            yOffset = 1
        elif direction == Constants.Direction.SOUTH:
            newMap = np.zeros((self.sizeY + 1, self.sizeX), MazeTile)
            for x in range(self.sizeX):
                newMap[self.sizeY, x] = MazeTile()
            newSizeX = self.sizeX
            newSizeY = self.sizeY + 1
            xOffset = 0
            yOffset = 0
        elif direction == Constants.Direction.WEST:
            newMap = np.zeros((self.sizeY, self.sizeX + 1), MazeTile)
            for y in range(self.sizeY):
                newMap[y][0] = MazeTile()
            newSizeX = self.sizeX + 1
            newSizeY = self.sizeY
            xOffset = 1
            yOffset = 0
        elif direction == Constants.Direction.EAST:
            newMap = np.zeros((self.sizeY, self.sizeX + 1), MazeTile)
            for y in range(self.sizeY):
                newMap[y, self.sizeX] = MazeTile()
            newSizeX = self.sizeX + 1
            newSizeY = self.sizeY
            xOffset = 0
            yOffset = 0

        for y in range(self.sizeY):
            for x in range(self.sizeX):
                newMap[y + yOffset, x + xOffset] = self.map[y, x]

        self.map = newMap
        self.sizeX = newSizeX
        self.sizeY = newSizeY

        self.robot.x += xOffset
        self.robot.y += yOffset

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

        return Constants.Direction((self.robot.direction.value + relDirection.value) % 4)

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
        return self.robot.direction

    @Logger.iLog
    def rotateRobot(self, relDirection):
        """Rotates robot by given relative rotation

        Args:
            relDirection (Constants.RelDirection): direction to rotate robot by
        
        Raises:
            TypeError: if relDirection is not of type Constants.RelDirection
        """
        if not isinstance(relDirection, Constants.RelDirection):
            raise TypeError("given argument is not of type Constants.RelDirection")

        self.robot.direction = self.relDirectionToDirection(relDirection)

    @Logger.iLog
    def move(self):
        """moves robot forward"""
        if self.robot.direction == Constants.Direction.NORTH:
            if self.robot.y < 1:
                self._expand(Constants.Direction.NORTH)
            self.robot.y -= 1
        elif self.robot.direction == Constants.Direction.SOUTH:
            if self.robot.y > self.sizeY - 2:
                self._expand(Constants.Direction.SOUTH)
            self.robot.y += 1
        elif self.robot.direction == Constants.Direction.WEST:
            if self.robot.x < 1:
                self._expand(Constants.Direction.WEST)
            self.robot.x -= 1
        elif self.robot.direction == Constants.Direction.EAST:
            if self.robot.x > self.sizeX - 2:
                self._expand(Constants.Direction.EAST)
            self.robot.x += 1

    def driveRobot(self, relDirection):
        """rotates and moves robot in specified direction

        Args:
            relDirection (Constants.RelDirection): relative direction to drive to
        """
        if relDirection != Constants.RelDirection.FORWARD:
            self.rotateRobot(relDirection)
        self.move()

        
    def _store(self):
        """Returns map information as python dict."""
        obj = {
            "sizeX": self.sizeX,
            "sizeY": self.sizeY,
            "robotX": self.robot.x,
            "robotY": self.robot.y,
            "robotDirection": str(self.robot.direction),
            "Map": {}
        }
        for y in range(self.sizeY):
            for x in range(self.sizeX):
                obj["Map"][str(x) + "," + str(y)] = {}
                for key in self.map[y, x]._data:
                    obj["Map"][str(x) + "," + str(y)][str(key)] = self.map[y, x][key]
        return obj

    def save(self, path):
        """saves map to json file

        Args:
            path (str): path to json file
        """
        with open(path, 'w+') as f:
            json.dump(self._store(), f)

    def saves(self):
        """Returns json string containing map information."""
        return json.dumps(self._store())

    @staticmethod
    def open(path):
        with open(path, 'r') as f:
            raw_data = json.load(f)

        newMap = Map(sizeX=raw_data['sizeX'], sizeY=raw_data['sizeY'])
        newMap.sizeX = raw_data['sizeX']
        newMap.sizeY = raw_data['sizeY']
        newMap.robot.x = raw_data['robotX']
        newMap.robot.y = raw_data['robotY']
        newMap.robot.direction = eval(raw_data['robotDirection'])
        for y in range(newMap.sizeY):
            for x in range(newMap.sizeX):
                for key, value in raw_data["Map"][f"{x},{y}"].items():
                    #TODO FILL IN THIS STUFF
                    newMap.map[y, x]._data[eval(key)] = value

        return newMap

    def findPath(self, startX, startY, endX, endY):
        class _ANode:
            def __init__(self, x, y, endX, endY, parent=None):
                self.x = x
                self.y = y
                self.parent = parent
                if parent is not None:
                    self.gCost = parent.gCost + 1
                else:
                    self.gCost = 0
                self.hCost = abs(x - endX) + abs(y - endY)
                self.f_cost = self.gCost + self.hCost
            
            def __repr__(self):
                return "ANode at ({},{})".format(self.x, self.y)
        
        openList = [_ANode(startX, startY, endX, endY)]
        closedList = [] # already visited nodes

        while True:
            if not len(openList) > 0: # no possible path
                return []
            else:
                current = openList[0]

            for node in openList:
                if node.f_cost < current.f_cost or (node.f_cost == current.f_cost and node.gCost < current.gCost):
                    current = node

            openList.remove(current)
            closedList.append(current)

            neighbors = []
            if self.get(current.x, current.y)[Constants.Direction.NORTH] is False and current.y - 1 >= 0 and self.get(current.x, current.y - 1)[Constants.BLACK] is False:
                neighbors.append(_ANode(current.x, current.y - 1, endX, endY, current))
            if self.get(current.x, current.y)[Constants.Direction.SOUTH] is False and current.y + 1 < self.sizeY and self.get(current.x, current.y + 1)[Constants.BLACK] is False:
                neighbors.append(_ANode(current.x, current.y + 1, endX, endY, current))
            if self.get(current.x, current.y)[Constants.Direction.WEST] is False and current.x - 1 >= 0 and self.get(current.x - 1, current.y)[Constants.BLACK] is False:
                neighbors.append(_ANode(current.x - 1, current.y, endX, endY, current))
            if self.get(current.x, current.y)[Constants.Direction.EAST] is False and current.x + 1 < self.sizeX and self.get(current.x + 1, current.y)[Constants.BLACK] is False:
                neighbors.append(_ANode(current.x + 1, current.y, endX, endY, current))

            for neighbour in neighbors:
                alreadyVisited = False

                if neighbour.x == endX and neighbour.y == endY:
                    ret = [neighbour]
                    node = neighbour.parent
                    while node is not None:
                        ret.append(node)
                        node = node.parent
                    ret.reverse()
                    return ret

                for closedNode in closedList:
                    if neighbour.x == closedNode.x and neighbour.y == closedNode.y:
                        alreadyVisited = True
                        break

                for openNode in openList:
                    if neighbour.x == openNode.x and neighbour.y == openNode.y:
                        if neighbour.f_cost < openNode.f_cost or (neighbour.f_cost == openNode.f_cost and neighbour.gCost < openNode.gCost):
                            openList.remove(openNode)
                            openList.append(neighbour)
                        alreadyVisited = True
                        break

                if not alreadyVisited:
                    openList.append(neighbour)