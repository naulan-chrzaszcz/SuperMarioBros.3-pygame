"""Game constants overridden by the YAML files.

The classes of the game keep their tuning values as UPPER_CASE class
constants (``Body.WALK_SPEED``, ``Goomba.SPEED``...), which are the defaults.
A YAML file gives new values with camelCase keys (``walkSpeed: 120``):
:func:`tune` checks that the constant exists and that the value has the same
type as the default, then sets it on one object, so a mistake in a file is
reported by name instead of breaking the game later.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Mapping, Optional

import yaml


def constant_name(key: str) -> str:
    """``walkSpeed`` (or ``walk_speed``) gives ``WALK_SPEED``."""
    snake = "".join(f"_{char}" if char.isupper() else char for char in str(key))
    return snake.strip("_").upper()


def setting_key(name: str) -> str:
    """``WALK_SPEED`` gives ``walkSpeed``, the key used in the YAML files."""
    first, *others = name.lower().split("_")
    return first + "".join(word.capitalize() for word in others)


def tunable_constants(cls: type) -> Dict[str, Any]:
    """The UPPER_CASE constants of ``cls`` (and of its parents) that a YAML file
    can set, except the ones listed in its ``NOT_TUNABLE`` tuple."""
    constants: Dict[str, Any] = {}
    fixed = set(getattr(cls, "NOT_TUNABLE", ())) | {"NOT_TUNABLE"}
    for klass in reversed(cls.__mro__):
        for name, value in vars(klass).items():
            if name.isupper() and not name.startswith("_") and name not in fixed and _is_setting(value):
                constants[name] = value
    return constants


def _is_setting(value: Any) -> bool:
    if isinstance(value, (bool, int, float, str)):
        return True
    return isinstance(value, tuple) and all(isinstance(item, (bool, int, float, str)) for item in value)


def convert(value: Any, default: Any, where: str) -> Any:
    """``value`` with the type of ``default``; ValueError when it cannot be."""
    if isinstance(default, bool):
        if isinstance(value, bool):
            return value
        raise ValueError(f"{where} must be true or false")
    if isinstance(default, int):
        if isinstance(value, int) and not isinstance(value, bool):
            return value
        raise ValueError(f"{where} must be a whole number")
    if isinstance(default, float):
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            return float(value)
        raise ValueError(f"{where} must be a number")
    if isinstance(default, str):
        if isinstance(value, str):
            return value
        raise ValueError(f"{where} must be a text")
    if isinstance(default, tuple):
        if not isinstance(value, (list, tuple)):
            raise ValueError(f"{where} must be a list")
        if default and len({type(item) for item in default}) == 1:
            return tuple(convert(item, default[0], where) for item in value)
        if len(value) != len(default):
            raise ValueError(f"{where} must have {len(default)} values")
        return tuple(convert(item, base, where) for item, base in zip(value, default))
    raise ValueError(f"{where} cannot be changed")


def check(cls: type, settings: Optional[Mapping[str, Any]], where: str) -> Dict[str, Any]:
    """The constants of ``cls`` that ``settings`` changes, with their new
    values; ValueError for an unknown setting or a value of the wrong type."""
    if not settings:
        return {}
    if not isinstance(settings, Mapping):
        raise ValueError(f"{where}: the settings must be a mapping of names to values")
    known = tunable_constants(cls)
    values = {}
    for key, value in settings.items():
        name = constant_name(key)
        if name not in known:
            choices = ", ".join(sorted(setting_key(constant) for constant in known))
            raise ValueError(f"{where}: unknown setting {key!r} (known: {choices})")
        if name.endswith("COLOR"):
            from .sprites import parse_color

            values[name] = parse_color(value, f"{where}: {key}")
        else:
            values[name] = convert(value, known[name], f"{where}: {key}")
    return values


def tune(target: Any, settings: Optional[Mapping[str, Any]], where: str) -> Any:
    """Sets the constants of ``settings`` on ``target`` (an instance: the
    class keeps its defaults). Returns ``target``."""
    cls = target if isinstance(target, type) else type(target)
    for name, value in check(cls, settings, where).items():
        setattr(target, name, value)
    return target


def defaults_of(cls: type) -> Dict[str, Any]:
    """The YAML keys of ``cls`` and their default values (for documentation)."""
    return {setting_key(name): value for name, value in tunable_constants(cls).items()}


def read_yaml(path: Path) -> Dict[str, Any]:
    """A YAML mapping; an empty dict when the file does not exist."""
    path = Path(path)
    if not path.is_file():
        return {}
    with path.open(encoding="utf-8") as file:
        try:
            data = yaml.safe_load(file)
        except yaml.YAMLError as error:
            raise ValueError(f"{path.name}: {error}") from None
    if data is None:
        return {}
    if not isinstance(data, dict):
        raise ValueError(f"{path.name}: the file must contain a mapping")
    return data
