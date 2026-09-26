"""Lazy access to the maps declared in ``ressources.yaml`` (world map, world card)."""

from __future__ import annotations

from typing import Dict, Optional

from .inputs.map import Map
from .inputs.ressources import Ressources


class MapManager:
    """Maps of ``ressources.yaml``, built the first time they are used."""

    def __init__(self, ressources: Ressources):
        self.ressources = ressources
        self.maps: Dict[str, Map] = {}
        self.current: Optional[Map] = None

    def register(self, name: str, _map: Map) -> None:
        self.maps[name] = _map

    def get(self, name: str) -> Map:
        if name not in self.maps:
            self.maps[name] = self.ressources.load_map(name)
        return self.maps[name]

    def change_map(self, name: str) -> Map:
        self.current = self.get(name)
        return self.current

    def update(self, dt: float) -> None:
        self.current.update(dt)

    def draw(self, surface) -> None:
        self.current.draw(surface)
