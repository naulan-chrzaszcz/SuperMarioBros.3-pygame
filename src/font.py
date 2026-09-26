"""Bitmap font used by every text of the game (menus, HUD, messages)."""

from __future__ import annotations

from typing import Dict, List

from pygame import SRCALPHA, Surface


class Font:
    """Bitmap font of ``custom_font.png``: 8x8 glyphs in the order of ``CHARSET``.

    The sheet has no ``Y``: it is built from the top of ``V`` and the stem of
    ``T``. Other missing characters (and spaces) are left blank.
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
        if "Y" not in self.glyphs and "V" in self.glyphs and "T" in self.glyphs:
            self.glyphs["Y"] = self._compose_y(self.glyphs["V"], self.glyphs["T"])

    @classmethod
    def _compose_y(cls, v: Surface, t: Surface) -> Surface:
        glyph = v.copy()
        # Rows of V (arms converging) then the bottom of T's stem.
        for row, (source, source_row) in enumerate(
            ((v, 0), (v, 1), (v, 2), (v, 4), (v, 5), (v, 6), (t, 6), (t, 7))
        ):
            glyph.blit(source, (0, row), (0, source_row, cls.WIDTH_FONT, 1))
        return glyph

    @staticmethod
    def wrap(text: str, width: int) -> List[str]:
        """Splits ``text`` in lines of at most ``width`` characters."""
        lines, line = [], ""
        for word in str(text).split():
            if line and len(line) + 1 + len(word) > width:
                lines.append(line)
                line = word
            else:
                line = f"{line} {word}".strip()
        return lines + ([line] if line else [])

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
