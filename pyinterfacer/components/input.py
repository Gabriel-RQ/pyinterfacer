"""
@author: Gabriel RQ
@description: Simple input component.
"""

import pygame

from typing import Optional, Tuple
from .text import Text
from .hoverable import Hoverable


class Input(Text, Hoverable):
    """Simple input component."""

    def __init__(
        self,
        active: bool = False,
        bg_color: Optional[str] = None,
        bg_focus_color: Optional[str] = None,
        border_radius: Optional[int] = None,
        border_focus_color: Optional[int] = None,
        max_length: Optional[int] = None,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)

        self.active = active
        self.bg_color = bg_color
        self.bg_focus_color = bg_focus_color
        self.border_focus_color = border_focus_color
        self.border_radius = border_radius
        self.max_length = max_length

        self._bg_color_backup = self.bg_color

    def handle_click(self, mouse_pos: Tuple[int, int]) -> None:
        """Checks if this component was clicked, if so, activates it, otherwise inactivate it."""

        if self.rect.collidepoint(mouse_pos):
            self.active = True
        else:
            self.active = False

    def handle_input(self, pressed_key: int, key_unicode: str) -> None:
        """Handles text input on the component."""

        if not self.active:
            return

        if pressed_key == pygame.K_BACKSPACE:
            self.text = self.text[:-1]
        elif pressed_key == pygame.K_RETURN or pressed_key == pygame.K_TAB:
            self.active = False
        elif self.max_length is None or len(self.text) < self.max_length:
            self.text += key_unicode

    def update(self) -> None:
        self.image = pygame.Surface((self.width, self.height))
        self.rect = self.image.get_rect(center=(self.x, self.y))

        # Checks if there is a background color and if the input should have border radius
        if self.bg_color is not None:
            if self.border_radius is not None:
                self.image.set_colorkey("black")
                pygame.draw.rect(
                    self.image,
                    self.bg_color,
                    (0, 0, self.rect.width, self.rect.height),
                    border_radius=self.border_radius,
                )
            else:
                self.image.fill(self.bg_color)

        if self.active and self.border_focus_color is not None:
            pygame.draw.rect(
                self.image,
                self.border_focus_color,
                (0, 0, self.rect.width, self.rect.height),
                width=2,
                border_radius=self.border_radius,
            )

        txt_surf = self.font.render(self.text)
        # offsets the x position of the text if it's wider than the input's width
        txt_x_pos = (
            15
            if txt_surf.get_width() <= self.width
            else self.width - txt_surf.get_width() - 15
        )
        self.image.blit(
            txt_surf, (txt_x_pos, (self.rect.height - txt_surf.get_height()) // 2)
        )

    def hover_action(self) -> None:
        if self.bg_focus_color is None:
            return

        if self._hovered:
            self.bg_color = self.bg_focus_color
        else:
            self.bg_color = self._bg_color_backup
