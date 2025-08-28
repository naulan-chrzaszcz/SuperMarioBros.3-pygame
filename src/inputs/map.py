from typing import Dict

from pygame import Vector2, transform, Surface
from pygame.sprite import LayeredUpdates

from ..sprite_animation import SpriteAnimation
from ..tile import Tile


class Map:
    TILE_COORD_SEPARATOR = ","
    TILE_FRAMES_SEPARATOR = "+"
    TILE_ROTATION_SEPARATOR = "&"

    def __init__(
        self, sheet: Surface, sheet_metadata: Dict[str, str], map_data: dict
    ):
        self.sprites = LayeredUpdates()
        self.width = 0
        self.height = 0

        column = 0
        row = 0
        for row in range(len(map_data["tiles"])):
            for column, tile in enumerate(map_data["tiles"][row]):
                x, y = tile.split(self.TILE_COORD_SEPARATOR)
                is_collidable = map_data["collidables"][row][column]

                x_frames = 1
                if x.count(self.TILE_FRAMES_SEPARATOR) > 0:
                    x, x_frames = x.split(self.TILE_FRAMES_SEPARATOR)

                y_frames = 1
                rotation = 0
                if y.count(self.TILE_FRAMES_SEPARATOR) > 0:
                    y, y_frames = y.split(self.TILE_FRAMES_SEPARATOR)
                    if y_frames.count(self.TILE_ROTATION_SEPARATOR) > 0:
                        y_frames, rotation = y.split(self.TILE_ROTATION_SEPARATOR)
                elif y.count(self.TILE_ROTATION_SEPARATOR) > 0:
                    y, rotation = y.split(self.TILE_ROTATION_SEPARATOR)

                x = int(x)
                y = int(y)

                if x == -1 and y == -1:
                    continue

                tile = Tile(
                    self.sprites,
                    sheet_metadata[f"{x},{y}"],
                    transform.rotate(
                        sheet.subsurface(
                            (x * Tile.WIDTH, y * Tile.HEIGHT), (Tile.WIDTH, Tile.HEIGHT)
                        ),
                        int(rotation) * 90,
                    ),
                    Vector2(column * Tile.WIDTH, row * Tile.HEIGHT),
                    collidable=is_collidable,
                )

                x_frames = int(x_frames)
                y_frames = int(y_frames)
                if (x_frames > 1) != (y_frames > 1):
                    tile.set_animation(
                        SpriteAnimation(
                            tile,
                            sheet.subsurface(
                                (x * Tile.WIDTH, y * Tile.HEIGHT),
                                (x_frames * Tile.WIDTH, y_frames * Tile.HEIGHT),
                            ),
                            x_frames if x_frames > 1 else y_frames,
                            1.5,  # TODO: speed animation should be parameterized
                            subsurface_direction="x" if x_frames > 1 else "y",
                        )
                    )

        self.width = (column + 1) * Tile.WIDTH
        self.height = (row + 1) * Tile.HEIGHT
