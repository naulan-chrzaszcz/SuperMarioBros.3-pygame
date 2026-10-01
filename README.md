# SuperMarioBros3 "like"

[![CI](https://github.com/naulan-chrzaszcz/SuperMarioBros.3-pygame/actions/workflows/ci.yml/badge.svg)](https://github.com/naulan-chrzaszcz/SuperMarioBros.3-pygame/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)
[![Contributions welcome](https://img.shields.io/badge/contributions-welcome-brightgreen.svg)](CONTRIBUTING.md)

A Super Mario Bros. 3 fan game made with Pygame, with its own map editor.
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
- Mario appears on the `Mario start` entity (or, without it, on the first
  ground from the left); the course is cleared when he reaches the right edge
  of the map (the time left gives points);
- what a tile does is its `behaviour` in the tileset metadata
  (`res/sheets/level.yaml`): `coin` tiles are collected, solid
  `question_block` tiles give a coin (or the item hidden in them) when hit from
  below and then look like their `becomes` tile, big Mario breaks `brick`
  tiles, `hurt` tiles hurt Mario and `goal` tiles clear the course;
- the editor gives each level its own time limit, sky colour and music (the
  `level` block of the map); the defaults are in `res/rules.yaml`;
- falling out of the map, touching an enemy as small Mario or running out of
  time costs a life; with no life left it is game over.

## Entities

Entities are placed with the map editor (`Entities` mode, key `E`) and saved in
the `entities` list of the map. They are declared in `res/entities.yaml`, shared
by the game and the editor:

| Entity         | Behaviour                                                         |
|----------------|-------------------------------------------------------------------|
| Mario start    | Where Mario appears (one per map)                                 |
| Goomba         | Walks and turns at walls; stomp it, touching it hurts Mario      |
| Koopa Troopa   | A stomp turns it into a shell; kick the shell into other enemies; it comes out after a while |
| Red Koopa      | The same koopa, red, turning back at the edge of a floor (only data: `red_koopa` in `res/entities.yaml`) |
| Super Mushroom | Makes Mario big (big Mario breaks bricks and survives one hit)   |
| 1-Up Mushroom  | One more life                                                     |

What an entity *does* is data too: its `settings` name the effects it uses
(`movement`, `onStomp`, `onTouch`, `onKnock`, `onWake`, `collect`), so a goomba
or a mushroom needs no Python at all (`behaviour: generic`). Only a real state
machine, like the shell of the koopa, has a class. The header of
`res/entities.yaml` lists every effect, and an unknown one is reported with the
known names when the game starts.

To tune a **single placed entity**, `Alt` + click it in the editor's `Entities`
mode. The panel changes only that entity, not the type in `res/entities.yaml`;
`Default` restores the type's value. The map stores only overrides, for example
`{"type": "goomba", "x": 3, "y": 6, "settings": {"speed": 64}}`.
The game validates these overrides when it lists the levels. See the
[editor controls](map_editor/README.md#entities).

A mushroom placed on a solid block (a `?` block) is hidden inside it and comes
out when the block is hit from below. Enemies are only woken up when they get
near the screen. Stomping several enemies without landing gives more and more
points, up to a 1UP.

On the world map, the `levelN` tile plays `res/maps/level_N.json` when there is
no `level_N` scene.

## A data-driven game

The code only knows ids and behaviours: the values live in YAML files, so the
game can be changed (or a new enemy made from an existing behaviour) without
writing Python. A misspelt name in any of them is reported when the game
starts, with the list of the known names.

| File                  | What it changes                                                          |
|-----------------------|--------------------------------------------------------------------------|
| `res/rules.yaml`      | Gameplay: Mario's physics (`player`), scores, durations, time limit, sky and music of the levels (`level`), world map (`worldMap`) |
| `res/sprites.yaml`    | Named animations cut in the images: Mario, world-map Mario, HUD layout, title screen |
| `res/entities.yaml`   | Entities: behaviour, animations, palette swaps, `settings` (speed, but also what a stomp or a touch does) |
| `res/sheets/*.yaml`   | Tile names and their `behaviour` (`coin`, `question_block`, `brick`, `hurt`, `goal`) |
| `ressources.yaml`     | Image, map, sound and music files, by id                                 |
| `res/maps/*.json`     | Levels made with the map editor, with their entities and `level` settings |
| `config.yaml`         | Window, controls, audio volume (the `SETTINGS` screen writes it)         |

Each section of `rules.yaml` and the `settings` of an entity set the
UPPER_CASE constants of a class, written in camelCase: `walkSpeed: 120` in
`player` sets `Body.WALK_SPEED` for Mario only. The constants in the code are
the defaults.

Sounds are *events* (`jump`, `coin`, `stomp`, `hurry`, `map_move`...) mapped to
files by the `sounds` list of `ressources.yaml`; an event without a file is
silent, and so is the game without an audio device.

## Settings: `config.yaml`

Every setting is optional: a missing one keeps its default value, a misspelt
one or a value of the wrong type is reported when the game starts. Boolean
settings require YAML `true`/`false` (not quoted strings), `framerateLimit`
must be a positive integer, and a key cannot belong to two actions. The
settings screen refuses to take another action's only key, and displays a
write error so you can retry without losing your changes.

| Setting                 | Meaning                                                   |
|-------------------------|-----------------------------------------------------------|
| `framerateLimit`        | Maximum frames per second                                 |
| `skipIntro`             | Start on the title screen instead of the splash screen   |
| `display`               | Size of the game image, in game pixels (464 x 240)        |
| `screen`                | Window size; `resizable`; `integerScaling: true` keeps sharp square pixels with black borders |
| `mouse.visible`         | Show the mouse cursor                                     |
| `controls`              | Keys of each action                                       |
| `audio`                 | `enabled`, `musicVolume` and `soundVolume` (0 to 1)       |

The game image is always scaled without distortion (black bars fill the rest).

`SETTINGS`, on the title screen, changes them without opening the file: audio
and volumes, sharp pixels, skip intro, mouse cursor, framerate and the keys of
each action (`CONTROLS`, then confirm a line and press the key to use).
Leaving the screen writes `config.yaml`; `DEFAULT SETTINGS` puts everything
back.

## Files

- `ressources.yaml`: images (`id`, `path`, optional `colorKey` and tile
  `metadata`), maps (`id`, `path`, `sheet` = id of the tileset image), `sounds`
  and `musics` (`id`, `path`).
- `res/maps/*.json`: maps made with the map editor; each one records its
  tileset (`sheet`), its `entities` (`type`, `x`, `y` in cells) and its `level`
  settings (`name`, `timeLimit`, `sky`, `music`).
- `res/entities.yaml`: entity types (`id`, `name`, `behaviour`, `image` = id of
  an image of `ressources.yaml`, `animations`, `facing`, `palette`, `settings`,
  `frame` shown in the editor, `flip`, `unique`, `description`); its header
  explains every key.
- `res/sprites.yaml`: animations of Mario, of the HUD and of the title screen.
- `res/rules.yaml`: gameplay values.
- `res/sheets/*.yaml`: tile names of a tileset and their `behaviour`. The world
  map needs a tile named `start`; a tile named `levelN` opens the level
  `level_N`.
- `save.yaml`: progress of the player (world, lives, score, coins...).
  Normal levels save on exit/clear and the game saves again on shutdown.
  Testing a level from the editor uses a disposable copy: score, coins,
  lives and power-ups earned in practice never change `save.yaml`.

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
  progress.py              real or disposable (practice) level progress
  platformer.py            Mario's movement and collisions (no pygame drawing)
  editor_bridge.py         runs the map editor in the game window
  font.py, hud.py          bitmap font and status bar
  animation.py             named animations of sprites.yaml (SpriteBank)
  audio.py                 sound events and music of ressources.yaml
  sprite_animation.py      tile strip animation (frames cut once)
  tile.py                  a tile sprite
  inputs/                  config.yaml, save.yaml, ressources.yaml, map files,
                           rules.yaml, sprites.yaml; tuning.py applies the
                           camelCase settings to the class constants
  scenes/                  intro, title screen, world card, world map,
                           custom level list, settings, platform level,
                           transient level effects
  entities/                entities.yaml catalog, data-driven Entity base
                           class, koopa, spawner; player.py (world map)
tests/                     python -m unittest discover -s tests
docs/ARCHITECTURE.md       how it all works at run time, with diagrams
```

[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) explains how the pieces work
together at run time (main loop, scenes, entities, editor), with diagrams.

Scenes receive a `GameContext` (config, ressources, save, font, HUD, maps,
display surface, level catalog, rules, sprite bank, audio, `open_editor`,
`play_level`, `apply_config`, `save_config` and `persist_progress`) instead of reaching global singletons, and react to
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

## Contributing

Contributions are welcome, from bug reports to new entities and levels: read
the [contribution guide](CONTRIBUTING.md) and the
[code of conduct](CODE_OF_CONDUCT.md). Changes are listed in the
[changelog](CHANGELOG.md); report security issues as explained in
[SECURITY.md](SECURITY.md).

## License and disclaimer

The source code is released under the [MIT license](LICENSE).

This is a non-commercial fan project, not affiliated with or endorsed by
Nintendo. Super Mario Bros. 3, its characters, graphics and sounds are
trademarks and copyrights of Nintendo; they are not covered by the MIT license.
