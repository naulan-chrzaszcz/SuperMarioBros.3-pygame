"""Splash screen shown before the title screen (``skipIntro`` in ``config.yaml``)."""

from __future__ import annotations

from enum import Enum, auto

from ..constants import BLACK
from ..inputs.config import Action
from .scene import GameContext, Scene


class AnimationState(Enum):
    FADE_IN = auto()
    PAUSE = auto()
    FADE_OUT = auto()
    DONE = auto()


class IntroScene(Scene):
    """Splash screen fading in and out; any confirm or back key skips it."""

    duration = {
        AnimationState.FADE_IN: 1.5,
        AnimationState.PAUSE: 3.0,
        AnimationState.FADE_OUT: 1.5,
    }

    def __init__(self, context: GameContext, next_scene: str = "main_menu"):
        super().__init__(context)
        self.next_scene = next_scene
        # A copy, so that fading does not change the shared image.
        self.background = context.ressources.image("intro").copy()

    def on_enter(self) -> None:
        super().on_enter()
        self.state = AnimationState.FADE_IN
        self.alpha = 0.0

    def on_action(self, action: Action) -> None:
        if action in (Action.CONFIRM, Action.BACK):
            self.state = AnimationState.DONE

    def update(self, dt: float) -> None:
        super().update(dt)
        if self.state == AnimationState.DONE:
            self.manager.change_scene(self.next_scene)
            return
        t = min(self.timer / self.duration[self.state], 1.0)
        if self.state == AnimationState.FADE_IN:
            self.alpha = 255 * t
        elif self.state == AnimationState.FADE_OUT:
            self.alpha = 255 * (1 - t)
        if t >= 1.0:
            self.state = list(AnimationState)[list(AnimationState).index(self.state) + 1]
            self.timer = 0.0

    def draw(self) -> None:
        self.surface.fill(BLACK)
        self.background.set_alpha(int(self.alpha))
        self.surface.blit(self.background, (0, 0))
