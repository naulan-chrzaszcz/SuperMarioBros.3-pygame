import os

from unittest import TestCase
from src.entities.entity import Entity

from src.maps.generator import MapsGenerator

class MapsGeneratorTest(TestCase):
    def setUp(self):
        self.generator = MapsGenerator()

    def test_empty_map(self):
        """
            Test with full empty tiles
        """
        with open(os.path.join(os.path.dirname(__file__), "res\\matrices\\empty.txt"), "r") as raw_data:
            self.generator.new(raw_data.readlines(), raw_data.name, False)

        self.assertTrue(len(self.generator.data) >= 1, "Have a map generated")
        empty_map = self.generator.data[0]
        self.assertTrue(len(empty_map.data) == 0, "Is really empty")        
        
        self.generator.data.clear()

    def test_player(self):
        """
            Test with only player on the map
        """
        with open(os.path.join(os.path.dirname(__file__), "res\\matrices\\player.txt"), "r") as raw_data:
            self.generator.new(raw_data.readlines(), raw_data.name, False)

        self.assertTrue(len(self.generator.data) >= 1, "Have a map generated")
        player_map = self.generator.data[0]
        self.assertTrue(len(player_map.data.sprites()) == 1, "Have player into the list of entities")
        self.assertTrue(isinstance(player_map.player, Entity), "Is really a player ?")

        player = player_map.player
        self.assertTrue(player.x == 4*MapsGenerator.TILE_SIZE, "Generated at a good position on x axis")
        self.assertTrue(player.y == MapsGenerator.TILE_SIZE, "Generated at a good position on y axis")

        self.generator.data.clear()
