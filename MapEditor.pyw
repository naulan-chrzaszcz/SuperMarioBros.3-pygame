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
import sys
import os

from src.camera import Camera
from src.outputs.map import Map
from src.outputs.tile import Tile

TILE_SIZE = 16
WINDOW_COLOR_FILL = (0, 0, 0)
FONT_COLOR = (255, 255, 255)
FONT_SIZE = 15
BUTTON_COLOR = (64, 64, 64)
BUTTON_WIDTH = 100
BUTTON_HEIGHT = 25
BUTTON_GAP = 10
WINDOW_GAP = 10
TILE_SELECTION_COLOR = (255, 0, 0)
TILE_SELECTION_FRAME_WIDTH = 2
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
map_surface = pygame.Surface((TILE_SIZE * args.map_width, TILE_SIZE * args.map_height))
map_scaling_surface = pygame.Surface(map_window.size)
map_camera_width = TILE_SIZE * 29
map_camera_height = TILE_SIZE * 15
if args.map_width < 29:
    map_camera_width = TILE_SIZE * args.map_width
if args.map_height < 15:
    map_camera_height = TILE_SIZE * args.map_height
map_camera = Camera(
    0, 0, map_camera_width, map_camera_height, map_surface.width, map_surface.height
)
map_scale_x = map_camera.width / map_scaling_surface.width
map_scale_y = map_camera.height / map_scaling_surface.height
map_tile_selection_x = 0
map_tile_selection_y = 0
map_tiles = {}

