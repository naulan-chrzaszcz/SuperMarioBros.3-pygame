from typing import Any, Optional, Tuple


class ButtonModel:
    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        color: Tuple[int, int, int],
        text: Optional[str] = None,
        value: Optional[Any] = None,
    ):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.text = text
        self.value = value

    def on_click(self) -> None:
        pass
