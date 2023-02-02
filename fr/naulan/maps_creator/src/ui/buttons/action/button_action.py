from abc import ABC, abstractmethod
from typing import Any


class ButtonAction(ABC):
    button: Any

    def __call__(self, button):
        self.button = button

    @abstractmethod
    def action(self, *args, **kwargs):
        pass
