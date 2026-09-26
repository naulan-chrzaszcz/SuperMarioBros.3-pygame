"""Sound effects and music declared in ``ressources.yaml``.

The code plays *events* by name (``"jump"``, ``"coin"``...): the ``sounds``
and ``musics`` lists of ``ressources.yaml`` give the file of each name, so a
sound is changed, added or muted without touching the code. An event without
a declared sound is silent. Without an audio device, nothing is played.
"""

from __future__ import annotations

from collections import deque
from pathlib import Path
from typing import Deque, Dict, Mapping, Optional

import pygame

from .inputs.config import Audio as AudioSettings


class Audio:
    """Sound events and musics of ``ressources.yaml``.

    Code plays *events* (``play("jump")``), the data maps them to files: an
    event without a file is silent, and so is the game without an audio device.
    """

    def __init__(
        self,
        sounds: Mapping[str, Path],
        musics: Mapping[str, Path],
        settings: AudioSettings = AudioSettings(),
    ):
        self.sounds = dict(sounds)
        self.musics = dict(musics)
        self.settings = settings
        self._loaded: Dict[str, Optional[pygame.mixer.Sound]] = {}
        self.music: Optional[str] = None
        # The last events, played or not (for the tests and debugging).
        self.history: Deque[str] = deque(maxlen=50)

    @property
    def enabled(self) -> bool:
        return self.settings.enabled and pygame.mixer.get_init() is not None

    def play(self, name: str) -> None:
        """Plays the sound effect of the event ``name``, if it has one."""
        self.history.append(name)
        if not self.enabled or name not in self.sounds:
            return
        if name not in self._loaded:
            try:
                sound = pygame.mixer.Sound(str(self.sounds[name]))
                sound.set_volume(self.settings.sound_volume)
            except pygame.error:
                sound = None
            self._loaded[name] = sound
        sound = self._loaded[name]
        if sound is not None:
            sound.play()

    def play_music(self, name: Optional[str], loop: bool = True) -> None:
        """Plays the music ``name`` (None: silence); the current one goes on
        when it is asked again."""
        if name == self.music:
            return
        self.stop_music()
        self.music = name
        if name is None or not self.enabled or name not in self.musics:
            return
        try:
            pygame.mixer.music.load(str(self.musics[name]))
            pygame.mixer.music.set_volume(self.settings.music_volume)
            pygame.mixer.music.play(-1 if loop else 0)
        except pygame.error:
            pass

    def stop_music(self) -> None:
        self.music = None
        if self.enabled:
            pygame.mixer.music.stop()
