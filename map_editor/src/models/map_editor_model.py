from contextlib import contextmanager
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterable, Iterator, List, Optional, Set, Tuple

from ..constantes import HISTORY_LIMIT
from ..outputs.map import Cell, Map
from ..outputs.tile import Tile
from .clipboard import Clipboard, Region
from .tileset import SheetCell, Tileset


@dataclass
class Edit:
    """One undoable user action: the previous and new value of every changed cell."""

    tiles: Dict[Cell, Tuple[Optional[Tile], Optional[Tile]]] = field(default_factory=dict)
    collisions: Dict[Cell, Tuple[bool, bool]] = field(default_factory=dict)

    def is_empty(self) -> bool:
        return not self.tiles and not self.collisions

    def record_tile(self, cell: Cell, old: Optional[Tile], new: Optional[Tile]) -> None:
        old = self.tiles.get(cell, (old, None))[0]
        if old == new:
            self.tiles.pop(cell, None)
        else:
            self.tiles[cell] = (old, new)

    def record_collision(self, cell: Cell, old: bool, new: bool) -> None:
        old = self.collisions.get(cell, (old, None))[0]
        if old == new:
            self.collisions.pop(cell, None)
        else:
            self.collisions[cell] = (old, new)


class MapEditorModel:
    """The edited map, in cell coordinates, with an undo/redo history."""

    def __init__(
        self,
        columns: int,
        rows: int,
        tiles: Optional[Dict[Cell, Tile]] = None,
        collidables: Iterable[Cell] = (),
    ) -> None:
        if columns <= 0 or rows <= 0:
            raise ValueError("Map dimensions must be positive")
        self.columns = columns
        self.rows = rows
        self.tiles: Dict[Cell, Tile] = {}
        self.collidables: Set[Cell] = set()
        for cell, tile in (tiles or {}).items():
            self._check_cell(cell)
            self.tiles[cell] = tile
        for cell in collidables:
            self._check_cell(cell)
            self.collidables.add(cell)

        self._undo: List[Edit] = []
        self._redo: List[Edit] = []
        self._current: Optional[Edit] = None
        self._saved_edit: Optional[Edit] = None
        self._resized = False

    @classmethod
    def from_file(cls, path: Path) -> "MapEditorModel":
        columns, rows, tiles, collidables = Map.read(path)
        return cls(columns, rows, tiles, collidables)

    def save(self, path: Path, sheet: Optional[Path] = None) -> None:
        self.end_edit()
        Map.write(path, self.columns, self.rows, self.tiles, self.collidables, sheet)
        self._saved_edit = self._last_edit()
        self._resized = False

    @property
    def dirty(self) -> bool:
        return self._resized or self._last_edit() is not self._saved_edit

    @property
    def can_undo(self) -> bool:
        return bool(self._undo) or (self._current is not None and not self._current.is_empty())

    @property
    def can_redo(self) -> bool:
        return bool(self._redo)

    def contains(self, cell: Cell) -> bool:
        return 0 <= cell[0] < self.columns and 0 <= cell[1] < self.rows

    def cells_between(self, start: Cell, end: Cell) -> Iterator[Cell]:
        """Cells of the rectangle defined by two corners, clipped to the map."""
        left, right = sorted((start[0], end[0]))
        top, bottom = sorted((start[1], end[1]))
        for row in range(max(top, 0), min(bottom, self.rows - 1) + 1):
            for col in range(max(left, 0), min(right, self.columns - 1) + 1):
                yield col, row

    def begin_edit(self) -> None:
        if self._current is None:
            self._current = Edit()

    def end_edit(self) -> None:
        edit, self._current = self._current, None
        if edit is None or edit.is_empty():
            return
        self._undo.append(edit)
        del self._undo[:-HISTORY_LIMIT]
        self._redo.clear()

    @contextmanager
    def edit(self) -> Iterator[None]:
        """Groups every change made inside the block into a single undo step."""
        owner = self._current is None
        self.begin_edit()
        try:
            yield
        finally:
            if owner:
                self.end_edit()

    def set_tile(self, cell: Cell, tile: Optional[Tile]) -> bool:
        if not self.contains(cell):
            return False
        old = self.tiles.get(cell)
        if old == tile:
            return False
        with self.edit():
            self._current.record_tile(cell, old, tile)
            self._apply_tile(cell, tile)
        return True

    def set_collidable(self, cell: Cell, value: bool) -> bool:
        if not self.contains(cell):
            return False
        old = cell in self.collidables
        if old == value:
            return False
        with self.edit():
            self._current.record_collision(cell, old, value)
            self._apply_collision(cell, value)
        return True

    def undo(self) -> bool:
        self.end_edit()
        if not self._undo:
            return False
        edit = self._undo.pop()
        for cell, (old, _) in edit.tiles.items():
            self._apply_tile(cell, old)
        for cell, (old, _) in edit.collisions.items():
            self._apply_collision(cell, old)
        self._redo.append(edit)
        return True

    def redo(self) -> bool:
        self.end_edit()
        if not self._redo:
            return False
        edit = self._redo.pop()
        for cell, (_, new) in edit.tiles.items():
            self._apply_tile(cell, new)
        for cell, (_, new) in edit.collisions.items():
            self._apply_collision(cell, new)
        self._undo.append(edit)
        return True

    def resize(self, columns: int, rows: int) -> None:
        """Changes the map size, dropping content outside it. Clears the history."""
        if columns <= 0 or rows <= 0:
            raise ValueError("Map dimensions must be positive")
        self.end_edit()
        self.columns = columns
        self.rows = rows
        self.tiles = {cell: tile for cell, tile in self.tiles.items() if self.contains(cell)}
        self.collidables = {cell for cell in self.collidables if self.contains(cell)}
        self._undo.clear()
        self._redo.clear()
        self._saved_edit = None
        self._resized = True

    def clip_region(self, region: Region) -> Optional[Region]:
        """The part of ``region`` inside the map, or None if it is outside."""
        left, top = max(region[0], 0), max(region[1], 0)
        right, bottom = min(region[2], self.columns - 1), min(region[3], self.rows - 1)
        if left > right or top > bottom:
            return None
        return left, top, right, bottom

    def copy(self, region: Region, sheet_path: Optional[Path] = None) -> Clipboard:
        left, top, right, bottom = region
        cells = list(self.cells_between((left, top), (right, bottom)))
        return Clipboard(
            right - left + 1,
            bottom - top + 1,
            {
                (col - left, row - top): self.tiles[(col, row)]
                for col, row in cells
                if (col, row) in self.tiles
            },
            frozenset(
                (col - left, row - top) for col, row in cells if (col, row) in self.collidables
            ),
            sheet_path,
        )

    def clear(self, region: Region) -> bool:
        """Removes the tiles and collisions of a region in one undo step."""
        changed = False
        with self.edit():
            for cell in self.cells_between(region[:2], region[2:]):
                changed |= self.set_tile(cell, None)
                changed |= self.set_collidable(cell, False)
        return changed

    def paste(self, clipboard: Clipboard, origin: Cell, tileset: Optional[Tileset] = None) -> int:
        """Pastes a block with its top-left corner on ``origin`` in one undo step.

        Tiles undeclared in ``tileset`` are skipped. Returns their number.
        """
        skipped = 0
        with self.edit():
            for (col, row), tile, solid in clipboard.cells():
                cell = (origin[0] + col, origin[1] + row)
                if not self.contains(cell):
                    continue
                if tile is not None and tileset is not None and not tileset.is_declared(tile.x, tile.y):
                    skipped += 1
                    continue
                self.set_tile(cell, tile)
                self.set_collidable(cell, solid)
        return skipped

    def undeclared_tiles(self, tileset: Tileset) -> Set[SheetCell]:
        return {
            (tile.x, tile.y)
            for tile in self.tiles.values()
            if not tileset.is_declared(tile.x, tile.y)
        }

    def _last_edit(self) -> Optional[Edit]:
        return self._undo[-1] if self._undo else None

    def _apply_tile(self, cell: Cell, tile: Optional[Tile]) -> None:
        if tile is None:
            self.tiles.pop(cell, None)
        else:
            self.tiles[cell] = tile

    def _apply_collision(self, cell: Cell, value: bool) -> None:
        if value:
            self.collidables.add(cell)
        else:
            self.collidables.discard(cell)

    def _check_cell(self, cell: Cell) -> None:
        if not self.contains(cell):
            raise ValueError(f"Cell is outside the map: {cell}")
