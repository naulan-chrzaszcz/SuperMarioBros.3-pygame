from __future__ import annotations

from typing import Dict

from pygame import SRCALPHA, Surface


class Font:
    """Bitmap font of ``custom_font.png``: 8x8 glyphs in the order of ``CHARSET``.

    The sheet has no ``Y``; missing characters (and spaces) are left blank.
    """

    WIDTH_FONT = 8
    HEIGHT_FONT = 8
    CHARSET = "ABCDEFGHIJKLMNOPQRSTUVWXZ0123456789"

    def __init__(self, sheet: Surface):
        self.sheet = sheet
        glyph_count = sheet.get_width() // self.WIDTH_FONT
        self.glyphs: Dict[str, Surface] = {
            char: sheet.subsurface((index * self.WIDTH_FONT, 0), (self.WIDTH_FONT, self.HEIGHT_FONT))
            for index, char in enumerate(self.CHARSET[:glyph_count])
        }

    def has_glyph(self, char: str) -> bool:
        return char.upper() in self.glyphs

    def size(self, message) -> tuple[int, int]:
        return len(str(message)) * self.WIDTH_FONT, self.HEIGHT_FONT

    def render(self, message) -> Surface:
        if message is None:
            return Surface((0, 0), SRCALPHA)
        message = str(message).upper()
        surface = Surface(self.size(message), SRCALPHA)
        for index, char in enumerate(message):
            glyph = self.glyphs.get(char)
            if glyph is not None:
                surface.blit(glyph, (index * self.WIDTH_FONT, 0))
        return surface
