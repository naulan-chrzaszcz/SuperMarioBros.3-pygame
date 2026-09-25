# Changelog

Notable changes of the project. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Added

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

- Game engine refactor: scenes receive a `GameContext`, actions instead of raw
  keys, paths from the project root, validated settings, saves and maps.

### Removed

- Unused prototypes (`src/blocks`, `src/camera.py` and the old entities).
