"""
A simple map editor

Usage:
    python MapEditor.pyw <map_width> <map_height> <sheet_path> <map_name>

Arguments:
    <map_width>     Width is determined by a multiplier of tile size (16).
    <map_height>    Height is determined by a multiplier of tile size (16).
    <sheet_path>    Path to the sheet file.
    <map_name>      Map name file.
"""

import pygame

from pygame._sdl2 import Window, Texture, Renderer

import argparse
import json
import sys
import os

from src.tile_selection_surface import TileSelectionSurface
from src.commands_surface import CommandsSurface
from src.camera import Camera
from src.outputs.map import Map
from src.outputs.tile import Tile

TILE_SIZE = 16
WINDOW_GAP = 10
FRAMERATE_LIMIT = 60

parser = argparse.ArgumentParser(description="A simple map editor")
parser.add_argument(
    "map_width", type=int, help="Width is determined by a multiplier of tile size (16)"
)
parser.add_argument(
    "map_height",
    type=int,
    help="Height is determined by a multiplier of tile size (16)",
)
parser.add_argument("sheet_path", help="Path to the sheet file")
parser.add_argument("map_name", help="Path to write the map file")
args = parser.parse_args()

if not os.path.exists(args.sheet_path):
    print("Sheet file not found")
    sys.exit(-1)
sheet = pygame.image.load(args.sheet_path)

pygame.font.init()
pygame.init()

map_window = Window(size=(1280, 720))
map_window.title = "Map editor"
map_renderer = Renderer(map_window)
map_surface_tile = pygame.Surface(
    (TILE_SIZE * args.map_width, TILE_SIZE * args.map_height)
)
map_surface_collidable = pygame.Surface(
    (TILE_SIZE * args.map_width, TILE_SIZE * args.map_height), pygame.SRCALPHA
)
map_surface_collidable.set_alpha(50)
map_scaling_surface = pygame.Surface(map_window.size)
map_camera_width = TILE_SIZE * 29
map_camera_height = TILE_SIZE * 15
if args.map_width < 29:
    map_camera_width = TILE_SIZE * args.map_width
if args.map_height < 15:
    map_camera_height = TILE_SIZE * args.map_height
map_camera = Camera(
    0,
    0,
    map_camera_width,
    map_camera_height,
    map_surface_tile.width,
    map_surface_tile.height,
)
map_scale_x = map_camera.width / map_scaling_surface.width
map_scale_y = map_camera.height / map_scaling_surface.height
map_tile_selection_x = 0
map_tile_selection_y = 0
map_tiles = {}
map_collidables = {}

if os.path.exists(args.map_name):
    map_data = None
    with open(args.map_name) as map_file:
        map_data = json.load(map_file)

    for row, tiles in enumerate(map_data["tiles"]):
        for column, tile in enumerate(tiles):
            sheet_x, sheet_y = tile.split(Map.TILE_COORD_SEPARATOR)
            frames_x = "1"
            if sheet_x.count("+") == 1:
                sheet_x, frames_x = sheet_x.split("+")
            frames_y = "1"
            if sheet_y.count("+") == 1:
                sheet_y, frames_y = sheet_y.split("+")
            rotation = "0"
            if sheet_y.count("&") == 1:
                sheet_y, rotation = sheet_y.split("&")
            if frames_y.count("&") == 1:
                frames_y, rotation = frames_y.split("&")

            if sheet_x == "-1" and sheet_y == "-1":
                continue

            tile = Tile(
                int(sheet_x),
                int(sheet_y),
                int(frames_x),
                int(frames_y),
                int(rotation) * 90,
            )
            tile.surface = pygame.transform.rotate(
                sheet.subsurface(
                    (tile.x * TILE_SIZE, tile.y * TILE_SIZE),
                    (TILE_SIZE, TILE_SIZE),
                ).copy(),
                int(rotation) * 90,
            )
            map_tiles[(column * TILE_SIZE, row * TILE_SIZE)] = tile

    for row, collidables in enumerate(map_data["collidables"]):
        for column, collidable in enumerate(collidables):
            if collidable:
                map_collidables[(column * TILE_SIZE, row * TILE_SIZE)] = (
                        pygame.Rect(column * TILE_SIZE, row * TILE_SIZE, 16, 16)
                    )

cmd_window = Window(size=(200, 300))
cmd_window.borderless = True
cmd_window.always_on_top = True
cmd_window.title = f"{map_window.title} - settings"
cmd_renderer = Renderer(cmd_window)
cmd_surface = CommandsSurface(200, 300)

def export_btn_on_click():
    Map.write(
        args.map_name,
        map_tiles,
        map_collidables,
        map_surface_tile.width,
        map_surface_tile.height,
    )

cmd_surface.export_btn.on_click = export_btn_on_click

sheet_window = Window(size=(sheet.get_width(), sheet.get_height()))
sheet_window.borderless = True
sheet_window.always_on_top = True
sheet_window.title = f"{map_window.title} - tile selector"
sheet_renderer = Renderer(sheet_window)
tile_selection_surface = TileSelectionSurface(sheet)

