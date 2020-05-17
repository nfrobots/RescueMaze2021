from Constants import *

MAZE_TILE_TEMPLATE =  {
    NORTH: False,
    SOUTH: False,
    WEST: False,
    EAST: False,
    "VICTIM": False,
    "RAMP": False,
    "BLACK": False
}


class MazeTile:
    """Represents tile in maze. Supports custom attributes"""

    def __init__(self, template = MAZE_TILE_TEMPLATE):
        """Initializes MazeTile

        Args:
            template (dict, optional): dict containing attributes of MazeTile. Defaults to MAZE_TILE_TEMPLATE.
        """
        self._data = template

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