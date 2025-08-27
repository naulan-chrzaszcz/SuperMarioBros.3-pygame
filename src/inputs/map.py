from typing import Dict

from pygame import Vector2, transform, Surface
from pygame.sprite import LayeredUpdates

from ..animated_tile import AnimatedTile
from ..tile import Tile


class Map:
    TILE_COORD_SEPARATOR = ","
    TILE_FRAMES_SEPARATOR = "+"
    TILE_ROTATION_SEPARATOR = "&"

    sprites = LayeredUpdates()

    width = 0
    height = 0

    def __init__(
        self, sheet: Surface, sheet_metadata: Dict[str, str], map_data: dict
    ):
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
                x_frames = int(x_frames)
                y_frames = int(y_frames)
                tile_id = sheet_metadata[f"{x},{y}"]
                tile_pos = Vector2(column * Tile.WIDTH, row * Tile.HEIGHT)
                if x_frames > 1:
                    AnimatedTile(
                        self.sprites,
                        tile_id,
                        sheet.subsurface(
                            (x * Tile.WIDTH, y * Tile.HEIGHT),
                            (x_frames * Tile.WIDTH, Tile.HEIGHT),
                        ),
                        tile_pos,
                        x_frames,
                        collidable=is_collidable,
                    )
                elif y_frames > 1:
                    AnimatedTile(
                        self.sprites,
                        tile_id,
                        sheet.subsurface(
                            (x * Tile.WIDTH, y * Tile.HEIGHT),
                            (Tile.WIDTH, y_frames * Tile.HEIGHT),
                        ),
                        tile_pos,
                        y_frames,
                        subsurface_direction="y",
                        collidable=is_collidable,
                    )
                else:
                    tile = sheet.subsurface(
                        (x * Tile.WIDTH, y * Tile.HEIGHT), (Tile.WIDTH, Tile.HEIGHT)
                    )
                    Tile(
                        self.sprites,
                        tile_id,
                        transform.rotate(tile, int(rotation) * 90),
                        tile_pos,
                        collidable=is_collidable,
                    )

        self.width = (column + 1) * Tile.WIDTH
        self.height = (row + 1) * Tile.HEIGHT
