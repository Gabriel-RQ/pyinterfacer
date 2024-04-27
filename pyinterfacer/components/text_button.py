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
        self._font_color_backup = self.font.color

    def update(self, *args, **kwargs) -> None:
        super().update()

    def hover_action(self) -> None:
        if self.focus_color is None:
            return

        if self._hovered:
            self.font.color = self.focus_color
        else:
            self.font.color = self._font_color_backup
