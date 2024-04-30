"""
@author: Gabriel RQ
@description: Base class for components that receive user input.
"""

import pygame

from ._standalone_component import _StandaloneComponent
from typing import Any


class _GetInput(_StandaloneComponent):

    IS_ANY_ACTIVE = False

    def __init__(self, active: bool = False, **kwargs) -> None:
        super().__init__(**kwargs)

        self.active = active

    def activate(self) -> None:
        """Gives focus to the Input."""

        self.active = True
        _GetInput.IS_ANY_ACTIVE = True
        pygame.key.start_text_input()
        pygame.key.set_repeat(250, 50)

    def deactivate(self) -> None:
        """Removes focus from the Input."""

        self.active = False
        _GetInput.IS_ANY_ACTIVE = False
        pygame.key.stop_text_input()
        pygame.key.set_repeat(0, 0)

    def on_input(self, arg: Any) -> None:
        """Handles text input on the component. Does nothing by default, should be overwritten by inherting components."""

        pass
