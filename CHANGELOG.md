# Changelog

Notable changes of the project. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Added

- Per-entity settings in the map editor (`Alt` + click a placed entity):
  undoable overrides in map JSON, preserved by copy/paste and validated by
  the game before offering a map for play.
- `SETTINGS` on the title screen: audio and volumes, sharp pixels, skip intro,
  mouse cursor, framerate and the keys of every action, applied right away and
  written back to `config.yaml`.
- Data-driven entity behaviours: the `settings` of `res/entities.yaml` choose
  the effects of an entity (`movement`, `onStomp`, `onTouch`, `onKnock`,
  `onWake`, `collect`), so an entity needs no Python (`behaviour: generic`).
- A data-driven engine: `res/rules.yaml` (Mario's physics, scores, durations,
  time limit, sky, musics), `res/sprites.yaml` (animations of Mario, the HUD
  and the title screen), entity `behaviour`, `animations` and `settings` in
  `res/entities.yaml`, tile `behaviour` in the tileset metadata (`coin`,
  `question_block`, `brick`, `hurt`, `goal`). Typos are reported at start-up.
- Red Koopa Troopa, made only of data (turns back at ledges).
- Sound effects and musics, as named events mapped in `ressources.yaml`;
  `audio` section in `config.yaml`.
- Level settings in the map editor (time limit, sky, music), saved in the map.
- `docs/ARCHITECTURE.md` (how the game and the editor work, with diagrams),
  a docstring on every module and commented `ressources.yaml`.
- Entities, placed with the map editor (`Entities` mode, `E`) and playable in
  the game: Mario start, Goomba, Koopa Troopa (shell to kick), Super Mushroom
  and 1-Up Mushroom, declared in `res/entities.yaml`. Mushrooms can be hidden
  in `?` blocks; big Mario breaks bricks and survives one hit.
- Play the maps made with the editor: `CUSTOM LEVELS` and `MAP EDITOR` on the
  title screen, `F5` in the editor to test a map, `level_N.json` maps played
  from the world map.
- Map editor launcher (recent maps, new map, tileset choice) and copy / cut /
  paste / rotation of blocks of tiles.
- Map editor in a single window, with undo / redo, zoom, rectangle fill,
  eyedropper, collisions mode, status bar and shortcuts help.
- Contribution guide, code of conduct, issue and pull request templates and
  continuous integration.

### Changed

- The goomba and the mushrooms are pure data: their Python classes are gone and
  only the shell state machine of the koopa remains a class.
- Game engine refactor: scenes receive a `GameContext`, actions instead of raw
  keys, paths from the project root, validated settings, saves and maps.
- Uniform code style, now checked by `pycodestyle` and `isort` (`setup.cfg`)
  in the continuous integration: line length, import order, `from __future__
  import annotations` in every module, `Optional[X]` and f-strings everywhere.
- `map_editor/src/constantes.py` renamed to `constants.py` (English, like the
  rest of the code).

### Removed

- Unused prototypes (`src/blocks`, `src/camera.py` and the old entities).