cmd_window = Window(size=(200, 300))
cmd_window.borderless = True
cmd_window.always_on_top = True
cmd_window.title = f"{map_window.title} - settings"
cmd_renderer = Renderer(cmd_window)
cmd_surface = pygame.Surface((200, 300))
cmd_font = pygame.font.SysFont("Arial", FONT_SIZE)
cmd_rotation_btn = pygame.Rect(BUTTON_GAP, BUTTON_GAP, BUTTON_WIDTH, BUTTON_HEIGHT)
cmd_rotation_btn_val = 0
cmd_rotation_font = cmd_font.render("ROTATION", False, FONT_COLOR)
cmd_rotation_font_pos = (
    cmd_rotation_btn.left + BUTTON_WIDTH / 2 - cmd_rotation_font.width / 2,
    cmd_rotation_btn.top + BUTTON_HEIGHT / 2 - cmd_rotation_font.height / 2,
)
cmd_frames_x_btn_font = cmd_font.render("FRAMES X", False, FONT_COLOR)
cmd_frames_x_btn_font_pos = (
    cmd_rotation_btn.left,
    cmd_rotation_btn.top + BUTTON_HEIGHT + BUTTON_GAP,
)
cmd_frames_x_btn_up = pygame.Rect(
    cmd_frames_x_btn_font_pos[0] + cmd_frames_x_btn_font.width + BUTTON_GAP,
    cmd_rotation_btn.top + BUTTON_HEIGHT + BUTTON_GAP,
    BUTTON_WIDTH / 4,
    BUTTON_HEIGHT / 2,
)
cmd_frames_x_btn_up_font = cmd_font.render("↑", False, FONT_COLOR)
cmd_frames_x_btn_up_font_pos = (
    cmd_frames_x_btn_up.left
    + cmd_frames_x_btn_up.width / 2
    - cmd_frames_x_btn_up_font.width / 2,
    cmd_frames_x_btn_up.top
    + cmd_frames_x_btn_up.height / 2
    - cmd_frames_x_btn_up_font.height / 2,
)
cmd_frames_x_btn_down = pygame.Rect(
    cmd_frames_x_btn_font_pos[0] + cmd_frames_x_btn_font.width + BUTTON_GAP,
    cmd_frames_x_btn_up.bottom,
    BUTTON_WIDTH / 4,
    BUTTON_HEIGHT / 2,
)
cmd_frames_x_btn_down_font = cmd_font.render("↓", False, FONT_COLOR)
cmd_frames_x_btn_down_font_pos = (
    cmd_frames_x_btn_down.left
    + cmd_frames_x_btn_down.width / 2
    - cmd_frames_x_btn_down_font.width / 2,
    cmd_frames_x_btn_down.top
    + cmd_frames_x_btn_down.height / 2
    - cmd_frames_x_btn_down_font.height / 2,
)
cmd_frames_x_btn_val = 1
cmd_frames_y_btn_font = cmd_font.render("FRAMES Y", False, FONT_COLOR)
cmd_frames_y_btn_font_pos = (
    cmd_frames_x_btn_font_pos[0],
    cmd_frames_x_btn_down_font_pos[1] + BUTTON_HEIGHT / 2 + BUTTON_GAP,
)
cmd_frames_y_btn_up = pygame.Rect(
    cmd_frames_x_btn_down.left,
    cmd_frames_x_btn_down.bottom + BUTTON_GAP,
    BUTTON_WIDTH / 4,
    BUTTON_HEIGHT / 2,
)
cmd_frames_y_btn_up_font = cmd_font.render("↑", False, FONT_COLOR)
cmd_frames_y_btn_up_font_pos = (
    cmd_frames_y_btn_up.left
    + cmd_frames_y_btn_up.width / 2
    - cmd_frames_y_btn_up_font.width / 2,
    cmd_frames_y_btn_up.top
    + cmd_frames_y_btn_up.height / 2
    - cmd_frames_y_btn_up_font.height / 2,
)
cmd_frames_y_btn_down = pygame.Rect(
    cmd_frames_y_btn_up.left,
    cmd_frames_y_btn_up.bottom,
    BUTTON_WIDTH / 4,
    BUTTON_HEIGHT / 2,
)
cmd_frames_y_btn_down_font = cmd_font.render("↓", False, FONT_COLOR)
cmd_frames_y_btn_down_font_pos = (
    cmd_frames_y_btn_down.left
    + cmd_frames_y_btn_down.width / 2
    - cmd_frames_y_btn_down_font.width / 2,
    cmd_frames_y_btn_down.top
    + cmd_frames_y_btn_down.height / 2
    - cmd_frames_y_btn_down_font.height / 2,
)
cmd_frames_y_btn_val = 1
cmd_export_btn = pygame.Rect(
    BUTTON_GAP,
    cmd_surface.height - BUTTON_HEIGHT - BUTTON_GAP,
    BUTTON_WIDTH,
    BUTTON_HEIGHT,
)
cmd_export_btn_font = cmd_font.render("EXPORT", False, FONT_COLOR)
cmd_export_btn_font_pos = (
    cmd_export_btn.left + BUTTON_WIDTH / 2 - cmd_export_btn_font.width / 2,
    cmd_export_btn.top + BUTTON_HEIGHT / 2 - cmd_export_btn_font.height / 2,
)

