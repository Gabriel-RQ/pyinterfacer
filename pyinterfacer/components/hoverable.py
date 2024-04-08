"""
@author: Gabriel RQ
@description: Base hoverable class.
"""

from typing import Tuple
from .component import Component


class Hoverable(Component):
    """Base class for hoverable components."""

    def hover_action(self) -> None:
        """
        The action to perform when this component is hovered. By default this does nothing, and should be overwritten by inheriting classes.
        """
        pass

    def handle_hover(self, mouse_pos: Tuple[int, int]) -> None:
        if self.rect and self.rect.collidepoint(mouse_pos):
            self.hover_action()
