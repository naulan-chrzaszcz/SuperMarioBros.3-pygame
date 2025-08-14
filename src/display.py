from pygame import Surface

from src.inputs.config import Config


class Display(Surface):
    _instance = None

    def __init__(self):
        config = Config()
        super().__init__((config.display.width, config.display.height))

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Display, cls).__new__(cls)
        return cls._instance
