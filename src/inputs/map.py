"""Reads a map made with the map editor: its tiles, solid cells, entities, the
behaviour of its tiles (``res/sheets/*.yaml``) and its ``level`` settings.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Iterator, List, Mapping, Optional, Tuple

from pygame import Surface, Vector2, transform
from pygame.sprite import LayeredUpdates

from ..sprite_animation import SpriteAnimation
from ..tile import Tile
from .sprites import Color, parse_color

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
    """An entity placed on a map with the editor, e.g. a goomba.

    ``settings`` overrides, for this entity only, the settings its type gives
    in ``res/entities.yaml`` (the editor writes them when you tune a placed
    entity); it is empty when the entity keeps the settings of its type.
    """

    type: str
    column: int
    row: int
    settings: Mapping[str, Any] = field(default_factory=dict)


def parse_entities(entries, columns: int, rows: int) -> List[EntitySpawn]:
    """The ``"entities"`` list of a map file, in reading order.

    Every entry is ``{"type": str, "x": column, "y": row}``, with an optional
    ``"settings"`` mapping. Maps made before entities existed have no such list.
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
        settings = entry.get("settings", {})
        if not isinstance(settings, dict) or not all(isinstance(key, str) for key in settings):
            raise ValueError(f"The settings of the entity {kind!r} must be a mapping")
        spawns[(column, row)] = EntitySpawn(kind, column, row, settings)
    return sorted(spawns.values(), key=lambda spawn: (spawn.row, spawn.column))


@dataclass(frozen=True)
class TileBehaviour:
    """What a named tile does in a platform level, from the ``behaviour`` (and
    ``becomes``) keys of the tileset metadata:

    - ``coin``: collected when Mario touches it;
    - ``question_block``: gives a coin (or the item hidden in it) when hit from
      below, then is drawn with the tile ``becomes``;
    - ``brick``: big Mario breaks it from below; ``becomes`` is ignored;
    - ``hurt``: hurts Mario when he touches it (spikes, lava...);
    - ``goal``: clears the course when Mario touches it.
    """

    kind: str
    becomes: Optional[str] = None

    KINDS = ("coin", "question_block", "brick", "hurt", "goal")
    # Tilesets without any behaviour (made before they existed) use these name
    # prefixes, as the first versions of the game did.
    GUESSES = (("coin", "coin", None), ("mystery_block", "question_block", "block"), ("brick", "brick", None))

    @classmethod
    def parse(cls, kind: Any, becomes: Any = None, where: str = "tile") -> "TileBehaviour":
        if kind not in cls.KINDS:
            raise ValueError(f"{where}: unknown behaviour {kind!r} (known: {', '.join(cls.KINDS)})")
        if becomes is not None and not isinstance(becomes, str):
            raise ValueError(f"{where}: 'becomes' must be a tile name")
        return cls(kind, becomes)

    @classmethod
    def guess(cls, name: str) -> Optional["TileBehaviour"]:
        for prefix, kind, becomes in cls.GUESSES:
            if name.startswith(prefix):
                return cls(kind, becomes)
        return None


@dataclass(frozen=True)
class LevelSettings:
    """The ``"level"`` block of a map file, set in the map editor. A missing
    value uses the default of ``res/rules.yaml``."""

    name: Optional[str] = None
    time_limit: Optional[int] = None
    sky: Optional[Color] = None
    music: Optional[str] = None

    KEYS = {"name": "name", "timeLimit": "time_limit", "sky": "sky", "music": "music"}

    @classmethod
    def parse(cls, data: Any) -> "LevelSettings":
        if data is None:
            return cls()
        if not isinstance(data, Mapping):
            raise ValueError("The level settings of a map must be a mapping")
        unknown = set(data) - set(cls.KEYS)
        if unknown:
            raise ValueError(f"Unknown level setting(s): {', '.join(sorted(unknown))}")
        name, time_limit, sky, music = (data.get(key) for key in cls.KEYS)
        if name is not None and not isinstance(name, str):
            raise ValueError("The level name must be a text")
        if time_limit is not None and (
            isinstance(time_limit, bool) or not isinstance(time_limit, int) or time_limit <= 0
        ):
            raise ValueError("The time limit of a level must be a positive whole number")
        if sky is not None:
            sky = parse_color(sky, "The sky color")
        if music is not None and not isinstance(music, str):
            raise ValueError("The music of a level must be a music id of ressources.yaml")
        return cls(name or None, time_limit, sky, music or None)


def tile_behaviours(
    metadata: Mapping[str, str], behaviours: Optional[Mapping[str, TileBehaviour]],
) -> Dict[str, TileBehaviour]:
    if behaviours:
        return dict(behaviours)
    guesses = {name: TileBehaviour.guess(name) for name in metadata.values()}
    return {name: guess for name, guess in guesses.items() if guess is not None}


