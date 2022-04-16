import copy
import json
import numpy as np
from enum import Enum
from queue import Queue
import heapq

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

    def __getitem__(self, key):
        if key == 0:
            return self.x
        elif key == 1:
            return self.y
        else:
            raise KeyError(f"cannot get element {key} of Position")

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
    def __init__(self, x=0, y=0, rotation=Direction.NORTH):
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
        return "<MazeTile: " + "\t".join("{}: {}".format(key, self._data[key]) for key in self._data) + ">"

    def __eq__(self, other):
        return isinstance(other, MazeTile) and self._data == other._data


class SearchFilterAttribute(Enum):
    ANY = "ANY"

def create_any_tile():
    return MazeTile({key: SearchFilterAttribute.ANY for key in MAZE_TILE_TEMPLATE})

class Map:
    """Map consisting of MazeTiles and a robot"""
    def __init__(self, Tile=MazeTile, sizeX=1, sizeY=1, logging=False, initialize=True, neighbours=False, path_pre_expand=False):
        """Constructor

        Args:
            Tile: Class representing a tile
            sizeX (int): initial size of the Map in x direction
            sizeY (int): initial size of the Map in y direction
            logging (bool): whether to log activity concerning the map
            initialize (bool): whether to initialize the initial tiles specified by sizeX and sizeY. Be careful when setting this to False.
            neighbours (bool): whether changes on tiles may effect neightbour tiles.
            path_pre_expand (bool): whether to expand the map for tiles that exist, but are not yet known
        """
        self.map = np.zeros((sizeY,sizeX), MazeTile)
        self.sizeX = sizeX
        self.sizeY = sizeY
        self.offsetX = 0
        self.offsetY = 0
        if initialize:
            for x in range(sizeX):
                for y in range(sizeY):
                    self.map[y,x] = Tile()

        self.robot = _Vctr(0, 0, Constants.Direction.NORTH)
        self.logging = logging
        self.apply_to_neighbours = neighbours
        self.path_pre_expand = path_pre_expand

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

    def getAtRobot(self) -> MazeTile:
        return self.get(self.robot.x, self.robot.y)

    def getAtAbsoloute(self, x, y):
        """gets tile at absoloute position (0,0 is the start position -> x and y can be negative)"""
        return self.get(x + self.offsetX, y + self.offsetY)

    def getAtOffset(self, x, y, direction):
        offset = self.directionToOffset(direction)
        return self.get(x + offset[0], y + offset[1])

    @Logger.iLog
    def set(self, x: int, y: int, value: MazeTile, expand=True, _path_pre_expand=None):
        """[[LOGGED]] Sets MazeTile at specified position, may expands until position reached. Does not set neighbours

        Args:
            x (int): x coordinate
            y (int): y coordinate
            value (MazeTile): MazeTile to set at specified posiotion
            expand (bool): weather to expand

        Returns:
            tuple of the position where the tile was set e.g. (2, 4) or
            None if the tile could not be set
        """
        prevOffsetX = self.offsetX
        prevOffsetY = self.offsetY

        if expand:
            if x >= self.sizeX:
                self._expand(Constants.Direction.EAST, x - self.sizeX + 1)
            elif x < 0:
                self._expand(Constants.Direction.WEST, -x)

            if y >= self.sizeY:
                self._expand(Constants.Direction.SOUTH, y - self.sizeY + 1)
            elif y < 0:
                self._expand(Constants.Direction.NORTH, -y)

        if _path_pre_expand == None and self.path_pre_expand:
            self._perform_path_pre_expand(x, y, value)
        elif isinstance(_path_pre_expand, Constants.Direction):
            self._perform_path_pre_expand(x, y, value, directionConstraint=_path_pre_expand)

        x = x + self.offsetX - prevOffsetX
        y = y + self.offsetY - prevOffsetY

        if(x >= 0 and x < self.sizeX and y >= 0 and y < self.sizeY):
            self.map[y, x] = value
            return (x, y)

        return None

    def _perform_path_pre_expand(self, x: int, y: int, tile: MazeTile, directionConstraint=None):
        """Pre-expands the maze, if there exists a way outside of it. Constraintable to a singel direciton."""
        if tile[Constants.Direction.NORTH] == False and y == 0 and (directionConstraint == None or directionConstraint == Constants.Direction.NORTH):
            self._expand(Constants.Direction.NORTH)
        if tile[Constants.Direction.SOUTH] == False and y == self.sizeY - 1 and (directionConstraint == None or directionConstraint == Constants.Direction.SOUTH):
            self._expand(Constants.Direction.SOUTH)
        if tile[Constants.Direction.EAST] == False and x == self.sizeX - 1 and (directionConstraint == None or directionConstraint == Constants.Direction.EAST):
            self._expand(Constants.Direction.EAST)
        if tile[Constants.Direction.WEST] == False and x == 0 and (directionConstraint == None or directionConstraint == Constants.Direction.WEST):
            self._expand(Constants.Direction.WEST)

    def setAtRobot(self, tile: MazeTile):
        for attribute in tile._data:
            self.setAttribute(self.robot.x, self.robot.y, attribute, tile[attribute])

    def setAttribute(self, x, y, attribute, value, expand=True, _neighbours=None, _path_pre_expand=None):
        """Sets attribute of tile at specified posiotion. Sets neighbours if specified in constructor of Map

        Args:
            x (int): x position
            y (int): y position
            attribute (Any): [description]
            value (Any): [description]
            expand (bool): weather to expand in order to set the tile
        """
        tile = self.get(x, y)
        if tile == None:
            tile = MazeTile()
        tile[attribute] = value

        if _path_pre_expand == None and isinstance(attribute, Constants.Direction): # if _path_pre_expand is not specified, allow the set method to only ppe in the specified direction
            _path_pre_expand = attribute
        elif not isinstance(attribute, Constants.Direction): # dont allow ppe if the attribute is not a wall
            _path_pre_expand = False

        tilePosition = self.set(x, y, tile, expand, _path_pre_expand)
        if isinstance(attribute, Constants.Direction) and self.apply_to_neighbours and _neighbours == None \
            and tilePosition:
            self._setNeighbourWall(tilePosition[0], tilePosition[1], attribute, value)

    def _setNeighbourWall(self, x, y, direction, value):
        offset = self.directionToOffset(direction)
        self.setAttribute(x + offset[0], y + offset[1], self.inverseDirection(direction), value, expand=False, _neighbours=False, _path_pre_expand=False)

    def setAttributeAtRobot(self, attribute, value):
        robotPosition = self.getRobotPosition()
        self.setAttribute(robotPosition.x, robotPosition.y, attribute, value)
        
    def setAttributeAtRobotRelDirection(self, relDirection, attribute, value, expand=True):
        """Sets a single tile attribute of a tile in a specified RelDirection to a specified value."""
        robotPosition = self.getRobotPosition()
        offset = self.relDirectionToOffset(relDirection)
        self.setAttribute(robotPosition.x + offset[0], robotPosition.y + offset[1], attribute, value, expand)

    def _expand(self, direction, n=1):
        """Expands map in specified direction

        Args:
            direction (Constants.Direction): direction in which to expand the map
            n (int): number of tiles to expand

        Raises:
            TypeError: if direction is not of type Constants.Direction
        """
        if not isinstance(direction, Constants.Direction):
            raise TypeError("given argument is not of type Constants.RelDirection")

        # prevent possibly unbount warning
        newMap = None
        yOffset = 0
        xOffset = 0
        newSizeX = self.sizeX
        newSizeY = self.sizeY

        if direction == Constants.Direction.NORTH:
            newSizeY += n
            newMap = np.zeros((newSizeY, newSizeX), MazeTile)
            for y in range(n):
                for x in range(self.sizeX):
                    newMap[y, x] = MazeTile()
            yOffset = n
        elif direction == Constants.Direction.SOUTH:
            newSizeY += n
            newMap = np.zeros((newSizeY, newSizeX), MazeTile)
            for y in range(n):
                for x in range(self.sizeX):
                    newMap[self.sizeY + y, x] = MazeTile()
        elif direction == Constants.Direction.WEST:
            newSizeX += n
            newMap = np.zeros((newSizeY, newSizeX), MazeTile)
            for x in range(n):
                for y in range(self.sizeY):
                    newMap[y, x] = MazeTile()
            xOffset = n
        elif direction == Constants.Direction.EAST:
            newSizeX += n
            newMap = np.zeros((newSizeY, newSizeX), MazeTile)
            for x in range(n):
                for y in range(self.sizeY):
                    newMap[y, self.sizeX + x] = MazeTile()

        for y in range(self.sizeY):
            for x in range(self.sizeX):
                newMap[y + yOffset, x + xOffset] = self.map[y, x]

        self.map = newMap
        self.sizeX = newSizeX
        self.sizeY = newSizeY

        self.robot.x += xOffset
        self.robot.y += yOffset

        self.offsetX += xOffset
        self.offsetY += yOffset

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

    def directionToRelDirection(self, direction):
        if not isinstance(direction, Constants.Direction):
            raise TypeError("given argument is not of type Constants.Direction")
        return Constants.RelDirection((direction.value - self.robot.direction.value) % 4)

    def directionToOffset(self, direction):
        if direction == Constants.Direction.NORTH:
            return 0, -1
        elif direction == Constants.Direction.SOUTH:
            return 0, 1
        elif direction == Constants.Direction.WEST:
            return -1, 0
        elif direction == Constants.Direction.EAST:
            return 1, 0

    def relDirectionToOffset(self, relDirection):
        """Converts relative direction to x and y offset"""
        return self.directionToOffset(self.relDirectionToDirection(relDirection))

    def offsetToDirection(self, offset):
        if offset == (0, -1):
            return Constants.Direction.NORTH
        elif offset == (0, 1):
            return Constants.Direction.SOUTH
        elif offset == (-1, 0):
            return Constants.Direction.WEST
        elif offset == (1, 0):
            return Constants.Direction.EAST

    def inverseDirection(self, direction):
        return Direction((direction.value + 2) % 4)

    def getRobotPosition(self):
        """Gets robot position

        Returns:
            Position: position of robot
        """
        return Position(self.robot.x, self.robot.y)

    def getRobotAbsolutePosition(self):
        return Position(self.robot.x - self.offsetX, self.robot.y - self.offsetY)

    def getRobotDirection(self):
        """Gets robot direction

        Returns:
            Constants.Direction: direction of robot
        """
        return self.robot.direction

    def robotIsAtStart(self):
        absoloutePosition = self.getRobotAbsolutePosition()
        return absoloutePosition.x == 0 and absoloutePosition.y == 0

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

    def canDrive(self, x, y, direction):
        current = self.get(x, y)
        if current == None or current[direction]:
            return False
        offset =  self.directionToOffset(direction)
        destination = self.get(x + offset[0], y + offset[1])
        if destination != None and destination[Constants.BLACK]:
            return False
        return True

        
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
        return Map._restore(raw_data)

    @staticmethod
    def _restore(raw_data):
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

    @Logger.iLog
    def findPath(self, startX, startY, endX, endY):
        class _ANode:
            def __init__(self, x, y, endX, endY, parent=None):
                self.x = x
                self.y = y
                self.parent = parent
                if parent is not None:
                    self.g_cost = parent.g_cost + 1 # cost to get there
                else:
                    self.g_cost = 0
                self.h_cost = abs(x - endX) + abs(y - endY) # apprx to get to the end
                self.f_cost = self.g_cost + self.h_cost
            
            def __repr__(self):
                return "ANode at ({},{})".format(self.x, self.y)

            def __lt__(self, other): # less than <
                return self.f_cost < other.f_cost or (self.f_cost == other.f_cost and self.g_cost < other.g_cost)

        class _ANodeHandler:
            def __init__(self):
                self._dict = {}
                self._heap = []

            def add(self, node):
                self._dict[(node.x, node.y)] = node
                heapq.heappush(self._heap, node)

            def pop(self):
                node = heapq.heappop(self._heap)
                del self._dict[(node.x, node.y)]
                return node

            def __contains__(self, node):
                """ONLY CHECK COORDINATES"""
                return (node.x, node.y) in self._dict

            def get(self, x, y):
                return self._dict[(x, y)]

            def replace(self, node):
                """replaces node at same position"""
                self._dict[(node.x, node.y)].g_cost = node.g_cost
                self._dict[(node.x, node.y)].f_cost = node.f_cost
                self._dict[(node.x, node.y)].parent = node.parent

            def __len__(self):
                return len(self._heap)
        
        openList = _ANodeHandler() #heapq binary tree
        openList.add(_ANode(startX, startY, endX, endY))
        closedList = {} # already visited nodes

        while True:
            if len(openList) == 0: # no possible path
                return []

            current = openList.pop()
            closedList[(current.x, current.y)] = True

            neighbours = []
            for direction in Constants.Direction:
                if self.canDrive(current.x, current.y, direction) and self.getAtOffset(current.x, current.y, direction) != None:#
                    offset = self.directionToOffset(direction)
                    destination_coords = current.x + offset[0], current.y + offset[1]
                    if destination_coords in closedList:
                        continue
                    neighbours.append(_ANode(*destination_coords, endX, endY, current))

            for neighbour in neighbours:
                if neighbour.x == endX and neighbour.y == endY:
                    ret = []
                    node = neighbour
                    while node is not None:
                        ret.append(Position(node.x, node.y))
                        node = node.parent
                    ret.reverse()
                    return ret

                already_set = False

                if neighbour in openList:
                    equiv = openList.get(neighbour.x, neighbour.y)
                    if neighbour.f_cost < equiv.f_cost or (neighbour.f_cost == equiv.f_cost and neighbour.g_cost < equiv.g_cost):
                        openList.replace(neighbour)
                    already_set = True

                if not already_set:
                    openList.add(neighbour)

    def pathToDirections(self, path):
        return [self.offsetToDirection((path[i].x - path[i - 1].x, path[i].y - path[i - 1].y)) for i in range(1, len(path))]


    def search(self, origin: Position, tile: MazeTile):
        """Searches for MazeTile. Attribute can be set to SearchFilterAttribute.ANY, if it is not supposed to be checked

            Returns:
                Tuple[MazeTile, int, int]: MazeTile that matched, x coordinate, y coordinate repectively
        """
        check_attributes = [attribute for attribute in tile._data if tile._data[attribute] != SearchFilterAttribute.ANY]
        queue = Queue() # contains (Tile, x, y)
        queue.put((self.get(origin.x, origin.y), origin.x, origin.y))
        checked_tiles = {} # key is (x, y)
        while True:
            if queue.qsize() == 0:
                return None, None, None
            qelem = queue.get()
            tl = qelem[0]
            matches = True
            for attribute in check_attributes:
                if tl[attribute] != tile[attribute]:
                    matches = False
                    break
            if matches:
                return qelem
            checked_tiles[qelem[1:]] = True
            next_directions = [direction for direction in Constants.Direction if not tl[direction]]
            for direction in next_directions:
                offset = self.directionToOffset(direction)
                destination_coords = (qelem[1] + offset[0], qelem[2] + offset[1])
                if destination_coords in checked_tiles:
                    continue
                destination = self.get(*destination_coords)
                if self.canDrive(qelem[1], qelem[2], direction):
                    queue.put((destination, *destination_coords))
                    checked_tiles[destination_coords] = True
