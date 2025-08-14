from dataclasses import dataclass
from enum import Enum, auto
from typing import List, AnyStr

import yaml
import os


@dataclass
class Position:
    x: int
    y: int


class PlayerState(Enum):
    LITTLE = auto()


@dataclass
class Game:
    level: AnyStr
    score: int
    coins: int
    life: int
    inventory: List[AnyStr]
    state: PlayerState


class Save:
    player: str
    position: Position
    game: Game

    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Save, cls).__new__(cls)
            with open(os.path.join("save.yaml")) as save_file:
                save = yaml.safe_load(save_file)
                cls._instance.player = save["player"]
                cls._instance.position = Position(
                    save["position"]["x"], save["position"]["y"]
                )
                game_data = save["game"]
                cls._instance.game = Game(
                    game_data["level"],
                    game_data["score"],
                    game_data["coins"],
                    game_data["life"],
                    game_data["inventory"],
                    PlayerState[game_data["state"].upper()],
                )
        return cls._instance
