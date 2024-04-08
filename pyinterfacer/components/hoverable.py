"""
@author: Gabriel RQ
@description: Base hoverable class.
"""

from typing import Tuple

from .component import Component


class Hoverable(Component):
    """Base class for hoverable components."""

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self._hovered = False

    def hover_action(self) -> None:
        """
        The action to perform when this component is hovered. By default this does nothing, and should be overwritten by inheriting classes.
        """
        pass

    def handle_hover(self, mouse_pos: Tuple[int, int]) -> None:
        """Checks if this component was hovered, and executes it's `hover_action` if so."""

        if self.rect is not None and self.rect.collidepoint(mouse_pos):
            self._hovered = True
        else:
            self._hovered = False

        self.hover_action()
