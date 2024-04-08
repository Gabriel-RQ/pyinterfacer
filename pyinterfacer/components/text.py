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
        bold: Optional[bool] = False,
        italic: Optional[bool] = False,
        antialias: Optional[bool] = True,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)

        self.text = text
        self.font = Font(font, font_size, font_color, bold, italic, antialias)

    def update(self) -> None:
        self.image = self.font.render(self.text)
        self.rect = self.image.get_rect(center=(self.x, self.y))
