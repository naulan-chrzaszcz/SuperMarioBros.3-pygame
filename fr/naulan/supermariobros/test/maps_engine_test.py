import os.path
from unittest import TestCase

from fr.naulan.supermariobros.src.maps.engine import MapsEngine


class MapsEngineTest(TestCase):
    maps_engine: MapsEngine

    def setUp(self) -> None:
        self.maps_engine = MapsEngine()

    def test_empty_map(self):
        raw_data = open("./res/matrices/empty.txt", "r")
        self.maps_engine.new(raw_data.readlines(), raw_data.name)
        self.assertTrue(len(self.maps_engine.data) == 1)

        empty_map = self.maps_engine.data[0]
        self.assertTrue(empty_map.data.empty())
