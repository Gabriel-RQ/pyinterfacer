"""
@author: Gabriel RQ
@description: Simple input component.
"""

from typing import Optional
from .text import Text
from .hoverable import Hoverable


class Input(Text, Hoverable):
    """Simple input component."""

    def __init__(
        self,
        max_length: Optional[int] = None,
        min_length: Optional[int] = None,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)

        self.max_length = max_length
        self.min_length = min_length

    def handle_input(self, pressed_key: str) -> None: ...
