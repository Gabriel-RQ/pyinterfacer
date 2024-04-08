"""
@author: Gabriel RQ
@description: Simple button component.
"""

import pygame
import os

from typing import Optional
from .clickable import Clickable
from .text import Text
from .hoverable import Hoverable


class Button(Clickable, Text, Hoverable):
    """Simple button component."""

    def __init__(
        self,
        bg_image: Optional[str] = None,
        bg_color: Optional[str] = None,
        bg_alpha: Optional[int] = None,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)

        self.bg_image = bg_image
        self.bg_color = bg_color
        self.bg_alpha = bg_alpha
        self._disabled_bg_alpha = 175

        self._load_error = False

        self.preload_image()

    def preload_image(self) -> None:
        """Try to initializes the button's background image. If it fails, simply render the buttons text."""
        if self.bg_image is not None:
            try:
                img = pygame.image.load(os.path.abspath(self.bg_image)).convert_alpha()

                # Checks if width and height were provided to this button
                if self.width > 0 and self.height > 0:
                    img = pygame.transform.scale(img, (self.width, self.height))
                else:
                    self.width, self.height = img.get_size()

                # Sets the background opacity
                if self.bg_alpha is not None:
                    img.set_alpha(self.bg_alpha)
                if not self.enabled:
                    img.set_alpha(self._disabled_bg_alpha)

                # Checks if there's text to be rendered into the button
                if len(self.text) > 0:
                    txt_surf = self.font.render(self.text)
                    img.blit(
                        txt_surf,
                        (
                            (img.get_width() - txt_surf.get_width()) // 2,
                            (img.get_height() - txt_surf.get_height()) // 2,
                        ),
                    )

                self.image = img
                self.rect = self.image.get_rect(center=(self.x, self.y))

            except:
                self._load_error = True
            else:
                self._load_error = False

    def update(self) -> None:
        # Checks if the background image was loaded successfully
        if self.bg_image is not None and not self._load_error:
            return

        # Otherwise renders a simple button filled with a background color and with text
        self.image = pygame.Surface((self.width, self.height))

        if self.bg_color is not None:
            self.image.fill(self.bg_color)

        if self.bg_alpha is not None:
            self.image.set_alpha(self.bg_alpha)
        if not self.enabled:
            self.image.set_alpha(self._disabled_bg_alpha)

        txt_surf = self.font.render(self.text)
        self.image.blit(
            txt_surf,
            (
                (self.width - txt_surf.get_width()) // 2,
                (self.height - txt_surf.get_height()) // 2,
            ),
        )
        self.rect = self.image.get_rect(center=(self.x, self.y))
