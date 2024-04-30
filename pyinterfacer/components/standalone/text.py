"""
@author: Gabriel RQ
@description: Base static text component class.
"""

from ._static_text import _StaticText
from typing import override


class Text(_StaticText):
    """Base text component class. Can be either static or dynamic."""

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

    @override
    def update(self, *args, **kwargs) -> None:
        if self._static:
            return

        self.image = self.font.render(self.text)[0].convert_alpha()
        self._set_rect()
        self._align()
