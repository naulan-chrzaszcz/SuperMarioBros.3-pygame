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

import sys
import os

from .map_editor_cli import MapEditorCLI
from src.tile_selection_surface import TileSelectionSurface
from src.commands_surface import CommandsSurface
from src.outputs.map import Map
from src.models import MapEditorModel
from src.views import MapEditorView
from src.controllers import MapEditorController

TILE_SIZE = 16
WINDOW_GAP = 10
FRAMERATE_LIMIT = 60

cli = MapEditorCLI.from_args()

if not os.path.exists(cli.sheet_path):
    print("Sheet file not found")
    sys.exit(-1)
sheet = pygame.image.load(cli.sheet_path)

pygame.font.init()
pygame.init()

map_window = Window(size=(1280, 720))
map_window.title = "SuperMarioBros3 - Map editor"
map_renderer = Renderer(map_window)
map_model = MapEditorModel(
    cli.map_width * TILE_SIZE,
    cli.map_height * TILE_SIZE,
    sheet,
)
map_view = MapEditorView((cli.map_width * TILE_SIZE, cli.map_height * TILE_SIZE))
map_controller = MapEditorController(map_model, map_view)

cmd_window = Window(size=(200, 300))
cmd_window.borderless = True
cmd_window.title = f"{map_window.title} - settings"
cmd_renderer = Renderer(cmd_window)
cmd_surface = CommandsSurface(200, 300)

def export_btn_on_click():
    Map.write(
        cli.map_name,
        map_model.tiles,
        map_model.collidables,
        map_model.width,
        map_model.height,
    )

cmd_surface.export_btn.on_click = export_btn_on_click

sheet_window = Window(size=(sheet.get_width(), sheet.get_height()))
sheet_window.borderless = True
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

    map_texture = Texture.from_surface(map_renderer, map_controller.view)
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
