# SuperMarioBros3 "like"
![illustration-TitleScreen](https://eapi.pcloud.com/getpubthumb?code=XZzBbJZwEoDuWD0fJJRWCIYAEUjpBhiDCek&linkpassword=undefined&size=1280x345&crop=0&type=auto)

[Map editor documentation](map_editor/README.md)

## Requirements

- Python 3.10+
- Pygame 2
- PyYAML

```bash
python -m pip install -r requirements.txt
```

## Run

Double-click `SuperMarioBros3.pyw`, or run `python SuperMarioBros3.pyw`. The
game finds its files from its own folder, whatever the working directory.

## Controls

| Action  | Keys (default)          | Use                                        |
|---------|-------------------------|--------------------------------------------|
| Move    | `Z Q S D` or arrows     | Walk on the world map (hold to keep going) |
| Confirm | `A`, `Enter` or `Space` | Start, skip the opening, enter a level     |
| Back    | `Esc`                   | World map → title screen → quit            |

Keys can be changed in the `controls` section of `config.yaml`, with
[pygame key names](https://www.pygame.org/docs/ref/key.html).

## Settings: `config.yaml`

Every setting is optional: a missing one keeps its default value, a misspelt
one is reported when the game starts.

| Setting                 | Meaning                                                   |
|-------------------------|-----------------------------------------------------------|
| `framerateLimit`        | Maximum frames per second                                 |
| `skipIntro`             | Start on the title screen instead of the splash screen   |
| `display`               | Size of the game image, in game pixels (464 x 240)        |
| `screen`                | Window size; `resizable`; `integerScaling: true` keeps sharp square pixels with black borders |
| `mouse.visible`         | Show the mouse cursor                                     |
| `controls`              | Keys of each action                                       |

The game image is always scaled without distortion (black bars fill the rest).

## Files

- `ressources.yaml`: images (`id`, `path`, optional `colorKey` and tile
  `metadata`) and maps (`id`, `path`, `sheet` = id of the tileset image).
- `res/maps/*.json`: maps made with the map editor.
- `res/sheets/*.yaml`: tile names of a tileset. The world map needs a tile
  named `start`; a tile named `levelN` opens the scene `level_N`.
- `save.yaml`: progress of the player (world, lives, score, coins...).

## Code structure

```
SuperMarioBros3.pyw        entry point
src/
  game.py                  composition root: window, files, scenes, main loop
  constants.py             paths (from the project root), sizes, colours
  scene_manager.py         current scene; scene changes happen after the update
  map_manager.py           maps of ressources.yaml, loaded on first use
  world_map.py             grid movement on the world map (no pygame drawing)
  font.py, hud.py          bitmap font and status bar
  sprite_animation.py      frame animation (frames cut once)
  tile.py                  a tile sprite
  inputs/                  config.yaml, save.yaml, ressources.yaml and map files
  scenes/                  intro, title screen, world card, world map
  entities/, blocks/       old prototypes, not used yet (except player.py)
tests/                     python -m unittest discover -s tests
```

Scenes receive a `GameContext` (config, ressources, save, font, HUD, maps,
display surface) instead of reaching global singletons, and react to
*actions* (`Action.CONFIRM`...) rather than raw keys.

### Adding a level

1. Draw the level with the map editor and declare it in `ressources.yaml`.
2. Write a scene (subclass of `src.scenes.Scene`) and register it in
   `src/game.py` as `level_1`, `level_2`...
3. The world map enters it when the player confirms on the `level1` tile;
   until then it shows "LEVEL 1 COMING SOON".

## Tests

```bash
SDL_VIDEODRIVER=dummy python -m unittest discover -s tests
```
