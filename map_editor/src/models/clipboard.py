from dataclasses import dataclass, field, replace
from pathlib import Path
from typing import Dict, FrozenSet, Iterator, Optional, Tuple

from ..outputs.map import Cell
from ..outputs.tile import Tile

# Inclusive rectangle of cells: (left, top, right, bottom).
Region = Tuple[int, int, int, int]


def make_region(start: Cell, end: Cell) -> Region:
    """Normalized region between two corner cells."""
    left, right = sorted((start[0], end[0]))
    top, bottom = sorted((start[1], end[1]))
    return left, top, right, bottom


def region_size(region: Region) -> Tuple[int, int]:
    return region[2] - region[0] + 1, region[3] - region[1] + 1


@dataclass(frozen=True)
class Clipboard:
    """A copied block of cells, in coordinates relative to its top-left corner.

    Cells that have no tile, no collision and no entity are transparent:
    pasting the block leaves the map untouched there.
    """

    columns: int
    rows: int
    tiles: Dict[Cell, Tile] = field(default_factory=dict)
    collidables: FrozenSet[Cell] = frozenset()
    sheet_path: Optional[Path] = None
    entities: Dict[Cell, str] = field(default_factory=dict)

    @property
    def is_empty(self) -> bool:
        return not self.tiles and not self.collidables and not self.entities

    def cells(self) -> Iterator[Tuple[Cell, Optional[Tile], bool]]:
        """Non-transparent cells with their tile and collision (their entity is
        in ``entities``)."""
        for cell in sorted(set(self.tiles) | self.collidables | set(self.entities)):
            yield cell, self.tiles.get(cell), cell in self.collidables

    def rotated(self, direction: int = 1) -> "Clipboard":
        """The block turned by a quarter turn, counter-clockwise for a positive
        direction like tile rotations in the game."""
        clipboard = self
        for _ in range(direction % 4):
            clipboard = clipboard._rotated_counter_clockwise()
        return clipboard

    def _rotated_counter_clockwise(self) -> "Clipboard":
        def turn(cell: Cell) -> Cell:
            return cell[1], self.columns - 1 - cell[0]

        return replace(
            self,
            columns=self.rows,
            rows=self.columns,
            tiles={
                turn(cell): replace(tile, rotation=(tile.rotation + 90) % 360)
                for cell, tile in self.tiles.items()
            },
            collidables=frozenset(turn(cell) for cell in self.collidables),
            entities={turn(cell): kind for cell, kind in self.entities.items()},
        )
