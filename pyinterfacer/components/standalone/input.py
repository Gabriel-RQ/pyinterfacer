"""
@author: Gabriel RQ
@description: Simple input component.
"""

import pygame

from ._get_input import _GetInput
from .text import Text
from ._hoverable import _Hoverable
from ._clickable import _Clickable
from typing import Optional, Union, Tuple, overload, override

_Color = Union[str, Tuple[int, int, int]]


class Input(Text, _GetInput, _Hoverable, _Clickable):
    def __init__(
        self,
        bg_color: Optional[_Color] = None,
        bg_focus_color: Optional[_Color] = None,
        border_focus_color: Optional[_Color] = None,
        border_radius: Optional[int] = None,
        max_length: Optional[int] = None,
        hint: Optional[str] = None,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)

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

    @override
    def on_click(self, mouse_pos: Tuple[int, int]) -> None:
        """Checks if this component was clicked, if so, activates it, otherwise inactivate it."""

        # The Input component is a special case, as it inherits from _Clickable only to have it's on_click method handled by the groups.
        # The other attributes from _Clickable are not used.
        if self.rect.collidepoint(mouse_pos):
            self.activate()
        else:
            self.deactivate()

    @overload
    def on_input(self, pressed_key: int) -> None: ...

    @overload
    def on_input(self, text: str) -> None: ...

    @override
    def on_input(self, arg: str | int):

        if not self.active:
            return

        if isinstance(arg, str):
            if self.max_length is None or len(self.text) < self.max_length:
                self.text += arg
        elif isinstance(arg, int):
            if arg == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif arg in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_TAB):
                self.deactivate()

    @override
    def hover_action(self) -> None:
        if self.bg_focus_color is None:
            return

        if self._hovered:
            self.bg_color = self.bg_focus_color
        else:
            self.bg_color = self._bg_color_backup

    @override
    def update(self, *args, **kwargs) -> None:
        self.image = pygame.Surface((self.width, self.height), flags=pygame.SRCALPHA)
        self._set_rect()
        self._align()

        if self.bg_color is not None:
            if self.border_radius is not None:
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
