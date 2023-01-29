from unittest import TestCase

from fr.naulan.supermariobros.src.entities.player import Player
from fr.naulan.supermariobros.src.maps.engine import MapsEngine


class MapsEngineTest(TestCase):
    def test_empty_map(self):
        """
            Test with full empty tiles
        """
        maps_engine = MapsEngine()

        raw_data = open("./res/matrices/empty.txt", "r")
        maps_engine.new(raw_data.readlines(), raw_data.name, False)
        self.assertTrue(len(maps_engine.data) == 1, "Have a map generated")

        empty_map = maps_engine.data[0]
        self.assertTrue(len(empty_map.data) == 0, "Is really empty")

    def test_player(self):
        """
            Test with only player on the map
        """
        maps_engine = MapsEngine()

        raw_data = open("./res/matrices/player.txt", "r")
        maps_engine.new(raw_data.readlines(), raw_data.name, False)
        self.assertTrue(len(maps_engine.data) == 1, "Have a map generated")

        player_map = maps_engine.data[0]
        self.assertTrue(len(player_map.data) == 1, "Have player into the list of entities")
        self.assertTrue(isinstance(player_map.player, Player), "Is really a player ?")

        player = player_map.player
        self.assertTrue(player.x == 4*16, "Generated at a good position on x axis")
        self.assertTrue(player.y == 16, "Generated at a good position on y axis")
