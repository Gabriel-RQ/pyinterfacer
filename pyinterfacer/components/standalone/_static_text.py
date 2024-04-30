"""
@author: Gabriel RQ
@description: Base class for rendering static text.
"""

from ._standalone_component import _StandaloneComponent
from ...util.font import Font
from typing import Optional


class _StaticText(_StandaloneComponent):
    """Base static text component class. Displays text on the screen. Other components that need text rendering can inherit from this."""

    def __init__(
        self,
        text: str = "",
        font: Optional[str] = None,
        font_size: int = 18,
        font_color: str = "#000000",
        font_bg_color: Optional[str] = None,
        bold: bool = False,
        italic: bool = False,
        rotation: int = 0,
        antialias: bool = True,
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

        self.image = self.font.render(self.text)[0]
        self._set_rect()
        self._align()
