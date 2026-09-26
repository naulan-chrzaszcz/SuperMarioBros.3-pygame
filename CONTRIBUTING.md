# Contributing

Thanks for your interest in this Super Mario Bros. 3 fan game! Bug reports,
ideas, levels, code and documentation are all welcome, from beginners too.
Issues and pull requests may be written in English or in French
(*les contributions en français sont les bienvenues*).

By taking part in the project you agree to follow the
[code of conduct](CODE_OF_CONDUCT.md).

## Ways to contribute

- **Report a bug** or **suggest a feature** with the
  [issue templates](https://github.com/naulan-chrzaszcz/SuperMarioBros.3-pygame/issues/new/choose).
  Search the existing issues first.
- **Make a level** with the map editor and share it (see
  [Adding a level](#adding-a-level)).
- **Write code**: issues labelled `good first issue` are a nice start. For a
  big change (new mechanic, new file format...), open an issue first so that we
  can agree on the design before you spend time on it.
- **Improve the documentation**: the [README](README.md) and the
  [map editor documentation](map_editor/README.md).

## Development setup

You need Python 3.10 or newer and git.

```bash
git clone https://github.com/<your-account>/SuperMarioBros.3-pygame.git
cd SuperMarioBros.3-pygame
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
python -m pip install -r requirements-dev.txt
```

Run the game with `python SuperMarioBros3.pyw` and the map editor with
`python map_editor/MapEditor.pyw` (or from the game: `MAP EDITOR` on the title screen).

## Checks

Run these before opening a pull request; the continuous integration runs the
same ones on every push and pull request.

```bash
# Tests (the dummy video driver runs them without opening a window)
SDL_VIDEODRIVER=dummy python -m unittest discover -s tests
# Windows (PowerShell): $env:SDL_VIDEODRIVER="dummy"; python -m unittest discover -s tests

# Lint: unused imports, undefined names...
python -m pyflakes src map_editor tests SuperMarioBros3.pyw
```

Every fix or feature should come with a test in `tests/`:
`tests/test_game.py` for the game, `tests/test_map_editor.py` for the editor.
The tests drive the real code with fake events (see `LevelTestCase` and
`write_level` in `tests/test_game.py`), so most behaviours can be tested
without a screen.

## Code style

- Follow [PEP 8](https://peps.python.org/pep-0008/), 4 spaces, lines up to
  about 110 characters (see [.editorconfig](.editorconfig)).
- Start every module with a docstring that says its role (a test checks it).
  Add type hints to new functions and a docstring when the purpose is not
  obvious. Comment *why*, not *what*.
- Code, comments and identifiers are in English.
- Keep the logic testable: game rules (movement, collisions, entities) do not
  draw anything; the scenes and views do the drawing.
- Game scenes receive a `GameContext` instead of using globals, and react to
  *actions* (`Action.CONFIRM`...) rather than raw keys.
- The map editor keeps its model / view / controller split: models have no
  pygame drawing code, views do not change the models, controllers turn events
  into model changes.
- Paths are built from the project root (`src/constants.py`,
  `map_editor/src/constantes.py`), never from the working directory.

## Git workflow

1. Fork the repository and create a branch from `main` with a short
   descriptive name: `fix/koopa-shell-wall`, `feature/piranha-plant`,
   `docs/editor-shortcuts`.
2. Make small, focused commits. Write the commit title in the imperative mood,
   under about 70 characters (`Add the piranha plant`, `Fix the shell going
   through walls`), and explain the *why* in the body when it helps.
3. Keep your branch up to date with `main` (rebase or merge).
4. Open a pull request and fill in its template: what changes, why, how it was
   tested, and screenshots for anything visible.
5. A maintainer reviews it. Answer the comments with new commits; they will be
   squashed or merged when the pull request is accepted.

Please do not commit your own `save.yaml` or `config.yaml` changes, editor
state (`map_editor/.launcher.json`) or generated files (`__pycache__`,
virtual environments).

## Project tour

The [README](README.md#code-structure) describes the code structure and
[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) how it works at run time. The main
extension points:

### Adding a level

1. Draw it with the map editor on the `res/sheets/level.png` tileset, paint the
   solid cells (`C`) and place the entities (`E`), including `Mario start`.
2. Test it with `F5` from the in-game editor.
3. Save it as `res/maps/level_N.json`: the `levelN` tile of the world map plays
   it. Any other map of `res/maps` is listed in `CUSTOM LEVELS`.

### Changing a value

Look in the data files first (see "A data-driven game" in the README): speeds,
scores, durations, sprites and sounds are there, not in the code. To make a
new constant configurable, add it UPPER_CASE on its class: `rules.yaml` (or the
`settings` of an entity) can then set it in camelCase. List the constants that
must not change in the `NOT_TUNABLE` tuple of the class, and add the new value,
with its default, to `res/rules.yaml` (a test checks that the file matches the
code).

### Adding an entity

An entity that behaves like an existing one is only data: add it to
`res/entities.yaml` with the `behaviour` of the existing one and its own
`animations`, `palette` or `settings` (see `red_koopa`). For a new behaviour:

1. Write its class in `src/entities/`, as a subclass of `Entity`
   (`src/entities/entity.py`): list the animation names it needs in
   `ANIMATIONS`, put its tunable values in UPPER_CASE constants, and override
   `behave` (what it does each frame), `touch_mario` (stomp or side touch),
   `knock` and `image` (pick a frame in `self.animations`). `CAN_HIDE` hides
   it in a `?` block, `TURN_AT_LEDGES` makes `walk` turn back at ledges. It
   talks to the level only through the `Level` protocol (`hurt_mario`,
   `stomped`, `score`, `play_sound`...).
2. Register the class in `ENTITY_CLASSES` (`src/entities/spawner.py`).
3. Declare it in `res/entities.yaml`. The editor lists it right away; the game
   checks its behaviour, animations and settings when it starts.
4. Test it in `tests/test_game.py` (see `EntityTest`) or `tests/test_data.py`,
   and document it in the entity table of the README.

### Adding a sprite or a sound

- Sprites: add an animation to `res/sprites.yaml` (or to the entity) and ask
  for it by name with `context.sprites.animation(sprite, name)`.
- Sounds: add the file to `res/sounds/`, map an event id to it in the `sounds`
  list of `ressources.yaml` and play it with `context.audio.play("event")`.
  Musics work the same with `musics` and `context.audio.play_music("id")`.

### Adding a scene

Subclass `src.scenes.Scene`, register it in `src/game.py` and switch to it with
the scene manager. A scene named `level_N` replaces the map of the level `N`.

### Adding a tile type to the editor

Name the tiles in the tileset metadata (`res/sheets/*.yaml` or the `metadata`
of the image in `ressources.yaml`) and give them a `behaviour` (`coin`,
`question_block` with `becomes`, `brick`, `hurt`, `goal`) to make them do
something in a level. A tileset without any behaviour falls back on the names
`coin*`, `mystery_block*` and `brick*`.

## Assets and copyright

Super Mario Bros. 3, its characters, graphics and sounds belong to Nintendo.
This is a non-commercial fan project made for learning. Only add assets that
you made yourself or that can legally be shared, and never add ripped music or
assets from other commercial games. The source code is under the
[MIT license](LICENSE): by contributing you agree that your code is released
under this license.

## Questions

Open an issue with the `question` label, or start a discussion in your pull
request. Thank you for helping!
