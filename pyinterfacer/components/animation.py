"""
@author: Gabriel RQ
@description: Simple animation component. Displays images in sequence.
"""

from typing import Tuple
from .component import Component


class Animation(Component):
    """Displays images in sequence."""

    def __init__(
        self,
        frames: int,
        delay: int,
        images: Tuple[str, ...],
        **kwargs,
    ) -> None:
        super().__init__(id, **kwargs)

        self.frames = frames
        self.delay = delay
        self.images = tuple(images)
