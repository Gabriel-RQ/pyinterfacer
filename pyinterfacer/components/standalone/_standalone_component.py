"""
@author: Gabriel RQ
@description: Base component class.
"""

import pygame

from enum import Enum
from typing import Tuple, Optional, Literal

_AlignmentOptions = Literal[
    "center",
    "topleft",
    "topright",
    "midleft",
    "midright",
    "bottomleft",
    "bottomright",
]


class AlignmentOptions(Enum):
    """Possible component alignment options."""

    CENTER = "center"
    TOP_LEFT = "topleft"
    TOP_RIGHT = "topright"
    MID_LEFT = "midleft"
    MID_RIGHT = "midright"
    BOTTOM_LEFT = "bottomleft"
    BOTTOM_RIGHT = "bottomright"


class _StandaloneComponent(pygame.sprite.Sprite):
    """
    Base component class with attributes common to all components. Every component should inherit from this.
    """

    def __init__(
        self,
        pos: Tuple[float, float],
        size: Tuple[int, int] = (0, 0),
        alignment: _AlignmentOptions | AlignmentOptions = "center",
        static: bool = False,
        groups: Tuple[pygame.sprite.AbstractGroup, ...] = (),
        *args,
        **kwargs,
    ) -> None:
        super().__init__(groups)

        self.x = pos[0]
        self.y = pos[1]
        self.width = size[0]
        self.height = size[1]
        self._static = static  # controls if the component updates every frame or is static. Static components should not update.

        if isinstance(alignment, AlignmentOptions):
            self.alignment = alignment.value
        else:
            self.alignment = (
                alignment if alignment in _AlignmentOptions.__args__ else "center"
            )  # Alignment fallback to 'center' if not specified or invalid

        self.image = pygame.Surface(size)
        self._set_rect()
        self._align()

    def preload_image(self) -> None:
        """
        This method does nothing by default. Can be overwritten by inheriting classes to execute image preloading logic.
        Must be manually called.
        """

        pass

    def _align(self) -> None:
        """
        Aligns this component's rect, positioning it correctly at (x, y).
        """

        setattr(self.rect, self.alignment, (self.x, self.y))

    def _set_rect(self) -> None:
        """Sets the component rect attribute."""

        self.rect = self.image.get_frect()

    def update(self, *args, **kwargs) -> None:
        """
        Component update method. Does nothing by default and should be ovewritten by inheriting classes.
        """

        return super().update(*args, **kwargs)
