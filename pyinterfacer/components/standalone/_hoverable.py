"""
@author: Gabriel RQ
@description: Base class for hoverable components.
"""

from ._standalone_component import _StandaloneComponent
from typing import Tuple


class _Hoverable(_StandaloneComponent):
    """Base class for hoverable components."""

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

        self._hovered = False

    def hover_action(self) -> None:
        """
        The action to perform when this component is hovered. By default this does nothing, and should be overwritten by inheriting classes.
        """

        pass

    def on_hover(self, mouse_pos: Tuple[int, int]) -> None:
        """Checks if this component was hovered, and executes it's `hover_action` if so."""

        if self.rect.collidepoint(mouse_pos):
            self._hovered = True
        else:
            self._hovered = False

        self.hover_action()
