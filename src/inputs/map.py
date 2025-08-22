from pygame import Vector2, transform, Surface

from ..animated_tile import AnimatedTile
from ..tile import Tile


class Map:
    LINE_SEPARATOR = "\n"
    TILE_SEPARATOR = ";"
    TILE_COORD_SEPARATOR = ","
    TILE_FRAMES_SEPARATOR = "+"
    TILE_ROTATION_SEPARATOR = "&"

    tiles = []
    animated_tiles = []

    width = 0
    height = 0

    def __init__(self, sheet: Surface, map_data: str):
        column = 0
        row = 0
        for row, line in enumerate(map_data.split(self.LINE_SEPARATOR)):
            column = 0
            for tile in line.split(self.TILE_SEPARATOR):
                x, y = tile.split(self.TILE_COORD_SEPARATOR)
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
                tile_pos = Vector2(column * Tile.WIDTH, row * Tile.HEIGHT)
                if x_frames > 1:
                    self.animated_tiles.append(
                        AnimatedTile(
                            sheet.subsurface(
                                (x * Tile.WIDTH, y * Tile.HEIGHT),
                                (x_frames * Tile.WIDTH, Tile.HEIGHT),
                            ),
                            tile_pos,
                            x_frames,
                        )
                    )
                if y_frames > 1:
                    self.animated_tiles.append(
                        AnimatedTile(
                            sheet.subsurface(
                                (x * Tile.WIDTH, y * Tile.HEIGHT),
                                (Tile.WIDTH, y_frames * Tile.HEIGHT),
                            ),
                            tile_pos,
                            y_frames,
                            subsurface_direction="y",
                        )
                    )
                else:
                    tile = sheet.subsurface(
                        (x * Tile.WIDTH, y * Tile.HEIGHT), (Tile.WIDTH, Tile.HEIGHT)
                    )
                    tile = transform.rotate(tile, int(rotation) * 90)
                    self.tiles.append(Tile(tile, tile_pos))
                column += 1

        self.width = column * Tile.WIDTH
        self.height = (row + 1) * Tile.HEIGHT
