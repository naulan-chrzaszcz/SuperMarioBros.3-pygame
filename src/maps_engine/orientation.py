from enum import Enum


class Orientation(Enum):
    """
        Enum for orientation of a tile
    """
    CORNER_LEFT_TOP = 1
    CORNER_LEFT_BOTTOM = 2
    BOTTOM = 3
    CORNER_RIGHT_BOTTOM = 4
    CORNER_RIGHT_TOP = 5
    TOP = 6
    FILL = 7
    LEFT = 8
    RIGHT = 9
