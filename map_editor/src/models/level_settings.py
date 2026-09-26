"""The ``"level"`` block of a map: its time limit, sky and music.

The game reads it (``src/inputs/map.py``, LevelSettings); a missing value uses
the default of ``res/rules.yaml``. Keys the editor does not change (``name``)
are kept as they are.
"""

from pathlib import Path
from typing import Any, Dict, Mapping, Optional, Tuple

import yaml

from ..constantes import RESSOURCES_FILE

Color = Tuple[int, int, int]

TIME_STEP = 50
# The default of res/rules.yaml: the first + starts from it.
DEFAULT_TIME = 300
MAX_TIME = 999
SKY_PRESETS: Tuple[Tuple[str, Optional[Color]], ...] = (
    ("Default", None),
    ("Day", (160, 220, 252)),
    ("Sunset", (248, 176, 120)),
    ("Night", (16, 24, 64)),
    ("Cave", (0, 0, 0)),
)


def load_musics(path: Path = RESSOURCES_FILE) -> Tuple[str, ...]:
    """The music ids of ``ressources.yaml``."""
    try:
        with Path(path).open(encoding="utf-8") as file:
            entries = (yaml.safe_load(file) or {}).get("musics") or []
    except (OSError, yaml.YAMLError):
        return ()
    return tuple(str(entry["id"]) for entry in entries if isinstance(entry, dict) and "id" in entry)


class LevelSettings:
    def __init__(self, data: Optional[Mapping[str, Any]] = None, musics: Optional[Tuple[str, ...]] = None):
        self.data: Dict[str, Any] = dict(data or {})
        self.musics = load_musics() if musics is None else tuple(musics)
        self._saved = dict(self.data)

    @property
    def changed(self) -> bool:
        """True while the settings differ from the saved ones."""
        return self.data != self._saved

    def mark_saved(self) -> None:
        self._saved = dict(self.data)

    def _set(self, key: str, value: Any) -> None:
        if value is None:
            self.data.pop(key, None)
        else:
            self.data[key] = value

    # ----------------------------------------------------------- time limit

    @property
    def time_limit(self) -> Optional[int]:
        return self.data.get("timeLimit")

    def change_time(self, steps: int) -> None:
        """Adds ``steps`` x 50 seconds; going under 50 goes back to the default."""
        current = self.time_limit
        if current is None:
            if steps > 0:
                self._set("timeLimit", DEFAULT_TIME)
            return
        value = current + steps * TIME_STEP
        self._set("timeLimit", None if value < TIME_STEP else min(value, MAX_TIME))

    @property
    def time_label(self) -> str:
        return f"Time: {self.time_limit}" if self.time_limit else "Time: default"

    # ------------------------------------------------------------------ sky

    @property
    def sky(self) -> Optional[Color]:
        sky = self.data.get("sky")
        return tuple(sky) if sky else None

    @property
    def sky_name(self) -> str:
        for name, color in SKY_PRESETS:
            if color == self.sky:
                return name
        return "Custom"

    def cycle_sky(self) -> None:
        names = [name for name, _ in SKY_PRESETS]
        index = names.index(self.sky_name) + 1 if self.sky_name in names else 0
        color = SKY_PRESETS[index % len(SKY_PRESETS)][1]
        self._set("sky", list(color) if color else None)

    # ---------------------------------------------------------------- music

    @property
    def music(self) -> Optional[str]:
        return self.data.get("music")

    def cycle_music(self) -> None:
        choices = (None, *self.musics)
        index = choices.index(self.music) + 1 if self.music in choices else 0
        self._set("music", choices[index % len(choices)])

    @property
    def music_label(self) -> str:
        return f"Music: {self.music or 'default'}"
