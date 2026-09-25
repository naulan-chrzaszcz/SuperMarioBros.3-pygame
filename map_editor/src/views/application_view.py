import pygame

from ..constantes import FONT_SIZE, MAX_SIDEBAR_WIDTH, MIN_SIDEBAR_WIDTH, STATUS_BAR_HEIGHT
from .camera import Camera
from .sidebar_view import SidebarView


class ApplicationView:
    """The single editor window: map on the left, sidebar on the right and a
    status bar at the bottom. The window can be resized."""

    def __init__(self, sidebar: SidebarView, camera: Camera, size) -> None:
        self.sidebar = sidebar
        self.camera = camera
        self.screen = pygame.display.set_mode(size, pygame.RESIZABLE)
        self.font = pygame.font.SysFont("Arial", FONT_SIZE)
        self.map_rect = pygame.Rect(0, 0, 0, 0)
        self.sidebar_rect = pygame.Rect(0, 0, 0, 0)
        self.status_rect = pygame.Rect(0, 0, 0, 0)
        self._caption = None
        self.layout(self.screen.get_size())

    def layout(self, size) -> None:
        width, height = size
        sidebar_width = min(
            self.sidebar.preferred_width(),
            max(width * 2 // 5, MIN_SIDEBAR_WIDTH),
            MAX_SIDEBAR_WIDTH,
        )
        content_height = height - STATUS_BAR_HEIGHT
        self.map_rect = pygame.Rect(0, 0, width - sidebar_width, content_height)
        self.sidebar_rect = pygame.Rect(self.map_rect.right, 0, sidebar_width, content_height)
        self.status_rect = pygame.Rect(0, content_height, width, STATUS_BAR_HEIGHT)
        self.sidebar.layout(self.sidebar_rect)
        self.camera.set_viewport(self.map_rect)

    def set_caption(self, caption: str) -> None:
        if caption != self._caption:
            pygame.display.set_caption(caption)
            self._caption = caption
