"""
@author: Gabriel RQ
@description: Base component class.
"""

import pygame
import typing

from typing import Tuple, Optional, Literal

if typing.TYPE_CHECKING:
    from ..interface import Interface


default_component_types = Literal[
    "animation",
    "button",
    "clickable",
    "component",
    "hoverable",
    "image",
    "input",
    "paragraph",
    "spritesheet-animation",
    "text-button",
    "text",
]

alignment_options = Literal[
    "center",
    "topleft",
    "topright",
    "midleft",
    "midright",
    "bottomleft",
    "bottomright",
]


class Component(pygame.sprite.Sprite):
    """
    Base component class with atributes common to all components. Every component should inherit from this.
    """

    def __init__(
        self,
        id: str,
        type: str,
        interface: str,
        x: float,
        y: float,
        width: Optional[int] = 0,
        height: Optional[int] = 0,
        grid_cell: Optional[int] = None,
        style: Optional[str | Tuple[str]] = None,
        alignment: Optional[alignment_options] = None,
        groups: Tuple[pygame.sprite.AbstractGroup, ...] = (),
        *args,
        **kwargs,
    ) -> None:
        super().__init__(groups)

        self.id = id
        self.type = type
        self.interface = interface
        self.x = x
        self.y = y
        self.width = width if width is not None else 0
        self.height = height if height is not None else 0
        self.grid_cell = grid_cell
        self.style_classes = tuple(style) if style is not None else None
        self.alignment = (
            alignment
            if alignment is not None and alignment in alignment_options.__args__
            else "center"
        )  # Alignment fallback to 'center' if not specified or invalid

        self.subtype: Optional[default_component_types] = (
            None  # Should be set by custom components, to indicate which of the default component set type the custom components belong to (used for group handling)
        )

        self.image = pygame.Surface((self.width, self.height))
        self._set_rect()

    def preload_image(self) -> None:
        """
        This method does nothing by default. Can be overwritten by inheriting classes to execute image preloading logic.
        Must be manually called.
        """

        pass

    def after_load(self, interface: "Interface") -> None:
        """
        This method is called directly after the component's interface is loaded into, and does nothing by default. This can be used to execute any logic that should be run after the interface and it's components are loaded.

        :param interface: The interface instance the component was loaded into.
        """

        pass

    def _align(self) -> None:
        """
        Aligns this component rect, positioning the rect correctly at (x, y).
        """

        setattr(self.rect, self.alignment, (self.x, self.y))

    def _set_rect(self) -> None:
        self.rect = self.image.get_frect()

    def update(self, *args, **kwargs) -> None:
        self.image = pygame.Surface((self.width, self.height))
        self._set_rect()
        self._align()

    def __repr__(self) -> str:
        return f"<{self.type.capitalize()} component | id: {self.id} ; interface: {self.interface} ; subtype: {self.subtype} ; in ({len(self.groups())}) groups>"
