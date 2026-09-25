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

From the repository root:

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
- `--sheet` is the tileset image (default: `res/sheets/level.png`).
- `--size` is measured in 16x16 tiles. It defaults to 29x15 (one game screen)
  for a new map; on an existing map it resizes it (content outside the new
  size is dropped when saving).

## Tileset metadata

The game finds the name of every placed tile in the YAML metadata of the
tileset, and cannot load a map that contains an undeclared tile. The editor
therefore reads the same metadata and color key as the game:

1. the `images` entry of `ressources.yaml` whose `path` is the sheet;
2. otherwise a `<sheet>.yaml` file next to the image (e.g. `res/sheets/level.yaml`).

Undeclared tiles are darkened in the tileset and cannot be painted. Declare
them in the metadata file first. If the sheet has no metadata at all, every
tile can be used.

## Window layout

Everything is in a single resizable window:

- left: the map, drawn with pixel-perfect integer zoom;
- right: the selected tile preview, the tool buttons, the tileset and a
  reminder of the shortcuts;
- bottom: a status bar with the hovered cell, its tile name and collision,
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

### Tools

| Action | Control |
| --- | --- |
| Rotate the tile (counter-clockwise, as in the game) | `R` (`Shift+R`: other way) |
| Horizontal / vertical animation frames | `Frames X` / `Frames Y` buttons |
| Switch between tiles and collisions | `C`, or the `Tiles` / `Collisions` buttons |
| Toggle the grid | `G` |
| Toggle the solid overlay | `O` |
| Undo / redo | `Ctrl+Z` / `Ctrl+Y` (or `Ctrl+Shift+Z`) |
| Save | `Ctrl+S` |
| Quit | `Esc` or close the window (press twice if there are unsaved changes) |

In the tileset, left click selects a tile and the mouse wheel moves the
selection through the declared tiles. Only one animation axis can have more
than one frame, and animations cannot go past the tileset bounds.

## Code structure

The editor follows a model / view / controller split:

- `src/outputs/`: the JSON map format (`Map`) and the immutable `Tile` value.
- `src/models/`: pure data without drawing code: the edited map with its
  undo/redo history (`MapEditorModel`), the tool settings (`EditorState`) and
  the tileset with its metadata (`Tileset`).
- `src/views/`: the camera (zoom and scrolling), the cached tile renderer and
  the map, sidebar and status bar views.
- `src/controllers/`: the map interactions, the sidebar clicks and the global
  shortcuts / event routing.
- `src/application.py`: builds everything and runs the main loop.

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
  ]
}
```

Each tile uses this encoding:

```text
x[+xFrames],y[+yFrames][&quarterTurns]
```

- `-1,-1` means that the cell is empty.
- `+N` sets the number of consecutive animation frames.
- `&N` stores rotation in quarter turns (`1` = 90 degrees).
