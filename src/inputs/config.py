"""Reads ``config.yaml``: window, controls (keys mapped to ``Action``), audio.

Every setting is optional; a misspelt one is reported with the known names.
"""

from __future__ import annotations

from dataclasses import dataclass, field, fields
from enum import Enum, auto
from pathlib import Path
from typing import Any, Dict, Mapping, Optional, Tuple

import yaml

from ..constants import CONFIG_FILE


@dataclass(frozen=True)
class Mixer:
    frequency: int = 22050
    size: int = -16
    channels: int = 2
    buffer: int = 512


@dataclass(frozen=True)
class Audio:
    enabled: bool = True
    # From 0 (silent) to 1.
    music_volume: float = 0.5
    sound_volume: float = 0.8


@dataclass(frozen=True)
class Display:
    """Size of the surface the game is drawn on, in game pixels."""

    width: int = 464
    height: int = 240


@dataclass(frozen=True)
class Screen:
    """The window: the display surface is scaled to fit it."""

    width: int = 1280
    height: int = 720
    flags: int = 0
    depth: int = 32
    resizable: bool = True
    # True keeps sharp square pixels (integer zoom) at the cost of black borders.
    integer_scaling: bool = False


@dataclass(frozen=True)
class Mouse:
    visible: bool = False


class Action(Enum):
    UP = auto()
    DOWN = auto()
    LEFT = auto()
    RIGHT = auto()
    CONFIRM = auto()
    BACK = auto()
    RUN = auto()


DEFAULT_CONTROLS: Dict[Action, Tuple[str, ...]] = {
    Action.UP: ("z", "up"),
    Action.DOWN: ("s", "down"),
    Action.LEFT: ("q", "left"),
    Action.RIGHT: ("d", "right"),
    Action.CONFIRM: ("a", "return", "space"),
    Action.BACK: ("escape",),
    Action.RUN: ("left shift", "right shift", "e"),
}


@dataclass(frozen=True)
class Controls:
    """Keyboard bindings, as pygame key names (``pygame.key.name``)."""

    bindings: Mapping[Action, Tuple[str, ...]] = field(
        default_factory=lambda: dict(DEFAULT_CONTROLS)
    )

    def __post_init__(self) -> None:
        used: Dict[str, Action] = {}
        for action, names in self.bindings.items():
            if not names:
                raise ValueError(f"Action {action.name.lower()} needs at least one key")
            for name in names:
                if not isinstance(name, str) or not name:
                    raise ValueError(f"Invalid key for action {action.name.lower()}: {name!r}")
                if name in used and used[name] != action:
                    raise ValueError(
                        f"Key {name!r} is assigned to both {used[name].name.lower()} "
                        f"and {action.name.lower()}"
                    )
                used[name] = action

    def action_of(self, key_name: str) -> Optional[Action]:
        key_name = key_name.lower()
        for action, names in self.bindings.items():
            if key_name in names:
                return action
        return None

    @classmethod
    def from_dict(cls, data: Optional[Mapping[str, Any]]) -> "Controls":
        bindings = dict(DEFAULT_CONTROLS)
        for name, keys in (data or {}).items():
            try:
                action = Action[str(name).upper()]
            except KeyError:
                raise ValueError(f"Unknown action in controls: {name!r}") from None
            if isinstance(keys, str):
                keys = [keys]
            if not isinstance(keys, (list, tuple)) or not keys:
                raise ValueError(f"Controls for {action.name.lower()} need a list of keys")
            bindings[action] = tuple(key.lower() if isinstance(key, str) else key for key in keys)
        return cls(bindings)


def _camel_to_snake(name: str) -> str:
    return "".join(f"_{char.lower()}" if char.isupper() else char for char in name)


def _snake_to_camel(name: str) -> str:
    first, *others = name.split("_")
    return first + "".join(word.capitalize() for word in others)


