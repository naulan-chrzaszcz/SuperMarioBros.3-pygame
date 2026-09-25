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
| Move    | `Z Q S D` or arrows     | Menus, world map (hold to keep going), walk in a level |
| Confirm | `A`, `Enter` or `Space` | Choose, skip the opening, enter a level; **jump** in a level (hold to jump higher) |
| Run     | `Shift` or `E`          | Run in a level (running jumps go higher)  |
| Back    | `Esc`                   | Pause a level (twice: leave it), world map → title screen → quit |

Keys can be changed in the `controls` section of `config.yaml`, with
[pygame key names](https://www.pygame.org/docs/ref/key.html).

## Title screen

- `START GAME`: the world map.
- `CUSTOM LEVELS`: every map of `res/maps` made with the map editor, to play it.
- `MAP EDITOR`: the map editor, in the game window. `F5` (or `Play the map`)
  saves the map and plays it right away; leaving the level comes back to the
  editor. Lives are not lost while testing.
- `QUIT`.

## Levels

Any map of `res/maps` (except the world maps of `ressources.yaml`) is a
playable level:

- the **solid** cells are the collisions painted in the editor (`Collisions`
  mode): a tile not marked solid is only decoration;
- Mario appears on the first ground from the left and the course is cleared
  when he reaches the right edge of the map (the time left gives points);
- tiles named `coin*` are collected, and solid `mystery_block*` tiles give a
  coin once when hit from below (they become `block`);
- falling out of the map or running out of time costs a life; with no life
  left it is game over.

On the world map, the `levelN` tile plays `res/maps/level_N.json` when there is
no `level_N` scene.

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
- `res/maps/*.json`: maps made with the map editor; each one records its
  tileset (`sheet`).
- `res/sheets/*.yaml`: tile names of a tileset. The world map needs a tile
  named `start`; a tile named `levelN` opens the level `level_N`.
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
  levels.py                playable maps of res/maps and their tileset
  platformer.py            Mario's movement and collisions (no pygame drawing)
  editor_bridge.py         runs the map editor in the game window
  font.py, hud.py          bitmap font and status bar
  sprite_animation.py      frame animation (frames cut once)
  tile.py                  a tile sprite
  inputs/                  config.yaml, save.yaml, ressources.yaml and map files
  scenes/                  intro, title screen, world card, world map,
                           custom level list, platform level
  entities/, blocks/       old prototypes, not used yet (except player.py)
tests/                     python -m unittest discover -s tests
```

Scenes receive a `GameContext` (config, ressources, save, font, HUD, maps,
display surface, level catalog, `open_editor` and `play_level`) instead of reaching global singletons, and react to
*actions* (`Action.CONFIRM`...) rather than raw keys.

### Adding a level

1. Draw the level with the map editor (from the game: `MAP EDITOR`), save it
   as `res/maps/level_1.json` and paint its solid cells. Test it with `F5`.
2. The world map plays it when the player confirms on the `level1` tile; with
   no map (and no `level_1` scene) it shows "LEVEL 1 COMING SOON".
3. A level that needs more than a map can still be a scene (subclass of
   `src.scenes.Scene`) registered in `src/game.py` as `level_1`: it wins over
   the map.

## Tests

```bash
SDL_VIDEODRIVER=dummy python -m unittest discover -s tests
```
