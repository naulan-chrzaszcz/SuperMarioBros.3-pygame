from unittest import TestCase

from fr.naulan.supermariobros.src.entities.player import Player
from fr.naulan.supermariobros.src.maps.engine import MapsEngine


class MapsEngineTest(TestCase):
    def test_empty_map(self):
        maps_engine = MapsEngine()

        raw_data = open("./res/matrices/empty.txt", "r")
        maps_engine.new(raw_data.readlines(), raw_data.name, False)
        self.assertTrue(len(maps_engine.data) == 1)

        empty_map = maps_engine.data[0]
        self.assertTrue(len(empty_map.data) == 0)

    def test_player(self):
        maps_engine = MapsEngine()

        raw_data = open("./res/matrices/player.txt", "r")
        maps_engine.new(raw_data.readlines(), raw_data.name, False)
        self.assertTrue(len(maps_engine.data) == 1)

        player_map = maps_engine.data[0]
        self.assertTrue(len(player_map.data) == 0)
        self.assertTrue(isinstance(player_map.player, Player))

        player = player_map.player
        self.assertTrue(player.x == 4*16)
        self.assertTrue(player.y == 16)
