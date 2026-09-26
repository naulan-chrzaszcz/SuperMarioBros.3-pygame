# Map Editor

A 2D tile map editor for the JSON maps loaded by `SuperMarioBros3.pyw`.

## Requirements

- Python 3.8+
- Pygame 2
- PyYAML

Install dependencies from the repository root:

```bash
python -m pip install -r requirements.txt
```

## Run

Double-click `map_editor/MapEditor.pyw`, or run it without arguments from the
repository root:

```bash
python map_editor/MapEditor.pyw
```

The editor can also be opened from the game: choose `MAP EDITOR` on the title
screen (or `OPEN THE MAP EDITOR` in `CUSTOM LEVELS`). It then runs in the game
window and can **test the map** (see below).

The launcher opens:

- on the left, the maps of `res/maps` with their size, and `+ New map`;
- on the right, the map name (for a new map), its size in tiles and the
  tileset, with a preview. The tileset of an existing map is the one recorded
  in the map file, otherwise the one used the last time, otherwise the first
  tileset that declares every tile of the map.
  Changing the size of an existing map resizes it.

Double-click a map or press `Enter` to open it; `Create` makes the new map file
in `res/maps` and opens it. `Tab` moves between the fields, the arrow keys
move in the map list and `Esc` quits. Leaving the editor with `Esc` goes back
to the launcher (the clipboard is kept, so blocks can be copied from one map to
another using the same tileset); closing the window quits.

The launcher remembers its choices in `map_editor/.launcher.json` (not
versioned).

### Command line

A map can also be opened directly, without the launcher:

```bash
python map_editor/MapEditor.pyw <map_path> [--sheet SHEET] [--size WIDTHxHEIGHT]
```

Examples:

```bash
# Create (or open) a level that is 100 tiles wide and 15 tiles high
python map_editor/MapEditor.pyw res/maps/level_1.json --size 100x15

# Edit the stage selection map with its own tileset
python map_editor/MapEditor.pyw res/maps/stage_menu.json --sheet res/sheets/choice_menu_stage.png
```

- `map_path` is opened with its own size when it exists, and is created on the
  first save otherwise.
- `--sheet` is the tileset image (default: the one recorded in the map,
  otherwise `res/sheets/level.png`).
- `--size` is measured in 16x16 tiles. It defaults to 29x15 (one game screen)
  for a new map; on an existing map it resizes it (content outside the new
  size is dropped when saving).

## Tileset metadata

The game finds the name of every placed tile in the YAML metadata of the
tileset, and cannot load a map that contains an undeclared tile. The editor
therefore reads the same metadata and color key as the game:

1. the `images` entry of `ressources.yaml` whose `path` is the sheet;
2. otherwise a `<sheet>.yaml` file next to the image (e.g. `res/sheets/level.yaml`).

The `behaviour` of a tile (`coin`, `question_block`, `brick`, `hurt`, `goal`,
see the header of `res/sheets/level.yaml`) is shown next to its name in the
preview and in the status bar.

Undeclared tiles are darkened in the tileset and cannot be painted. Declare
them in the metadata file first. If the sheet has no metadata at all, every
tile can be used.

## Window layout

Everything is in a single resizable window:

- left: the map, drawn with pixel-perfect integer zoom;
- right: the selected tile (or entity) preview, the tool buttons, the tileset
  (or the entity palette) and a reminder of the shortcuts;
- bottom: a status bar with the hovered cell, its tile name, entity and collision,
  the map size, the zoom and the mode, plus messages (save result, warnings).

An asterisk in the window title indicates unsaved changes.

## Controls

### Map

| Action | Control |
| --- | --- |
| Paint the selected tile | Left click or drag |
| Erase | Right click or drag |
| Fill / erase a rectangle | `Shift` + left / right drag |
| Pick the tile under the cursor (eyedropper) | Middle click |
| Pan | Middle drag, mouse wheel, `Shift` + wheel (horizontal), arrow keys (`Shift` = one screen) |
| Zoom at the cursor | `Ctrl` + wheel, `+` / `-` |
| Fit the map height in the view | `Home` |

In **Collisions** mode (`C`), left click marks cells as solid and right click
clears them. Solid cells are always shown with a red overlay that can be
hidden with `O`.

### Entities

In **Entities** mode (`E` or the `Entities` button) the sidebar shows the
entity palette (click or mouse wheel to choose): Mario start, Goomba, Koopa
Troopa, Red Koopa Troopa, Super Mushroom, 1-Up Mushroom. Left click places the chosen entity,
right click removes the entity of the cell and middle click picks it. There is
one entity per cell; `Mario start` is unique, so placing it again moves it.
Entities are drawn in every mode, standing on the bottom of their cell like in
the game. Put a mushroom on a solid `?` block to hide it inside.

