from typing import Dict

from pygame import Surface


class Gallery(object):
    images: Dict[int, Surface]

    def __init__(self, images: Dict[int, Surface] = None) -> None:
        self.images = {} if images is None else images

    def add(self, tile_code: int, image: Surface) -> None:
        self.images[tile_code] = image

    def get(self, tile_code: int) -> Surface:
        return self.images[tile_code]
