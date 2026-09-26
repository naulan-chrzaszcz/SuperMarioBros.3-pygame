"""Reads ``ressources.yaml``: images, maps, sounds and musics, by id."""

from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING, Dict, Mapping

import yaml
from pygame import Surface, image

from ..constants import PROJECT_ROOT, RESSOURCES_FILE

if TYPE_CHECKING:
    from .map import TileBehaviour


class Ressources:
    """Images, tile names, maps, sounds and musics declared in ``ressources.yaml``.

    Images are converted for the screen, so a display mode has to be set before
    loading them.
    """

    def __init__(
        self,
        images: Mapping[str, Surface],
        metadata: Mapping[str, Dict[str, str]],
        maps: Mapping[str, dict],
        sounds: Mapping[str, Path] = None,
        musics: Mapping[str, Path] = None,
        behaviours: Mapping[str, Dict[str, "TileBehaviour"]] = None,
    ):
        self.images = dict(images)
        self.metadata = dict(metadata)
        self.maps = dict(maps)
        self.sounds = dict(sounds or {})
        self.musics = dict(musics or {})
        # Behaviours of the named tiles of each image (coins, blocks...).
        self.behaviours = dict(behaviours or {})

    def image(self, name: str) -> Surface:
        try:
            return self.images[name]
        except KeyError:
            raise KeyError(f"Image {name!r} is not declared in ressources.yaml") from None

    def load_map(self, name: str):
        """Builds the map ``name`` with the tileset declared by its ``sheet`` key."""
        from .map import Map

        try:
            entry = self.maps[name]
        except KeyError:
            raise KeyError(f"Map {name!r} is not declared in ressources.yaml") from None
        sheet = entry["sheet"]
        if sheet not in self.metadata:
            raise KeyError(f"Map {name!r}: image {sheet!r} has no metadata file")
        with Path(entry["path"]).open(encoding="utf-8") as map_file:
            data = json.load(map_file)
        return Map(self.image(sheet), self.metadata[sheet], data, self.behaviours.get(sheet))

    @staticmethod
    def read_metadata(path: Path) -> Dict[str, str]:
        """Tile names of a sheet, indexed by ``"x,y"`` tile coordinates."""
        with Path(path).open(encoding="utf-8") as metadata_file:
            metadata = yaml.safe_load(metadata_file) or {}
        return {
            f"{tile['coordinate']['x']},{tile['coordinate']['y']}": str(tile["name"])
            for tile in metadata.get("tiles", [])
        }

    @staticmethod
    def read_behaviours(path: Path) -> Dict[str, "TileBehaviour"]:
        """What the named tiles of a sheet do in a level (``behaviour`` and
        ``becomes`` keys of its tiles), indexed by tile name."""
        from .map import TileBehaviour

        with Path(path).open(encoding="utf-8") as metadata_file:
            metadata = yaml.safe_load(metadata_file) or {}
        behaviours = {}
        for tile in metadata.get("tiles", []):
            if tile.get("behaviour") is not None:
                behaviours[str(tile["name"])] = TileBehaviour.parse(
                    tile["behaviour"], tile.get("becomes"), f"{Path(path).name}: tile {tile['name']!r}"
                )
            elif tile.get("becomes") is not None:
                raise ValueError(
                    f"{Path(path).name}: tile {tile['name']!r} has 'becomes' without 'behaviour'")
        return behaviours

    @classmethod
    def load(cls, path: Path = RESSOURCES_FILE, root: Path = PROJECT_ROOT) -> "Ressources":
        with Path(path).open(encoding="utf-8") as ressources_file:
            ressources = yaml.safe_load(ressources_file) or {}

        images, metadata, behaviours = {}, {}, {}
        for entry in ressources.get("images", []):
            surface = image.load(str(root / entry["path"])).convert()
            color_key = entry.get("colorKey")
            if color_key is not None:
                surface.set_colorkey((color_key["r"], color_key["g"], color_key["b"]))
            images[entry["id"]] = surface
            if entry.get("metadata") is not None:
                metadata[entry["id"]] = cls.read_metadata(root / entry["metadata"])
                behaviours[entry["id"]] = cls.read_behaviours(root / entry["metadata"])

        maps = {}
        for entry in ressources.get("maps", []):
            maps[entry["id"]] = {
                "path": root / entry["path"],
                # The tileset of a map is the image with the same id, unless told.
                "sheet": entry.get("sheet", entry["id"]),
            }
        sounds = cls._audio_files(ressources, "sounds", root)
        musics = cls._audio_files(ressources, "musics", root)
        return cls(images, metadata, maps, sounds, musics, behaviours)

    @staticmethod
    def _audio_files(ressources: dict, section: str, root: Path) -> Dict[str, Path]:
        files = {}
        for entry in ressources.get(section) or []:
            path = root / entry["path"]
            if not path.is_file():
                raise ValueError(
                    f"ressources.yaml: {section} {entry['id']!r}: file {entry['path']} not found")
            files[str(entry["id"])] = path
        return files