sheet_window = Window(size=(sheet.get_width(), sheet.get_height()))
sheet_window.borderless = True
sheet_window.always_on_top = True
sheet_window.title = f"{map_window.title} - tile selector"
sheet_renderer = Renderer(sheet_window)
sheet_surface = pygame.Surface((sheet.get_width(), sheet.get_height()))
sheet_selection_rect_x = 0
sheet_selection_rect_y = 0
sheet_selection_rect = pygame.Rect(
    sheet_selection_rect_x, sheet_selection_rect_y, TILE_SIZE, TILE_SIZE
)

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
        if getattr(event, "window", None) == map_window:
            if event.type == pygame.MOUSEMOTION:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                mouse_x = mouse_x * map_scale_x // TILE_SIZE
                mouse_y = mouse_y * map_scale_y // TILE_SIZE
                map_tile_selection_x = mouse_x * TILE_SIZE + map_camera.left
                map_tile_selection_y = mouse_y * TILE_SIZE + map_camera.top
            if event.type == pygame.MOUSEWHEEL:
                sheet_selection_rect_x = min(
                    sheet.width // TILE_SIZE - 1,
                    sheet_selection_rect_x + event.precise_x,
                )
                sheet_selection_rect_y = min(
                    sheet.height // TILE_SIZE - 1,
                    sheet_selection_rect_y + event.precise_y,
                )
                sheet_selection_rect_x = max(sheet_selection_rect_x, 0)
                sheet_selection_rect_y = max(sheet_selection_rect_y, 0)
                sheet_selection_rect.update(
                    sheet_selection_rect_x * TILE_SIZE,
                    sheet_selection_rect_y * TILE_SIZE,
                    TILE_SIZE,
                    TILE_SIZE,
                )
            if event.type == pygame.MOUSEBUTTONDOWN:
                tile = Tile(
                    sheet_selection_rect_x,
                    sheet_selection_rect_y,
                    cmd_frames_x_btn_val,
                    cmd_frames_y_btn_val,
                    cmd_rotation_btn_val,
                )
                tile.surface = pygame.transform.rotate(
                    sheet.subsurface(
                        (tile.x * TILE_SIZE, tile.y * TILE_SIZE), (TILE_SIZE, TILE_SIZE)
                    ).copy(),
                    cmd_rotation_btn_val,
                )
                map_tiles[(map_tile_selection_x, map_tile_selection_y)] = tile
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
                if event.key == pygame.K_UP:
                    map_camera.update(
                        map_camera.left, map_camera.top - map_camera.height
                    )
                if event.key == pygame.K_DOWN:
                    map_camera.update(
                        map_camera.left, map_camera.top + map_camera.height
                    )
                if event.key == pygame.K_RIGHT:
                    map_camera.update(
                        map_camera.left + map_camera.width, map_camera.top
                    )
                if event.key == pygame.K_LEFT:
                    map_camera.update(
                        map_camera.left - map_camera.width, map_camera.top
                    )
                if event.key == pygame.K_r:
                    cmd_rotation_btn_val += 90
                    cmd_rotation_btn_val %= 360
        if getattr(event, "window", None) == sheet_window:
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                sheet_selection_rect_x = mouse_x // TILE_SIZE
                sheet_selection_rect_y = mouse_y // TILE_SIZE
                sheet_selection_rect.update(
                    sheet_selection_rect_x * TILE_SIZE,
                    sheet_selection_rect_y * TILE_SIZE,
                    TILE_SIZE,
                    TILE_SIZE,
                )
        if getattr(event, "window", None) == cmd_window:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = pygame.mouse.get_pos()
                if cmd_rotation_btn.collidepoint(mouse_pos):
                    cmd_rotation_btn_val += 90
                    cmd_rotation_btn_val %= 360
                if cmd_frames_x_btn_up.collidepoint(mouse_pos):
                    cmd_frames_x_btn_val += 1
                if cmd_frames_x_btn_down.collidepoint(mouse_pos):
                    cmd_frames_x_btn_val = max(cmd_frames_x_btn_val - 1, 1)
                if cmd_frames_y_btn_up.collidepoint(mouse_pos):
                    cmd_frames_y_btn_val += 1
                if cmd_frames_y_btn_down.collidepoint(mouse_pos):
                    cmd_frames_y_btn_val = max(cmd_frames_y_btn_val - 1, 1)
                if cmd_export_btn.collidepoint(mouse_pos):
                    Map.write(args.map_name, map_tiles, map_surface.width, map_surface.height)

    map_surface.fill(WINDOW_COLOR_FILL)
    # Map Grid
    for line in range(map_surface.height // TILE_SIZE):
        pygame.draw.line(
            map_surface, (64, 64, 64), (0, line * 16), (map_surface.width, line * 16)
        )
    for row in range(map_surface.width // TILE_SIZE):
        pygame.draw.line(
            map_surface, (64, 64, 64), (row * 16, 0), (row * 16, map_surface.height)
        )
    # Map render
    for pos, tile in map_tiles.items():
        map_surface.blit(tile.surface, pos)
    # Display tile selection following the cursor
    map_surface.blit(
        pygame.transform.rotate(
            sheet.subsurface(
                (
                    (
                        sheet_selection_rect_x * TILE_SIZE,
                        sheet_selection_rect_y * TILE_SIZE,
                    ),
                    (TILE_SIZE, TILE_SIZE),
                )
            ),
            cmd_rotation_btn_val,
        ),
        (map_tile_selection_x, map_tile_selection_y),
    )
    map_scaling_surface.blit(
        pygame.transform.scale(
            map_surface.subsurface(map_camera), map_scaling_surface.size
        ),
        (0, 0),
    )
    map_texture = Texture.from_surface(map_renderer, map_scaling_surface)
    map_texture.draw(dstrect=(0, 0))

    cmd_surface.fill(WINDOW_COLOR_FILL)
    # Rotation tile setting draw
    pygame.draw.rect(cmd_surface, BUTTON_COLOR, cmd_rotation_btn, border_radius=1)
    cmd_surface.blit(cmd_rotation_font, cmd_rotation_font_pos)
    # Frames X tile setting draw
    cmd_surface.blit(cmd_frames_x_btn_font, cmd_frames_x_btn_font_pos)
    # Frames X increase setting draw
    pygame.draw.rect(cmd_surface, BUTTON_COLOR, cmd_frames_x_btn_up)
    cmd_surface.blit(cmd_frames_x_btn_up_font, cmd_frames_x_btn_up_font_pos)
    # Frames X decrease setting draw
    pygame.draw.rect(cmd_surface, BUTTON_COLOR, cmd_frames_x_btn_down)
    cmd_surface.blit(cmd_frames_x_btn_down_font, cmd_frames_x_btn_down_font_pos)
    # Frame X value
    cmd_surface.blit(
        cmd_font.render(str(cmd_frames_x_btn_val), False, FONT_COLOR),
        (
            cmd_frames_x_btn_font_pos[0]
            + cmd_frames_x_btn_font.width
            + cmd_frames_x_btn_up.width
            + BUTTON_GAP,
            cmd_frames_x_btn_font_pos[1],
        ),
    )
    # Frames Y tile setting draw
    cmd_surface.blit(cmd_frames_y_btn_font, cmd_frames_y_btn_font_pos)
    # Frames Y increase setting draw
    pygame.draw.rect(cmd_surface, BUTTON_COLOR, cmd_frames_y_btn_up)
    cmd_surface.blit(cmd_frames_y_btn_up_font, cmd_frames_y_btn_up_font_pos)
    # Frames Y decrease setting draw
    pygame.draw.rect(cmd_surface, BUTTON_COLOR, cmd_frames_y_btn_down)
    cmd_surface.blit(cmd_frames_y_btn_down_font, cmd_frames_y_btn_down_font_pos)
    # Frame Y value
    cmd_surface.blit(
        cmd_font.render(str(cmd_frames_y_btn_val), False, FONT_COLOR),
        (
            cmd_frames_y_btn_font_pos[0]
            + cmd_frames_y_btn_font.width
            + cmd_frames_y_btn_up.width
            + BUTTON_GAP,
            cmd_frames_y_btn_font_pos[1],
        ),
    )
    # Export setting draw
    pygame.draw.rect(cmd_surface, BUTTON_COLOR, cmd_export_btn)
    cmd_surface.blit(cmd_export_btn_font, cmd_export_btn_font_pos)
    command_texture = Texture.from_surface(cmd_renderer, cmd_surface)
    command_texture.draw(dstrect=(0, 0))

    sheet_surface.fill(WINDOW_COLOR_FILL)
    sheet_surface.blit(sheet, (0, 0))
    pygame.draw.rect(
        sheet_surface,
        TILE_SELECTION_COLOR,
        sheet_selection_rect,
        TILE_SELECTION_FRAME_WIDTH,
    )
    sheet_texture = Texture.from_surface(sheet_renderer, sheet_surface)
    sheet_texture.draw(dstrect=(0, 0))

    map_renderer.present()
    cmd_renderer.present()
    sheet_renderer.present()
