"""
@author: Gabriel RQ
@description: Simple animation component. Displays images in sequence.
"""

import pygame

from typing import Tuple, Optional
from .component import Component


class Animation(Component):
    """Displays images in sequence."""

    def __init__(
        self,
        delay: int,
        images: Tuple[str, ...],
        colorkey: Optional[str] = None,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)

        self.delay = delay
        self.colorkey = colorkey

        try:
            # checks if 'images' is a list of paths, otherwise it should be a list of Surfaces
            if len(images) > 0 and type(images[0]) is str:
                self.images = [pygame.image.load(image).convert() for image in images]
            else:
                self.images = images
        except:
            self.images = None
        else:
            # Verifies if needs to scale images
            if self.width > 0 and self.height > 0:
                self.images = [
                    pygame.transform.scale(image, (self.width, self.height))
                    for image in self.images
                ]

            # Applies colorkey, if provided
            if self.colorkey is not None:
                for image in self.images:
                    image.set_colorkey(self.colorkey)

            self.images = tuple(self.images)

        self.frames = len(self.images) if self.images is not None else 0

        self._current_frame = 0
        self._delay_counter = 0

    def update(self) -> None:
        # Verify if there are loaded images
        if self.images is None or len(self.images) == 0:
            return

        # Define the image for the current frame
        self.image = self.images[self._current_frame]
        self.rect = self.image.get_rect()
        self._align()

        # Handles the delay
        self._delay_counter += 1

        if self._delay_counter == self.delay:
            self._current_frame = (self._current_frame + 1) % self.frames
            self._delay_counter = 0
