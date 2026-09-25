from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterator, List, Optional, Tuple

from pygame import Surface, Vector2, transform
from pygame.sprite import LayeredUpdates

from ..sprite_animation import SpriteAnimation
from ..tile import Tile

Cell = Tuple[int, int]


@dataclass(frozen=True)
class TileCode:
    """A cell of a map file, e.g. ``"1+4,2&3"``.

    ``x,y`` is the tile in the sheet, ``+n`` after ``x`` (or ``y``) animates it
    over ``n`` tiles to the right (or below), ``&r`` rotates it by ``r`` quarter
    turns counter-clockwise. ``-1,-1`` is an empty cell.
    """

    x: int
    y: int
    x_frames: int = 1
    y_frames: int = 1
    rotation: int = 0

    COORD_SEPARATOR = ","
    FRAMES_SEPARATOR = "+"
    ROTATION_SEPARATOR = "&"

    @classmethod
    def parse(cls, code: str) -> Optional["TileCode"]:
        try:
            x, y = str(code).split(cls.COORD_SEPARATOR)
            rotation = 0
            if cls.ROTATION_SEPARATOR in y:
                y, rotation = y.split(cls.ROTATION_SEPARATOR)
            x, _, x_frames = x.partition(cls.FRAMES_SEPARATOR)
            y, _, y_frames = y.partition(cls.FRAMES_SEPARATOR)
            tile = cls(int(x), int(y), int(x_frames or 1), int(y_frames or 1), int(rotation) % 4)
        except ValueError:
            raise ValueError(f"Invalid tile code: {code!r}") from None
        if tile.x == -1 and tile.y == -1:
            return None
        if tile.x < 0 or tile.y < 0 or tile.x_frames < 1 or tile.y_frames < 1:
            raise ValueError(f"Invalid tile code: {code!r}")
        if tile.x_frames > 1 and tile.y_frames > 1:
            raise ValueError(f"A tile is animated along one axis only: {code!r}")
        return tile

    @property
    def frames(self) -> int:
        return max(self.x_frames, self.y_frames)

    @property
    def direction(self) -> str:
        return "y" if self.y_frames > 1 else "x"


@dataclass(frozen=True)
class EntitySpawn:
    """An entity placed on a map with the editor, e.g. a goomba."""

    type: str
    column: int
    row: int


def parse_entities(entries, columns: int, rows: int) -> List[EntitySpawn]:
    """The ``"entities"`` list of a map file, in reading order.

    Every entry is ``{"type": str, "x": column, "y": row}``. Maps made before
    entities existed have no such list.
    """
    if entries is None:
        return []
    if not isinstance(entries, list):
        raise ValueError("The entities of a map must be a list")
    spawns: Dict[Cell, EntitySpawn] = {}
    for entry in entries:
        if not isinstance(entry, dict):
            raise ValueError(f"Invalid entity: {entry!r}")
        kind, column, row = entry.get("type"), entry.get("x"), entry.get("y")
        if not isinstance(kind, str) or not kind:
            raise ValueError(f"An entity has no type: {entry!r}")
        if type(column) is not int or type(row) is not int:
            raise ValueError(f"Entity {kind!r} has invalid coordinates")
        if not (0 <= column < columns and 0 <= row < rows):
            raise ValueError(f"Entity {kind!r} at {column},{row} is outside the map")
        if (column, row) in spawns:
            raise ValueError(f"Two entities are on the cell {column},{row}")
        spawns[(column, row)] = EntitySpawn(kind, column, row)
    return sorted(spawns.values(), key=lambda spawn: (spawn.row, spawn.column))


