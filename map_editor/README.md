# Map Editor

<img width="1498" height="543" alt="Capture d’écran du 2025-08-24 19-17-53" src="https://github.com/user-attachments/assets/53b59467-76b4-4981-801f-571cf75671fe" />

A basic 2D tile-based map editor using Python and Pygame.

## Requirements

- Python 3.8+
- Pygame (`pip install pygame`)

## How to Run

```bash
python MapEditor.pyw <map_width> <map_height> <sheet_path> <map_name>
```

- `<map_width>`: Width in number of 16x16 tiles.
- `<map_height>`: Height in number of 16x16 tiles.
- `<sheet_path>`: Path to the tileset image.
- `<map_name>`: Output map file name.

## Controls

- Mouse wheel: Scroll tile selection
- Mouse click on map: Place tile
- Mouse click on tileset: Select tile
- Arrow keys: Move camera
- R key: Rotate tile
- ESC: Exit

## Editor UI

- Change tile rotation (0°, 90°, 180°, 270°)
- Set tile animation frames (X/Y)
- Export to file

## Output Format

- Each tile is saved as:
```
x[+xFrames],y[+yFrames][&rotation]
```
- Empty tiles are -1,-1
- Tiles are separated by ;
- Rows are separated by newlines (\n)

### Example:

```
-1,-1;-1,-1;-1,-1;0+3,0&1;1,0
```
