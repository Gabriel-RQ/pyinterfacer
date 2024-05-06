"""
@author: Gabriel RQ
@description: Component that loads it's animation from a spritesheet.
"""

import pygame

from typing import Tuple
from .animation import Animation


class SpritesheetAnimation(Animation):
    """Displays images in sequence, loaded from a spritesheet."""

    def __init__(
        self,
        spritesheet: str,
        sprite_width: int,
        sprite_height: int,
        **kwargs,
    ) -> None:

        self.sprite_width = sprite_width
        self.sprite_height = sprite_height
        self.spritesheet = pygame.image.load(spritesheet).convert()

        images = self._parse_spritesheet()
        super().__init__(images=images, **kwargs)

    def _parse_spritesheet(self) -> Tuple[pygame.Surface, ...]:
        """
        Parses a spritesheet into a tuple of pygame Surfaces, for each image.

        :return: A tuple containing the Surfaces of each sprite.
        """

        spritesheet_width, spritesheet_height = self.spritesheet.get_size()
        sprites = []

        # for each line
        for y in range(0, spritesheet_height, self.sprite_height):
            # for each column
            for x in range(0, spritesheet_width, self.sprite_width):
                r = pygame.Rect(x, y, self.sprite_width, self.sprite_height)
                spr = pygame.Surface(r.size).convert()
                spr.blit(source=self.spritesheet, dest=(0, 0), area=r)

                sprites.append(spr)

        return tuple(sprites)
