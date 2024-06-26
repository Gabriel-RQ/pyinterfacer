"""
@author: Gabriel RQ
@description: Multi-line text component.
"""

import pygame

from .text import Text
from typing import List, Optional, override


class Paragraph(Text):
    """Simple multi-line text component."""

    def __init__(
        self,
        lines: List[str],
        line_height: Optional[int] = None,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self.lines = lines
        self.line_height = (
            line_height if line_height is not None else self.font.size * 0.75
        )

    def _render_lines(self) -> None:
        # Gets a surface of rendered text for each line
        line_surfs = [self.font.render(line) for line in self.lines]
        blit_seq = []

        # Gets the surfaces and their rects at the right position for the line
        for i, line in enumerate(line_surfs):
            r = line[1]
            r.y += i * self.line_height

            blit_seq.append((line[0], r))

        return blit_seq

    @override
    def update(self, *args, **kwargs) -> None:
        lines = self._render_lines()
        # Calculates the max size for the surface
        max_width = max([line[1].width for line in lines])
        max_height = max([line[1].bottom for line in lines])

        self.image = pygame.Surface((max_width, max_height), pygame.SRCALPHA)
        self.image.blits(lines)
        self._set_rect()
        self._align()