def _section(cls, data: Optional[Mapping[str, Any]]):
    """Builds a dataclass from a YAML section, keeping defaults for missing keys."""
    if data is not None and not isinstance(data, Mapping):
        raise ValueError(f"{cls.__name__.lower()} must be a mapping")
    known = {item.name for item in fields(cls)}
    values = {}
    for key, value in (data or {}).items():
        name = _camel_to_snake(key)
        if name not in known:
            raise ValueError(f"Unknown setting {key!r} for {cls.__name__.lower()}")
        default = getattr(cls, name)
        valid = (
            type(value) is bool if isinstance(default, bool) else
            type(value) is int if isinstance(default, int) else
            isinstance(value, (int, float)) and not isinstance(value, bool)
            if isinstance(default, float) else isinstance(value, type(default))
        )
        if not valid:
            raise ValueError(f"{cls.__name__.lower()}.{key} has an invalid type")
        values[name] = value
    return cls(**values)


@dataclass(frozen=True)
class Config:
    """Every setting of ``config.yaml``; the README lists them."""

    framerate_limit: int = 120
    skip_intro: bool = False
    mixer: Mixer = Mixer()
    audio: Audio = Audio()
    display: Display = Display()
    screen: Screen = Screen()
    mouse: Mouse = Mouse()
    controls: Controls = field(default_factory=Controls)

    @classmethod
    def from_dict(cls, data: Optional[Mapping[str, Any]]) -> "Config":
        if data is not None and not isinstance(data, Mapping):
            raise ValueError("config must be a mapping")
        data = dict(data or {})
        framerate = data.pop("framerateLimit", cls.framerate_limit)
        skip_intro = data.pop("skipIntro", cls.skip_intro)
        if type(framerate) is not int or framerate <= 0:
            raise ValueError("framerateLimit must be a positive whole number")
        if type(skip_intro) is not bool:
            raise ValueError("skipIntro must be true or false")
        config = cls(
            framerate_limit=framerate,
            skip_intro=skip_intro,
            mixer=_section(Mixer, data.pop("mixer", None)),
            audio=_section(Audio, data.pop("audio", None)),
            display=_section(Display, data.pop("display", None)),
            screen=_section(Screen, data.pop("screen", None)),
            mouse=_section(Mouse, data.pop("mouse", None)),
            controls=Controls.from_dict(data.pop("controls", None)),
        )
        if data:
            raise ValueError(f"Unknown settings: {', '.join(sorted(data))}")
        for name, size in (("display", config.display), ("screen", config.screen)):
            if size.width <= 0 or size.height <= 0:
                raise ValueError(f"{name} width and height must be positive")
        for name in ("music_volume", "sound_volume"):
            volume = getattr(config.audio, name)
            if isinstance(volume, bool) or not isinstance(volume, (int, float)) or not 0 <= volume <= 1:
                raise ValueError(f"audio {name.replace('_v', 'V')} must be a number from 0 to 1")
        return config

    @classmethod
    def load(cls, path: Path = CONFIG_FILE) -> "Config":
        """Reads ``config.yaml``; a missing file gives the default settings."""
        path = Path(path)
        if not path.exists():
            return cls()
        with path.open(encoding="utf-8") as config_file:
            try:
                return cls.from_dict(yaml.safe_load(config_file))
            except ValueError as error:
                raise ValueError(f"{path.name}: {error}") from None

    def to_dict(self) -> Dict[str, Any]:
        """The settings as ``config.yaml`` writes them (camelCase keys)."""
        data: Dict[str, Any] = {
            "framerateLimit": self.framerate_limit,
            "skipIntro": self.skip_intro,
        }
        for name in ("mixer", "audio", "display", "screen", "mouse"):
            section = getattr(self, name)
            data[name] = {
                _snake_to_camel(item.name): getattr(section, item.name) for item in fields(section)
            }
        data["controls"] = {
            action.name.lower(): list(keys) for action, keys in self.controls.bindings.items()
        }
        return data

    def write(self, path: Path = CONFIG_FILE) -> None:
        """Writes the settings back to ``config.yaml`` (see the SETTINGS screen)."""
        path = Path(path)
        temporary = path.with_suffix(path.suffix + ".tmp")
        with temporary.open("w", encoding="utf-8") as config_file:
            yaml.safe_dump(self.to_dict(), config_file, sort_keys=False)
        temporary.replace(path)
