"""
@author: Gabriel RQ
@description: Font utilities for PyInterfacer.
"""

import pygame
import string


class Font:
    """Stores font information and handles text rendering."""

    def __init__(
        self,
        font: str,
        font_size: int,
        font_color: str,
        bold: bool,
        italic: bool,
        antialias: bool,
    ):
        self.font_size = font_size
        self.font_color = font_color
        self.bold = bold
        self.italic = italic
        self.antialias = antialias

        try:
            # Tries to load the specified font as a sys font
            f = "".join(font.lower().strip().split(" ")).translate(
                str.maketrans("", "", string.punctuation)
            )
            if f in pygame.font.get_fonts():
                self.font = pygame.font.SysFont(
                    name=f,
                    size=self.font_size,
                    bold=self.bold,
                    italic=self.italic,
                )
            else:
                # otherwise tries to load it from a file
                self.font = pygame.font.Font(filename=font, size=self.font_size)
                self.font.set_bold(self.bold)
                self.font.set_italic(self.italic)
        except:
            # if none work, load pygame's default font instead
            self.font = pygame.font.SysFont(
                name=pygame.font.match_font(
                    pygame.font.get_default_font(),
                    bold=self.bold,
                    italic=self.italic,
                ),
                size=self.font_size,
                bold=self.bold,
                italic=self.italic,
            )

    def render(self, text: str) -> pygame.surface.Surface:
        """Renders text using the font to a surface and returns it."""
        return self.font.render(text, antialias=self.antialias, color=self.font_color)
