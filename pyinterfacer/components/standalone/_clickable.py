"""
@author: Gabriel RQ
@description: Base class for clickable components.
"""

from ._standalone_component import _StandaloneComponent
from typing import Optional, Callable, Tuple


class _Clickable(_StandaloneComponent):
    """Base class for clickable components. Clickable components should inherit from this."""

    def __init__(
        self,
        action: Optional[Callable] = None,
        enabled: bool = True,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)

        self.action = action
        self.enabled = enabled

    def on_click(self, mous_pos: Tuple[int, int]) -> None:
        """Checks if this component was clicked, and executes it's action if so."""

        if (
            self.enabled
            and self.action is not None
            and self.rect.collidepoint(mous_pos)
        ):
            self.action()