The types come from `res/entities.yaml` (shared with the game); an unknown type
found in a map is shown as a magenta cross.

### Level settings

Below the undo buttons, the sidebar sets the settings of the level, saved in
the `level` block of the map. They are not part of the undo history: change
them back with the same buttons.

- `Time`: `-` / `+` by 50 seconds; under 50 goes back to the default of
  `res/rules.yaml` (300);
- `Sky`: click to go through Default, Day, Sunset, Night and Cave;
- `Music`: click to go through the musics of `ressources.yaml` (Default is the
  one of `res/rules.yaml`).

A `name` written by hand in the `level` block is kept and shown in the
`CUSTOM LEVELS` list of the game.

### Selection, copy and paste

| Action | Control |
| --- | --- |
| Select mode | `S` or the `Select` button, then drag on the map (right click: deselect) |
| Select the whole map | `Ctrl+A` |
| Copy / cut the selection | `Ctrl+C` / `Ctrl+X` (or the `Copy` / `Cut` buttons) |
| Clear the selection | `Delete` or `Backspace` (or `Clear`) |
| Paste | `Ctrl+V` (or `Paste`): the block follows the mouse, left click pastes it (as many times as needed) |
| Rotate the block being pasted | `R` (`Shift+R`: other way) |
| Stop pasting / deselect | Right click or `Esc` |

Copies keep the tiles (with their animation and rotation), the collisions and
the entities. Cells that have no tile, no collision and no entity are
transparent: pasting leaves the map unchanged there. Every paste, cut or clear is a single undo step.

### Tools

| Action | Control |
| --- | --- |
| Rotate the tile (counter-clockwise, as in the game) | `R` (`Shift+R`: other way) |
| Horizontal / vertical animation frames | `Frames X` / `Frames Y` buttons |
| Switch between tiles and collisions | `C`, or the `Tiles` / `Solid` buttons |
| Entities mode (and back to tiles) | `E`, or the `Entities` button |
| Toggle the grid | `G` |
| Toggle the solid overlay | `O` |
| Undo / redo | `Ctrl+Z` / `Ctrl+Y` (or `Ctrl+Shift+Z`) |
| Save | `Ctrl+S` |
| Test the map in the game (saves it first) | `F5` or `Play the map`, only when the editor was opened from the game. `Esc` in the level (twice) comes back to the editor, with its undo history |
| Close the map (back to the launcher) | `Esc` (press twice if there are unsaved changes; the first `Esc` stops pasting or deselects) |
| Quit | Close the window |

In the tileset, left click selects a tile and the mouse wheel moves the
selection through the declared tiles. Only one animation axis can have more
than one frame, and animations cannot go past the tileset bounds.

## Code structure

The editor follows a model / view / controller split:

- `src/outputs/`: the JSON map format (`Map`) and the immutable `Tile` value.
- `src/models/`: pure data without drawing code: the edited map with its
  undo/redo history (`MapEditorModel`), the tool settings (`EditorState`) and
  the tileset with its metadata (`Tileset`), the copied cells (`Clipboard`),
  the entity types (`EntityType`) and the launcher choices (`LauncherModel`).
- `src/views/`: the camera (zoom and scrolling), the cached tile and entity
  renderers and the map, sidebar and status bar views.
- `src/controllers/`: the map interactions, the sidebar clicks and the global
  shortcuts / event routing.
- `src/launcher.py` and `src/application.py`: build the launcher and the
  editor, and run their main loop.

Run the tests from the repository root:

```bash
python -m unittest discover -s tests
```

## Output format

The editor writes the same JSON structure consumed by the game:

```json
{
  "tiles": [
    ["-1,-1", "0+3,0&1", "1,0"]
  ],
  "collidables": [
    [false, true, true]
  ],
  "entities": [
    {"type": "goomba", "x": 0, "y": 0}
  ],
  "sheet": "res/sheets/level.png",
  "level": {"timeLimit": 200, "sky": [16, 24, 64], "music": "overworld"}
}
```

`entities` is only written when the map has some; `x` / `y` are cells.
`level` is only written when a setting differs from the defaults.

`sheet` is the tileset the map was drawn with, relative to the repository
root: the game uses it to know which image the coordinates refer to. Maps
without it still load (the game then looks for a tileset that declares every
tile of the map).

`collidables` are the solid cells of the level: Mario stands on them and hits
them. Paint them in the `Collisions` mode; a tile that is not marked solid is
only decoration, even if it looks like a floor.

Each tile uses this encoding:

```text
x[+xFrames],y[+yFrames][&quarterTurns]
```

- `-1,-1` means that the cell is empty.
- `+N` sets the number of consecutive animation frames.
- `&N` stores rotation in quarter turns (`1` = 90 degrees).
