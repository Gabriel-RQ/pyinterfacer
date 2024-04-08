"""
@author: Gabriel RQ
@description: Base clickable class.
"""

from typing import Optional, Callable, Tuple
from .component import Component


class Clickable(Component):
    """Base class for clickable components. Clickable components should inherit from this."""

    def __init__(
        self,
        action: Optional[Callable] = None,
        enabled: Optional[bool] = True,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)

        self.action = action
        self.enabled = enabled

    def handle_click(self, mous_pos: Tuple[int, int]) -> None:
        """Checks if this component was clicked, and executes it's action if so."""
        if (
            self.enabled
            and self.action is not None
            and self.rect is not None
            and self.rect.collidepoint(mous_pos)
        ):
            self.action()
