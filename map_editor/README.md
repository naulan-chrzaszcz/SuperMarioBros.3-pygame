# Map Editor

A 2D tile map editor for the JSON maps loaded by `SuperMarioBros3.pyw`.

## Requirements

- Python 3.8+
- Pygame 2

Install dependencies from the repository root:

```bash
python -m pip install -r requirements.txt
```

## Run

From the repository root:

```bash
python map_editor/MapEditor.pyw <map_width> <map_height> <sheet_path> <map_path>
```

Example using the level tileset:

```bash
python map_editor/MapEditor.pyw 100 15 res/sheets/level.png res/maps/level_1.json
```

- `map_width` and `map_height` are measured in 16x16 tiles.
- `sheet_path` is the tileset image.
- `map_path` is loaded when it already exists and is created on export.
- When loading, the dimensions passed on the command line must match the map.

## Window layout

Everything is in a single window:

- left: the map, with the grid and a preview of the selected tile;
- top right: the settings panel;
- bottom right: the tile selector (the tileset is displayed at 2x).

## Controls

### Map

- Left click or drag: place the selected tile.
- Right click or drag: erase a tile.
- Arrow keys: move the camera by one viewport.
- `R`: rotate the tile by 90 degrees.
- `Ctrl+S`: save the map.
- `Esc`: close the editor.

### Tile selector

- Left click: select a tile.
- Mouse wheel: move the selection.

### Settings

- `ROTATION`: choose 0, 90, 180, or 270 degrees.
- `FRAMES X/Y`: configure a horizontal or vertical animation. Only one axis
  can contain multiple frames, and the count is limited by the tileset bounds.
- `COLLIDABLE`: switch to collision editing mode. Left click adds a collision
  cell and right click removes it.
- `EXPORT`: save the map.

An asterisk in the window title indicates unsaved changes.

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
