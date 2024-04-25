"""
@author: Gabriel RQ
@description: Base text class.
"""

from typing import Optional
from .component import Component
from ..util import Font


class Text(Component):
    """Base text component class. Displays text on the screen. Other components that need text rendering can inherit from this."""

    def __init__(
        self,
        text: str = "",
        font: Optional[str] = None,
        font_size: Optional[int] = 18,
        font_color: Optional[str] = "#000000",
        font_bg_color: Optional[str] = None,
        bold: Optional[bool] = False,
        italic: Optional[bool] = False,
        rotation: Optional[int] = 0,
        antialias: Optional[bool] = True,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)

        self.text = text
        self.font = Font(
            font,
            font_size,
            font_color,
            font_bg_color,
            bold,
            italic,
            rotation,
            antialias,
        )

    def update(self) -> None:
        self.image, _ = self.font.render(self.text)
        self._set_rect()
        self._align()
