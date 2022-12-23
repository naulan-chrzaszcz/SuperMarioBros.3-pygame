from enum import Enum


class TypeOfBlock(Enum):
    TOP = 1
    BOTTOM = 2
    LEFT = 3
    RIGHT = 4
    CORNER_LEFT_TOP = 5
    CORNER_RIGHT_TOP = 6
    CORNER_LEFT_BOTTOM = 7
    CORNER_RIGHT_BOTTOM = 8

    @staticmethod
    def is_corner_right_top(type_of_block) -> bool: return type_of_block == TypeOfBlock.CORNER_RIGHT_TOP
    @staticmethod
    def is_corner_right_bottom(type_of_block) -> bool: return type_of_block == TypeOfBlock.CORNER_RIGHT_BOTTOM
    @staticmethod
    def is_corner_left_bottom(type_of_block) -> bool: return type_of_block == TypeOfBlock.CORNER_LEFT_BOTTOM
    @staticmethod
    def is_left(type_of_block) -> bool: return type_of_block == TypeOfBlock.LEFT
    @staticmethod
    def is_bottom(type_of_block) -> bool: return type_of_block == TypeOfBlock.BOTTOM

    # TODO Find a better way, maybe is dirty
    @staticmethod
    def position_platform_on_sheet(type_of_block) -> tuple:
        if type_of_block == TypeOfBlock.TOP:
            return 1, 1
        elif type_of_block == TypeOfBlock.BOTTOM:
            return 7, 1
        elif type_of_block == TypeOfBlock.LEFT:
            return 8, 1
        elif type_of_block == TypeOfBlock.RIGHT:
            return 5, 1
        elif type_of_block == TypeOfBlock.CORNER_LEFT_TOP:
            return 0, 1
