"""
@author: Gabriel RQ
@description: Simple text button component.
"""

from ._clickable import _Clickable
from ._hoverable import _Hoverable
from .text import Text
from typing import Optional, override


class TextButton(_Clickable, Text, _Hoverable):
    def __init__(self, focus_color: Optional[str] = None) -> None:
        self.focus_color = focus_color

    @override
    def hover_action(self) -> None:
        if self.focus_color is None:
            return

        if self._hovered:
            self.font.color = self.focus_color
        else:
            self.font.color = self.font.color_backup
