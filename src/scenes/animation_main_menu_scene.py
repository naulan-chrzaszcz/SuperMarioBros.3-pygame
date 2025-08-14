from pygame import KEYDOWN, K_a, Vector2, Surface, SRCALPHA
from enum import Enum, auto
from math import sin

from .scene import Scene
from ..inputs.ressources import Ressources
from ..font import Font


class AnimationState(Enum):
    PAUSE = auto()
    CURTAIN_UP = auto()
    BACKGROUND_SHOW = auto()
    TITLE_ANIM = auto()
    PRESS_A = auto()
    DONE = auto()


class AnimationMainMenuScene(Scene):
    duration = {
        AnimationState.PAUSE: 1,
        AnimationState.CURTAIN_UP: 2,
        AnimationState.TITLE_ANIM: 1,
        AnimationState.BACKGROUND_SHOW: 0,
        AnimationState.PRESS_A: 0,
    }
    state = AnimationState.PAUSE

    def __init__(self):
        super().__init__()
        sheet = Ressources()["images"]["mainMenu"]
        self.shadow_curtain = sheet.subsurface((257, 0), (256, 187))
        self.curtain = Surface((512, 187), SRCALPHA)
        self.curtain.blit(sheet.subsurface((0, 0), (256, 187)), (0, 0))
        self.curtain.blit(sheet.subsurface((0, 0), (256, 187)), (256, 0))
        self.floor = Surface((512, 37))
        self.floor.blit(sheet.subsurface((0, 188), (256, 37)), (0, 0))
        self.floor.blit(sheet.subsurface((0, 188), (256, 37)), (256, 0))
        self.small_cloud = sheet.subsurface((180, 285), (16, 8))
        self.cloud = sheet.subsurface((180, 268), (32, 16))
        self.small_cactus = sheet.subsurface((257, 188), (64, 64))
        self.cactus = sheet.subsurface((322, 188), (63, 93))
        self.title = Surface((179, 113), SRCALPHA)
        self.title.blit(sheet.subsurface((0, 226), (179, 72)), (0, 0))
        self.title.blit(
            sheet.subsurface((180, 226), (42, 41)),
            (self.title.get_width() / 2 - 20.5, 72),
        )
        self.subtitle = Font().render("PRESS A TO START")

    def on_enter(self):
        self.curtain_start_pos = Vector2(0, 0)
        self.curtain_end_pos = Vector2(0, -171)
        self.curtain_current_pos = self.curtain_start_pos.copy()

        self.title_start_pos = Vector2(
            self.surface.get_width() / 2 - self.title.get_width() / 2,
            -self.title.get_height(),
        )
        self.title_end_pos = Vector2(
            self.surface.get_width() / 2 - self.title.get_width() / 2,
            self.surface.get_height() / 2 - self.title.get_width() / 2,
        )
        self.title_current_pos = self.title_start_pos.copy()

    def handle_event(self, event):
        if event.type == KEYDOWN:
            if event.key == K_a:
                self.manager.change_scene("main_menu")

    def update(self, dt):
        self.timer += dt

        match self.state:
            case AnimationState.PAUSE:
                if self.timer >= self.duration[self.state]:
                    self.timer = 0
                    self.state = AnimationState.CURTAIN_UP
            case AnimationState.CURTAIN_UP:
                t = min(self.timer / self.duration[self.state], 1.0)
                self.curtain_current_pos = self.curtain_start_pos.lerp(
                    self.curtain_end_pos, t
                )
                if self.timer >= self.duration[self.state]:
                    self.timer = 0
                    self.state = AnimationState.BACKGROUND_SHOW
            case AnimationState.BACKGROUND_SHOW:
                if self.timer >= self.duration[self.state]:
                    self.timer = 0
                    self.state = AnimationState.TITLE_ANIM
            case AnimationState.TITLE_ANIM:
                t = min(self.timer / self.duration[self.state], 1.0)
                self.title_current_pos = self.title_start_pos.lerp(
                    self.title_end_pos, t
                )
                if self.timer >= self.duration[self.state]:
                    self.timer = 0
                    self.state = AnimationState.PRESS_A
            case AnimationState.PRESS_A:
                if self.timer >= self.duration[self.state]:
                    self.timer = 0
                    self.state = AnimationState.DONE
            case AnimationState.DONE:
                self.manager.change_scene("main_menu")

    def draw(self):
        w = self.surface.get_width()
        h = self.surface.get_height()

        self.surface.fill((0, 0, 0))
        if self.state not in [AnimationState.PAUSE, AnimationState.CURTAIN_UP]:
            self.surface.fill((255, 219, 161))

        self.surface.blit(self.curtain, self.curtain_current_pos)

        if self.state not in [AnimationState.PAUSE, AnimationState.CURTAIN_UP]:
            self.surface.blit(
                self.cloud, (w / 3.5 - 22, (h / 4 - 12) + sin(self.timer / 2) * 5)
            )
            self.surface.blit(
                self.small_cloud,
                (w / 3.5 + 185, (h / 4 + 22) + sin(self.timer / 2) * 3.5),
            )
            self.surface.blit(self.small_cactus, (0, h - 101))
            self.surface.blit(self.cactus, (w - 63, h - 130))

        self.surface.blit(self.floor, (0, 203))

        if self.state != AnimationState.BACKGROUND_SHOW:
            self.surface.blit(self.title, self.title_current_pos)

        if self.state == AnimationState.PRESS_A:
            self.surface.blit(
                self.subtitle,
                (
                    w / 2 - self.subtitle.get_width() / 2,
                    h / 4 + self.title.get_height(),
                ),
            )
