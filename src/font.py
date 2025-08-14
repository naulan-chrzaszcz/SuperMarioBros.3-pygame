from pygame import SRCALPHA, Surface

from .inputs.ressources import Ressources


class Font:
    WIDTH_FONT = 8
    HEIGHT_FONT = 8

    _instance = None

    def __init__(self):
        self.font = Ressources()["images"]["font"]

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Font, cls).__new__(cls)
        return cls._instance

    def render(self, message: str) -> Surface:
        if message is None:
            return Surface((0, 0), SRCALPHA)
        message = str(message)

        ascii_code = [ord(char) for char in message]
        width_surface = len(ascii_code) * self.WIDTH_FONT
        message_surface = Surface((width_surface, self.HEIGHT_FONT), SRCALPHA)

        for n, code in enumerate(ascii_code):
            if code >= ord("A"):
                message_surface.blit(
                    self.font.subsurface(
                        ((code - ord("A")) * self.WIDTH_FONT, 0),
                        (self.WIDTH_FONT, self.HEIGHT_FONT),
                    ),
                    (n * self.WIDTH_FONT, 0),
                )
            elif code >= ord("0"):
                message_surface.blit(
                    self.font.subsurface(
                        (
                            ((ord("Z") - ord("A")) + (code - ord("0")))
                            * self.WIDTH_FONT,
                            0,
                        ),
                        (self.WIDTH_FONT, self.HEIGHT_FONT),
                    ),
                    (n * self.WIDTH_FONT, 0),
                )
        return message_surface
