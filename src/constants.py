from pathlib import Path

# Every file is resolved from the project root, so the game also starts when it
# is launched from another directory (double click, shortcut, IDE...).
PROJECT_ROOT = Path(__file__).resolve().parent.parent
CONFIG_FILE = PROJECT_ROOT / "config.yaml"
RESSOURCES_FILE = PROJECT_ROOT / "ressources.yaml"
SAVE_FILE = PROJECT_ROOT / "save.yaml"
RULES_FILE = PROJECT_ROOT / "res" / "rules.yaml"
SPRITES_FILE = PROJECT_ROOT / "res" / "sprites.yaml"

TITLE = "Super Mario Bros. 3"

TILE_WIDTH = 16
TILE_HEIGHT = 16

# A frame longer than this (window dragged, breakpoint...) is cut, so that the
# game never jumps several tiles at once.
MAX_FRAME_TIME = 0.1

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
SAND = (255, 219, 161)
STATS_BACKGROUND = (175, 232, 226)
