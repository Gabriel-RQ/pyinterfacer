import pygame


class Font:
    """Stores font information and handles text rendering."""

    def __init__(
        self,
        font: str,
        font_size: int,
        font_color: str,
        bold: bool,
        italic: bool,
    ):
        self.font_size = font_size
        self.font_color = font_color
        self.bold = bold
        self.italic = italic

        if f := font.lower() in pygame.font.get_fonts():
            self.font = pygame.font.SysFont(
                name=f,
                size=self.font_size,
                bold=self.bold,
                italic=self.italic,
            )
        else:
            self.font = pygame.font.Font(filename=font, size=self.font_size)
            self.font.set_bold(self.bold)
            self.font.set_italic(self.italic)

    def render(self, text: str) -> pygame.surface.Surface:
        """Renders text using the font to a surface and returns it."""
        return self.font.render(text, antialias=True, color=self.font_color)