@dataclass(frozen=True)
class MapData:
    """Validated map data, independent of Pygame surfaces and sprites."""

    tiles: List[List[Optional[TileCode]]]
    collidables: List[List[bool]]
    entities: List[EntitySpawn]
    settings: LevelSettings

    @property
    def columns(self) -> int:
        return len(self.tiles[0])

    @property
    def rows(self) -> int:
        return len(self.tiles)

    @classmethod
    def parse(cls, data: Any) -> "MapData":
        if not isinstance(data, dict):
            raise ValueError("A map must be a JSON object")
        tiles, solids = data.get("tiles"), data.get("collidables")
        if not isinstance(tiles, list) or not tiles or not isinstance(tiles[0], list) or not tiles[0]:
            raise ValueError("Map tiles must be a non-empty matrix")
        columns = len(tiles[0])
        if any(not isinstance(row, list) or len(row) != columns for row in tiles):
            raise ValueError("Every row of a map must have the same number of tiles")
        if not isinstance(solids, list) or len(solids) != len(tiles) or any(
            not isinstance(row, list) or len(row) != columns for row in solids
        ):
            raise ValueError("The collision grid does not match the size of the map")
        if any(type(value) is not bool for row in solids for value in row):
            raise ValueError("The collision grid must contain only booleans")
        codes = [[TileCode.parse(value) for value in row] for row in tiles]
        return cls(
            codes, [list(row) for row in solids],
            parse_entities(data.get("entities"), columns, len(tiles)),
            LevelSettings.parse(data.get("level")),
        )

    def validate_sheet(
        self, metadata: Mapping[str, str], behaviours: Mapping[str, TileBehaviour],
        sheet_size: Tuple[int, int],
    ) -> None:
        """Check tiles and their replacements against the actual sheet image."""
        sheet_columns, sheet_rows = sheet_size[0] // Tile.WIDTH, sheet_size[1] // Tile.HEIGHT
        names = set(metadata.values())
        for name, behaviour in behaviours.items():
            if behaviour.becomes is not None and behaviour.becomes not in names:
                raise ValueError(
                    f"Tile {name!r} becomes {behaviour.becomes!r}, which the tileset does not declare")
        for row, codes in enumerate(self.tiles):
            for column, code in enumerate(codes):
                if code is None:
                    continue
                if code.x + code.x_frames > sheet_columns or code.y + code.y_frames > sheet_rows:
                    raise ValueError(f"Tile at {column},{row} is outside the tileset")
                if f"{code.x},{code.y}" not in metadata:
                    raise ValueError(
                        f"Tile {code.x},{code.y} at {column},{row} "
                        "is not declared in the tileset metadata"
                    )


class Map:
    """A level made with the map editor: tile sprites, a collision grid and the
    entities to spawn."""

    # Kept for the code that still reads them from the map.
    TILE_COORD_SEPARATOR = TileCode.COORD_SEPARATOR
    TILE_FRAMES_SEPARATOR = TileCode.FRAMES_SEPARATOR
    TILE_ROTATION_SEPARATOR = TileCode.ROTATION_SEPARATOR

    ANIMATION_SPEED = 1.5  # frames per second

    def __init__(
        self,
        sheet: Surface,
        sheet_metadata: Dict[str, str],
        map_data: dict,
        behaviours: Optional[Mapping[str, TileBehaviour]] = None,
    ):
        parsed = MapData.parse(map_data)
        parsed.validate_sheet(
            sheet_metadata, tile_behaviours(sheet_metadata, behaviours), sheet.get_size()
        )
        self.rows = parsed.rows
        self.columns = parsed.columns

        self.width = self.columns * Tile.WIDTH
        self.height = self.rows * Tile.HEIGHT
        self.collidables = parsed.collidables
        self.entities = parsed.entities
        self.settings = parsed.settings
        self.sprites = LayeredUpdates()
        self.sheet = sheet
        self._by_name: Dict[str, List[Tile]] = {}
        self._by_cell: Dict[Cell, Tile] = {}
        self._animated: List[Tile] = []
        self._coordinates: Dict[str, Cell] = {}
        for coordinate, name in sheet_metadata.items():
            x, y = coordinate.split(",")
            self._coordinates.setdefault(name, (int(x), int(y)))
        self.behaviours = tile_behaviours(sheet_metadata, behaviours)
        for row, codes in enumerate(parsed.tiles):
            for column, tile_code in enumerate(codes):
                if tile_code is None:
                    continue
                name = sheet_metadata[f"{tile_code.x},{tile_code.y}"]
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

    def behaviour_of(self, tile: Optional[Tile]) -> Optional[TileBehaviour]:
        return None if tile is None else self.behaviours.get(tile.id)

    def names_with(self, kind: str) -> List[str]:
        """Tile names of the tileset with the behaviour ``kind``, in the order
        of the metadata."""
        return [name for name in self._coordinates
                if getattr(self.behaviours.get(name), "kind", None) == kind]

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
