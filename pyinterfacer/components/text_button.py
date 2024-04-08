"""
@author: Gabriel RQ
@description: Simple text button component.
"""

from typing import Optional, Tuple
from .clickable import Clickable
from .text import Text
from .hoverable import Hoverable


class TextButton(Clickable, Text, Hoverable):
    """Simple text button component. Adapts to text size."""

    def __init__(
        self,
        focus_color: Optional[str] = None,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)

        self.focus_color = focus_color
        self._font_color_backup = self.font.font_color

    def update(self) -> None:
        super().update()
        self.image.set_colorkey("#000000")

    def handle_hover(self, mouse_pos: Tuple[int, int]) -> None:
        if self.rect is not None and self.rect.collidepoint(mouse_pos):
            self.font.font_color = self.focus_color
        else:
            self.font.font_color = self._font_color_backup
