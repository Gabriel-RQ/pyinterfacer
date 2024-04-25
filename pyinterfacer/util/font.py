"""
@author: Gabriel RQ
@description: Font utilities for PyInterfacer.
"""

import pygame
import pygame.freetype
import string

from typing import Optional, Union, Tuple

_Color = Union[pygame.Color, str, Tuple[int, int, int]]


class Font:
    """Stores font information and handles text rendering. Uses the pygame.freetype module."""

    def __init__(
        self,
        name: Optional[str] = None,
        size: int = 14,
        color: Optional[_Color] = None,
        bg_color: Optional[_Color] = None,
        bold: bool = False,
        italic: bool = False,
        rotation: int = 0,
        antialiased: bool = True,
    ) -> None:
        try:
            # Removes punctation from the font name and tries to load it as a system font
            f = "".join(name.lower().strip().split(" ")).translate(
                str.maketrans("", "", string.punctuation)
            )
            if f in pygame.font.get_fonts():
                self._font = pygame.freetype.SysFont(
                    name=f,
                    size=size,
                    bold=bold,
                    italic=italic,
                )
            else:
                self._font = pygame.freetype.Font(file=name, size=size)
                self._font.strong = bold
                self._font.oblique = italic
        except:
            self._font = pygame.freetype.SysFont(None, size, bold, italic)

        self._font.antialiased = antialiased
        self._font.fgcolor = pygame.Color(color)
        if bg_color is not None:
            self._font.bgcolor = pygame.Color(bg_color)
        self._font.rotation = rotation

    @property
    def size(self) -> int:
        return self._font.size

    @size.setter
    def size(self, s: int) -> None:
        self._font.size = s

    @property
    def color(self) -> pygame.Color:
        return self._font.fgcolor

    @color.setter
    def color(self, c: _Color) -> None:
        self._font.fgcolor = pygame.Color(c)

    @property
    def bg_color(self) -> pygame.Color:
        return self._font.bgcolor

    @bg_color.setter
    def bg_color(self, c: _Color) -> None:
        self._font.bgcolor = pygame.Color(c)

    @property
    def bold(self) -> bool:
        return self._font.strong

    @bold.setter
    def bold(self, b: bool) -> None:
        self._font.strong = b

    @property
    def italic(self) -> bool:
        return self._font.oblique

    @italic.setter
    def italic(self, i: bool) -> None:
        self._font.oblique = i

    @property
    def rotation(self) -> int:
        return self._font.rotation

    @rotation.setter
    def rotation(self, r: int) -> None:
        self._font.rotation = r

    @property
    def antialiased(self) -> bool:
        return self._font.antialiased

    @antialiased.setter
    def antialiased(self, aa: bool) -> None:
        self._font.antialiased = aa

    def render(
        self,
        text: str,
        fg: Optional[_Color] = None,
        bg: Optional[_Color] = None,
        rotation: Optional[int] = None,
    ) -> Tuple[pygame.Surface, pygame.Rect]:
        """Renders text and returns it's surface and rect."""

        return self._font.render(
            text, fgcolor=fg, bgcolor=bg, rotation=(rotation or self.rotation)
        )
