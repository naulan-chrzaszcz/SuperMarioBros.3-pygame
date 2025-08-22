from typing import Dict, Tuple

from .tile import Tile


class Map:
    LINE_SEPARATOR = "\n"
    TILE_SEPARATOR = ";"
    TILE_COORD_SEPARATOR = ","
    TILE_FRAMES_SEPARATOR = "+"
    TILE_ROTATION_SEPARATOR = "&"

    @staticmethod
    def write(file_name: str, tiles: Dict[Tuple[int, int], Tile], width_map: int, height_map: int):
        map_data = {}
        for y in range(height_map // 16):
            for x in range(width_map // 16):
                map_data[(x * 16, y * 16)] = "-1,-1"
        
        for pos, tile in tiles.items():
            tile_data = f"{tile.x}"
            if tile.x_frames > 1:
                tile_data += f"{Map.TILE_FRAMES_SEPARATOR}{tile.x_frames}"
            tile_data += f"{Map.TILE_COORD_SEPARATOR}{tile.y}"
            if tile.y_frames > 1:
                tile_data += f"{Map.TILE_FRAMES_SEPARATOR}{tile.y_frames}"
            if tile.rotation > 0:
                tile_data += f"{Map.TILE_ROTATION_SEPARATOR}{tile.rotation // 90}"
            map_data[pos] = tile_data

        lines = []
        current_line = []
        last_y = None
        for (x, y), tile_data in sorted(map_data.items(), key=lambda item: (item[0][1], item[0][0])):
            if y != last_y and current_line:
                lines.append(Map.TILE_SEPARATOR.join(current_line))
                current_line = []
            current_line.append(tile_data)
            last_y = y

        if current_line:
            lines.append(Map.TILE_SEPARATOR.join(current_line))
        data = Map.LINE_SEPARATOR.join(lines)

        with open(file_name, "w") as file:
            file.write(data)