class Map:
    """A level made with the map editor: tile sprites, a collision grid and the
    entities to spawn."""

    # Kept for the code that still reads them from the map.
    TILE_COORD_SEPARATOR = TileCode.COORD_SEPARATOR
    TILE_FRAMES_SEPARATOR = TileCode.FRAMES_SEPARATOR
    TILE_ROTATION_SEPARATOR = TileCode.ROTATION_SEPARATOR

    ANIMATION_SPEED = 1.5  # frames per second

    def __init__(self, sheet: Surface, sheet_metadata: Dict[str, str], map_data: dict):
        tiles = map_data.get("tiles") or []
        collidables = map_data.get("collidables") or []
        self.rows = len(tiles)
        self.columns = len(tiles[0]) if tiles else 0
        if any(len(row) != self.columns for row in tiles):
            raise ValueError("Every row of a map must have the same number of tiles")
        if len(collidables) != self.rows or any(len(row) != self.columns for row in collidables):
            raise ValueError("The collision grid does not match the size of the map")

        self.width = self.columns * Tile.WIDTH
        self.height = self.rows * Tile.HEIGHT
        self.collidables: List[List[bool]] = [[bool(value) for value in row] for row in collidables]
        self.entities = parse_entities(map_data.get("entities"), self.columns, self.rows)
        self.sprites = LayeredUpdates()
        self.sheet = sheet
        self._by_name: Dict[str, List[Tile]] = {}
        self._by_cell: Dict[Cell, Tile] = {}
        self._animated: List[Tile] = []
        self._coordinates: Dict[str, Cell] = {}
        for coordinate, name in sheet_metadata.items():
            x, y = coordinate.split(",")
            self._coordinates.setdefault(name, (int(x), int(y)))

        sheet_columns = sheet.get_width() // Tile.WIDTH
        sheet_rows = sheet.get_height() // Tile.HEIGHT
        for row, codes in enumerate(tiles):
            for column, code in enumerate(codes):
                tile_code = TileCode.parse(code)
                if tile_code is None:
                    continue
                last_x = tile_code.x + tile_code.x_frames - 1
                last_y = tile_code.y + tile_code.y_frames - 1
                if last_x >= sheet_columns or last_y >= sheet_rows:
                    raise ValueError(f"Tile {code!r} at {column},{row} is outside the tileset")
                name = sheet_metadata.get(f"{tile_code.x},{tile_code.y}")
                if name is None:
                    raise ValueError(
                        f"Tile {tile_code.x},{tile_code.y} at {column},{row} "
                        "is not declared in the tileset metadata"
                    )
                self._add_tile(sheet, tile_code, name, column, row)

    def _add_tile(self, sheet: Surface, code: TileCode, name: str, column: int, row: int) -> None:
        origin = (code.x * Tile.WIDTH, code.y * Tile.HEIGHT)
        tile = Tile(
            self.sprites,
            name,
            transform.rotate(sheet.subsurface(origin, (Tile.WIDTH, Tile.HEIGHT)), code.rotation * 90),
            Vector2(column * Tile.WIDTH, row * Tile.HEIGHT),
            collidable=self.collidables[row][column],
        )
        if code.frames > 1:
            strip = sheet.subsurface(
                origin, (code.x_frames * Tile.WIDTH, code.y_frames * Tile.HEIGHT)
            )
            tile.set_animation(
                SpriteAnimation(
                    tile, strip, code.frames, self.ANIMATION_SPEED, code.direction, code.rotation * 90
                )
            )
            self._animated.append(tile)
        self._by_name.setdefault(name, []).append(tile)
        self._by_cell[(column, row)] = tile

    def contains(self, column: int, row: int) -> bool:
        return 0 <= column < self.columns and 0 <= row < self.rows

    def is_blocked(self, column: int, row: int) -> bool:
        """True outside the map and on collidable cells."""
        return not self.contains(column, row) or self.collidables[row][column]

    def tiles_named(self, name: str) -> List[Tile]:
        return list(self._by_name.get(name, []))

    def find(self, name: str) -> Optional[Tile]:
        """First tile called ``name`` (reading order), or None."""
        tiles = self._by_name.get(name)
        return tiles[0] if tiles else None

    def tile_at(self, column: int, row: int) -> Optional[Tile]:
        return self._by_cell.get((column, row))

    def has_tile_named(self, name: str) -> bool:
        """True when the tileset declares a tile called ``name``."""
        return name in self._coordinates

    def image_of(self, name: str) -> Surface:
        """Still image of the tileset tile called ``name``."""
        x, y = self._coordinates[name]
        return self.sheet.subsurface((x * Tile.WIDTH, y * Tile.HEIGHT), (Tile.WIDTH, Tile.HEIGHT))

    def remove(self, tile: Tile) -> None:
        """Takes a tile out of the map (e.g. a collected coin)."""
        tile.kill()
        if self._by_cell.get(tile.cell) is tile:
            del self._by_cell[tile.cell]
        if tile in self._by_name.get(tile.id, []):
            self._by_name[tile.id].remove(tile)
        if tile in self._animated:
            self._animated.remove(tile)

    def set_collidable(self, column: int, row: int, value: bool) -> None:
        """Changes the collision of a cell (e.g. a broken brick lets Mario pass)."""
        self.collidables[row][column] = value
        tile = self._by_cell.get((column, row))
        if tile is not None:
            tile.collidable = value

    def replace(self, tile: Tile, name: str) -> None:
        """Draws ``tile`` with the still tileset tile called ``name`` from now on
        (e.g. an emptied ? block)."""
        image = self.image_of(name)
        if tile in self._by_name.get(tile.id, []):
            self._by_name[tile.id].remove(tile)
        if tile in self._animated:
            self._animated.remove(tile)
        tile.set_animation(None)
        tile.image = image
        tile.id = name
        self._by_name.setdefault(name, []).append(tile)

    def __iter__(self) -> Iterator[Tile]:
        return iter(self.sprites)

    def update(self, dt: float) -> None:
        # Map tiles do not move: only the animated ones need an update.
        for tile in self._animated:
            tile.update(dt)

    def draw(self, surface: Surface) -> None:
        self.sprites.draw(surface)
