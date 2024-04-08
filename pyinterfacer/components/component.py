"""
@author: Gabriel RQ
@description: Base component class.
"""

import pygame

from typing import Tuple, Optional


class Component(pygame.sprite.Sprite):
    """Base component class with atributes common to all components. Every component should inherit from this."""

    def __init__(
        self,
        id: str,
        type: str,
        interface: str,
        x: int,
        y: int,
        width: Optional[int] = 0,
        height: Optional[int] = 0,
        groups: Tuple[pygame.sprite.AbstractGroup, ...] = (),
        *args,
        **kwargs,
    ) -> None:
        super().__init__(groups)

        self.id = id
        self.type = type
        self.interface = interface
        self.x = x
        self.y = y
        self.width = width if width is not None else 0
        self.height = height if height is not None else 0

        self.subtype = None  # Should be set by custom components, to indicate which of the default component set type the custom components belong to (used for group handling)

    def preload_image(self) -> None:
        """This method does nothing by default. Can be overwritten by inheriting classes to execute image preloading logic."""
        pass

    def update(self) -> None:
        self.image = pygame.Surface((self.width, self.height))
        self.rect = self.image.get_rect(center=(self.x, self.y))
        self.image.fill("black")
