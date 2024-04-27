"""
@author: Gabriel RQ
@description: Simple image component.
"""

import os
import pygame

from .component import Component


class Image(Component):
    """Displays an static image."""

    def __init__(
        self,
        path: str,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)

        self.path = path

        self.preload_image()

    def preload_image(self) -> None:
        # Tries to load the specified image
        try:
            img = pygame.image.load(os.path.abspath(self.path)).convert_alpha()

            # resizes it if width and height are provided
            if self.width > 0 and self.height > 0:
                img = pygame.transform.scale(img, (self.width, self.height))
            else:
                self.width, self.height = img.get_size()
        except:
            # if not possible to load, simply displays a pygame Surface
            img = pygame.Surface((self.width, self.height))
            img.fill("black")
        finally:
            self.image = img
            self._set_rect()
            self._align()

    def update(self, *args, **kwargs) -> None:
        return
