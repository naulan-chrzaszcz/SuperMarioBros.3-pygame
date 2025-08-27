from enum import Enum, auto
from pygame import image

import json
import yaml
import os


class RessourceType(Enum):
    IMAGES = auto()
    MAPS = auto()


class Ressources(dict):
    _instance = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Ressources, cls).__new__(cls)
            for type in list(RessourceType):
                cls._instance[type.name.lower()] = {}
                cls._instance["metadata"] = {}

            ressources = None
            with open(os.path.join("ressources.yaml")) as ressources_file:
                ressources = yaml.safe_load(ressources_file)

            for map_data in ressources["maps"]:
                with open(os.path.join(map_data["path"])) as map_file:
                    cls._instance["maps"][map_data["id"]] = json.load(map_file)

            for image_data in ressources["images"]:
                img = image.load(image_data["path"]).convert()
                if image_data.get("colorKey") is not None:
                    color_key = image_data["colorKey"]
                    img.set_colorkey((color_key["r"], color_key["g"], color_key["b"]))
                cls._instance["images"][image_data["id"]] = img

                if image_data.get("metadata") is not None:
                    metadata = None
                    with open(
                        os.path.join(image_data.get("metadata"))
                    ) as metadata_file:
                        metadata = yaml.safe_load(metadata_file)

                    cls._instance["metadata"][image_data["id"]] = {}
                    for mtdt in metadata["tiles"]:
                        cls._instance["metadata"][image_data["id"]][
                            f"{mtdt['coordinate']['x']},{mtdt['coordinate']['y']}"
                        ] = mtdt["name"]
        return cls._instance
