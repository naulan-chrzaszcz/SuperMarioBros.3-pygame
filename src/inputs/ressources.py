from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Mapping

import yaml
from pygame import Surface, image

from ..constants import PROJECT_ROOT, RESSOURCES_FILE


class Ressources:
    """Images, tile names and maps declared in ``ressources.yaml``.

    Images are converted for the screen, so a display mode has to be set before
    loading them.
    """

    def __init__(
        self,
        images: Mapping[str, Surface],
        metadata: Mapping[str, Dict[str, str]],
        maps: Mapping[str, dict],
    ):
        self.images = dict(images)
        self.metadata = dict(metadata)
        self.maps = dict(maps)

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
        return Map(self.image(sheet), self.metadata[sheet], data)

    @staticmethod
    def read_metadata(path: Path) -> Dict[str, str]:
        """Tile names of a sheet, indexed by ``"x,y"`` tile coordinates."""
        with Path(path).open(encoding="utf-8") as metadata_file:
            metadata = yaml.safe_load(metadata_file) or {}
        return {
            f"{tile['coordinate']['x']},{tile['coordinate']['y']}": str(tile["name"])
            for tile in metadata.get("tiles", [])
        }

    @classmethod
    def load(cls, path: Path = RESSOURCES_FILE, root: Path = PROJECT_ROOT) -> "Ressources":
        with Path(path).open(encoding="utf-8") as ressources_file:
            ressources = yaml.safe_load(ressources_file) or {}

        images, metadata = {}, {}
        for entry in ressources.get("images", []):
            surface = image.load(str(root / entry["path"])).convert()
            color_key = entry.get("colorKey")
            if color_key is not None:
                surface.set_colorkey((color_key["r"], color_key["g"], color_key["b"]))
            images[entry["id"]] = surface
            if entry.get("metadata") is not None:
                metadata[entry["id"]] = cls.read_metadata(root / entry["metadata"])

        maps = {}
        for entry in ressources.get("maps", []):
            maps[entry["id"]] = {
                "path": root / entry["path"],
                # The tileset of a map is the image with the same id, unless told.
                "sheet": entry.get("sheet", entry["id"]),
            }
        return cls(images, metadata, maps)
