from dataclasses import dataclass

import yaml
import os


@dataclass
class Mixer:
    frequency: int
    size: int
    channels: int
    buffer: int


@dataclass
class Display:
    width: int
    height: int


@dataclass
class Screen:
    width: int
    height: int
    flags: int
    depth: int


@dataclass
class Mouse:
    visible: bool


class Config:
    framerate_limit: int
    skip_intro: bool
    mixer: Mixer
    display: Display
    screen: Screen
    mouse: Mouse

    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Config, cls).__new__(cls)
            with open(os.path.join("config.yaml")) as config_file:
                config = yaml.safe_load(config_file)
                cls._instance.framerate_limit = config["framerateLimit"]
                cls._instance.skip_intro = config["skipIntro"]
                mixer_data = config["mixer"]
                cls._instance.mixer = Mixer(
                    mixer_data["frequency"],
                    mixer_data["size"],
                    mixer_data["channels"],
                    mixer_data["buffer"],
                )
                cls._instance.display = Display(
                    config["display"]["width"], config["display"]["height"]
                )
                screen_data = config["screen"]
                cls._instance.screen = Screen(
                    screen_data["width"],
                    screen_data["height"],
                    screen_data["flags"],
                    screen_data["depth"],
                )
                cls._instance.mouse = Mouse(config["mouse"]["visible"])
        return cls._instance
