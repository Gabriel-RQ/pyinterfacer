"""
@author: Gabriel RQ
@description: Group utilities for PyInterfacer.
"""

import pygame

from typing import List, Tuple, Optional, override
from ..components.handled._components import _HandledComponent
from ..components.standalone._hoverable import _Hoverable
from ..components.standalone._clickable import _Clickable
from ..components.standalone._get_input import _GetInput


def _filter_components(
    component: _HandledComponent, interfaces: Tuple[str, ...]
) -> bool:
    return (
        isinstance(component, _HandledComponent) and component.interface in interfaces
    )


class ComponentGroup(pygame.sprite.Group):
    """Base container for Component objects."""

    @override
    def update(self, interfaces: Optional[Tuple[str, ...]] = None) -> None:
        """
        Same as `pygame.sprite.Group.update`, extended with interface filtering.

        :param interfaces: Tuple of the interfaces that should be updated.
        """

        if interfaces is not None and len(interfaces) > 0:
            sprites = filter(
                lambda c: _filter_components(c, interfaces), self.sprites()
            )
        else:
            sprites = self.sprites()

        for sprite in sprites:
            sprite.update()

    @override
    def draw(
        self,
        surface: pygame.Surface,
        interfaces: Optional[Tuple[str, ...]] = None,
    ) -> List:
        """
        Same as `pygame.sprite.Group.draw`, extended with interface filtering.

        :param interfaces: Tuple of the interfaces that should be drawn.
        """

        # Filter the sprites
        if interfaces is not None and len(interfaces) > 0:
            sprites = filter(
                lambda c: _filter_components(c, interfaces), self.sprites()
            )
        else:
            sprites = self.sprites()

        if hasattr(surface, "blits"):
            self.spritedict.update(
                zip(sprites, surface.blits((spr.image, spr.rect) for spr in sprites))
            )
        else:
            for spr in sprites:
                self.spritedict[spr] = surface.blit(spr.image, spr.rect)
        self.lostsprites = []
        dirty = self.lostsprites

        return dirty


class ClickableGroup(ComponentGroup):
    """Specialized group for handling Clickable components."""

    def handle_click(
        self, mpos: Tuple[int, int], interfaces: Optional[Tuple[str, ...]] = None
    ) -> None:
        """
        Emits an activation for all the Clickable components in the group to check if they received a click. If `interfaces` is provided, emits the activation only for the components in the specified interfaces.

        :param mpos: Mouse position at event time.
        :param interfaces: Filter the Clickable components that will receive the activation.
        """

        if interfaces is not None and len(interfaces) > 0:
            sprites = filter(
                lambda c: _filter_components(c, interfaces), self.sprites()
            )
        else:
            sprites = self.sprites()

        for sprite in sprites:
            if isinstance(sprite, _Clickable) or hasattr(sprite, "on_click"):
                sprite.on_click(mpos)


class HoverableGroup(ComponentGroup):
    """Specialized group for handling Hoverable components."""

    def handle_hover(self, interfaces: Optional[Tuple[str, ...]] = None) -> None:
        """
        Handles hover event for each Hoverable component in the group. If `interfaces` is provided, handle hover events only for the components in the specified interfaces.
        :param interfaces: Filter the Hoverable components that will be handled.
        """

        if interfaces is not None and len(interfaces) > 0:
            sprites = filter(
                lambda c: _filter_components(c, interfaces), self.sprites()
            )
        else:
            sprites = self.sprites()

        mpos = pygame.mouse.get_pos()
        for sprite in sprites:
            if isinstance(sprite, _Hoverable):
                sprite.on_hover(mpos)


class ButtonGroup(ClickableGroup, HoverableGroup):
    """Specialized group for handling Button components."""


class InputGroup(ClickableGroup, HoverableGroup):
    def handle_input(self, event, interfaces: Optional[Tuple[str, ...]] = None) -> None:
        """
        Handles input for all of the Input components in the group. If `interfaces` is provided, handles the input only for the components in the specified interfaces.

        :param interfaces: Filter the Input components that will receive the user input.
        """

        if interfaces is not None and len(interfaces) > 0:
            sprites = filter(
                lambda c: _filter_components(c, interfaces), self.sprites()
            )
        else:
            sprites = self.sprites()

        for sprite in sprites:
            if isinstance(sprite, _GetInput):
                match event.type:
                    case pygame.KEYDOWN:
                        sprite.on_input(event.key)
                    case pygame.TEXTINPUT | pygame.TEXTEDITING:
                        sprite.on_input(event.text)
