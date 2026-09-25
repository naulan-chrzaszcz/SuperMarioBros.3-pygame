from dataclasses import dataclass, field
from typing import Optional

import pygame


@dataclass
class Tile:
    x: int
    y: int
    x_frames: int
    y_frames: int
    rotation: int
    surface: Optional[pygame.Surface] = field(
        repr=False, compare=False, default=None
    )
