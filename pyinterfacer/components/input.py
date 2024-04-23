"""
@author: Gabriel RQ
@description: Simple input component.
"""

import pygame

from typing import Optional, Tuple, overload
from .text import Text
from .hoverable import Hoverable


class Input(Text, Hoverable):
    """Simple input component."""

    IS_ANY_ACTIVE = False

    def __init__(
        self,
        active: bool = False,
        bg_color: Optional[str] = None,
        bg_focus_color: Optional[str] = None,
        border_radius: Optional[int] = None,
        border_focus_color: Optional[int] = None,
        max_length: Optional[int] = None,
        hint: Optional[str] = None,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)

        self.active = active
        self.bg_color = bg_color
        self.bg_focus_color = bg_focus_color
        self.border_focus_color = border_focus_color
        self.border_radius = border_radius
        self.max_length = max_length
        self.hint = hint

        self._bg_color_backup = self.bg_color
        self._fill_color = pygame.Color(self.bg_color)
        self._fill_color.r = (
            self._fill_color.r + 1
            if self._fill_color.r < 255
            else self._fill_color.r - 1
        )

    def _activate(self) -> None:
        """Gives focus to the Input."""
        self.active = True
        Input.IS_ANY_ACTIVE = True
        pygame.key.start_text_input()
        pygame.key.set_repeat(250, 50)

    def _deactivate(self) -> None:
        """Removes focus from the Input."""
        self.active = False
        Input.IS_ANY_ACTIVE = False
        pygame.key.stop_text_input()
        pygame.key.set_repeat(0, 0)

    def handle_click(self, mouse_pos: Tuple[int, int]) -> None:
        """Checks if this component was clicked, if so, activates it, otherwise inactivate it."""

        if self.rect.collidepoint(mouse_pos):
            self._activate()
        else:
            self._deactivate()

    @overload
    def handle_input(self, pressed_key: int) -> None: ...

    @overload
    def handle_input(self, text: str) -> None: ...

    def handle_input(self, p1: str | int) -> None:
        """Handles text input on the component."""

        if not self.active:
            return

        if isinstance(p1, str):
            if self.max_length is None or len(self.text) < self.max_length:
                self.text += p1
        elif isinstance(p1, int):
            if p1 == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif p1 in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_TAB):
                self._deactivate()

    def hover_action(self) -> None:
        if self.bg_focus_color is None:
            return

        if self._hovered:
            self.bg_color = self.bg_focus_color
        else:
            self.bg_color = self._bg_color_backup

    def update(self) -> None:
        self.image = pygame.Surface((self.width, self.height))
        self._set_rect()
        self._align()

        # Checks if there is a background color and if the input should have border radius
        if self.bg_color is not None:
            if self.border_radius is not None:
                self.image.fill(self._fill_color)
                self.image.set_colorkey(self._fill_color)
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

        txt_surf, _ = self.font.render(
            self.hint if self.hint is not None and not len(self.text) > 0 else self.text
        )
        # offsets the x position of the text if it's wider than the input's width
        txt_x_pos = (
            15
            if txt_surf.get_width() <= self.width
            else self.width - txt_surf.get_width() - 15
        )
        self.image.blit(
            txt_surf, (txt_x_pos, (self.rect.height - txt_surf.get_height()) // 2)
        )