map_window.show()
cmd_window.show()
sheet_window.show()

clock = pygame.time.Clock()
while True:
    dt = clock.tick(FRAMERATE_LIMIT) / 1000.0

    cmd_window.position = (
        map_window.position[0] + map_window.size[0] + WINDOW_GAP,
        map_window.position[1],
    )
    sheet_window.position = (
        cmd_window.position[0],
        cmd_window.position[1] + cmd_window.size[1] + WINDOW_GAP,
    )

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        # Map editor
        if getattr(event, "window", None) == map_window:
            map_camera.handle_event(event)

            if event.type == pygame.MOUSEMOTION:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                mouse_x = mouse_x * map_scale_x // TILE_SIZE
                mouse_y = mouse_y * map_scale_y // TILE_SIZE
                map_tile_selection_x = mouse_x * TILE_SIZE + map_camera.left
                map_tile_selection_y = mouse_y * TILE_SIZE + map_camera.top
            if event.type == pygame.MOUSEBUTTONDOWN:
                if not cmd_surface.collidable_btn.value:
                    tile = Tile(
                        tile_selection_surface.selection_x,
                        tile_selection_surface.selection_y,
                        cmd_surface.frames_x_btn.value,
                        cmd_surface.frames_y_btn.value,
                        cmd_surface.rotation_btn.value,
                    )
                    tile.surface = pygame.transform.rotate(
                        sheet.subsurface(
                            (tile.x * TILE_SIZE, tile.y * TILE_SIZE),
                            (TILE_SIZE, TILE_SIZE),
                        ).copy(),
                        cmd_surface.rotation_btn.value,
                    )
                    map_tiles[(map_tile_selection_x, map_tile_selection_y)] = tile
                else:
                    map_collidables[(map_tile_selection_x, map_tile_selection_y)] = (
                        pygame.Rect(map_tile_selection_x, map_tile_selection_y, 16, 16)
                    )
            if (
                event.type == pygame.KEYDOWN
                and event.key == pygame.K_ESCAPE
                or event.type == pygame.WINDOWCLOSE
            ):
                map_window.destroy()
                cmd_window.destroy()
                sheet_window.destroy()
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    cmd_surface.rotation_btn.on_click()
        # Sheet selection controls
        if getattr(event, "window", None) == sheet_window:
            tile_selection_surface.handle_event(event)
        # GUI controls
        if getattr(event, "window", None) == cmd_window:
            cmd_surface.handle_event(event)

    map_surface_tile.fill((0, 0, 0))
    map_surface_collidable.fill((0, 0, 0, 0))
    # Map Grid
    for line in range(map_surface_tile.height // TILE_SIZE):
        pygame.draw.line(
            map_surface_tile,
            (64, 64, 64),
            (0, line * 16),
            (map_surface_tile.width, line * 16),
        )
    for row in range(map_surface_tile.width // TILE_SIZE):
        pygame.draw.line(
            map_surface_tile,
            (64, 64, 64),
            (row * 16, 0),
            (row * 16, map_surface_tile.height),
        )
    # Map render
    for pos, tile in map_tiles.items():
        map_surface_tile.blit(tile.surface, pos)
    for pos, rect in map_collidables.items():
        pygame.draw.rect(map_surface_collidable, (255, 0, 0), rect)
    if not cmd_surface.collidable_btn.value:
        # Display tile selection following the cursor
        map_surface_tile.blit(
            pygame.transform.rotate(
                sheet.subsurface(
                    (
                        (
                            tile_selection_surface.selection_x * TILE_SIZE,
                            tile_selection_surface.selection_y * TILE_SIZE,
                        ),
                        (TILE_SIZE, TILE_SIZE),
                    )
                ),
                cmd_surface.rotation_btn.value,
            ),
            (map_tile_selection_x, map_tile_selection_y),
        )
    else:
        pygame.draw.rect(
            map_surface_collidable,
            (255, 0, 0),
            pygame.Rect(map_tile_selection_x, map_tile_selection_y, 16, 16),
        )
    map_scaling_surface.blit(
        pygame.transform.scale(
            map_surface_tile.subsurface(map_camera), map_scaling_surface.size
        ),
        (0, 0),
    )
    map_scaling_surface.blit(
        pygame.transform.scale(
            map_surface_collidable.subsurface(map_camera), map_scaling_surface.size
        ),
        (0, 0),
    )
    map_texture = Texture.from_surface(map_renderer, map_scaling_surface)
    map_texture.draw(dstrect=(0, 0))

    cmd_surface.draw()
    cmd_texture = Texture.from_surface(cmd_renderer, cmd_surface)
    cmd_texture.draw(dstrect=(0, 0))

    tile_selection_surface.draw()
    sheet_texture = Texture.from_surface(sheet_renderer, tile_selection_surface)
    sheet_texture.draw(dstrect=(0, 0))

    map_renderer.present()
    cmd_renderer.present()
    sheet_renderer.present()
