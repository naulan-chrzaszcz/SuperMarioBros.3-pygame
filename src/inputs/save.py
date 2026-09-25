from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum, auto
from pathlib import Path
from typing import List, Optional

import yaml

from ..constants import SAVE_FILE


@dataclass
class Position:
    x: int = 128
    y: int = 16


class PlayerState(Enum):
    LITTLE = auto()
    BIG = auto()


INVENTORY_SIZE = 3


@dataclass
class Game:
    level: str = "WORLD 1"
    score: int = 0
    coins: int = 0
    life: int = 4
    inventory: List[Optional[str]] = field(default_factory=lambda: [None] * INVENTORY_SIZE)
    state: PlayerState = PlayerState.LITTLE

    @property
    def world(self) -> str:
        """World number shown by the HUD: "WORLD 1" gives "1"."""
        return self.level.split()[-1] if self.level.split() else ""


@dataclass
class Save:
    """Progress of the player, read from and written to ``save.yaml``."""

    player: str = "mario"
    position: Position = field(default_factory=Position)
    game: Game = field(default_factory=Game)

    @classmethod
    def from_dict(cls, data: dict | None) -> "Save":
        data = data or {}
        game = dict(data.get("game") or {})
        state = game.pop("state", PlayerState.LITTLE.name)
        inventory = list(game.pop("inventory", None) or [])
        inventory = (inventory + [None] * INVENTORY_SIZE)[:INVENTORY_SIZE]
        try:
            player_state = PlayerState[str(state).upper()]
        except KeyError:
            raise ValueError(f"Unknown player state: {state!r}") from None
        return cls(
            player=str(data.get("player", "mario")),
            position=Position(**(data.get("position") or {})),
            game=Game(**game, inventory=inventory, state=player_state),
        )

    def to_dict(self) -> dict:
        data = asdict(self)
        data["game"]["state"] = self.game.state.name.lower()
        return data

    @classmethod
    def load(cls, path: Path = SAVE_FILE) -> "Save":
        """Reads the save; a missing file starts a new game."""
        path = Path(path)
        if not path.exists():
            return cls()
        with path.open(encoding="utf-8") as save_file:
            try:
                return cls.from_dict(yaml.safe_load(save_file))
            except (TypeError, ValueError) as error:
                raise ValueError(f"{path.name}: {error}") from None

    def write(self, path: Path = SAVE_FILE) -> None:
        path = Path(path)
        temporary = path.with_suffix(path.suffix + ".tmp")
        with temporary.open("w", encoding="utf-8") as save_file:
            yaml.safe_dump(self.to_dict(), save_file, sort_keys=False)
        temporary.replace(path)
