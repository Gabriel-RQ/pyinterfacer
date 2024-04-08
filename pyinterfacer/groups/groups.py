"""
@author: Gabriel RQ
@description: Group utilities for PyInterfacer.
"""

import pygame

from typing import List, Tuple, Optional
from ..components import Component, Clickable, Hoverable

FocusGroup = pygame.sprite.GroupSingle


def _filter_components(component: Component, interfaces: Tuple[str, ...]) -> bool:
    return isinstance(component, Component) and component.interface in interfaces


class ComponentGroup(pygame.sprite.Group):
    """Base container for Component objects."""

    def update(self, interfaces: Optional[Tuple[str, ...]] = None) -> None:
        if interfaces is not None and len(interfaces) > 0:
            sprites = filter(
                lambda c: _filter_components(c, interfaces), self.sprites()
            )
        else:
            sprites = self.sprites()

        for sprite in sprites:
            sprite.update()

    def draw(
        self,
        surface: pygame.Surface,
        interfaces: Optional[Tuple[str, ...]] = None,
    ) -> List:
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

    def handle_click(self, interfaces: Optional[Tuple[str, ...]] = None) -> None:
        """
        Emits an activation for all the Clickable components in the group to check if they received a click. If `interfaces` is provided, emits the activation only for the components in the specified interfaces.

        :param interfaces: Filter the Clickable components that will receive the activation.
        """

        if interfaces is not None and len(interfaces) > 0:
            sprites = filter(
                lambda c: _filter_components(c, interfaces), self.sprites()
            )
        else:
            sprites = self.sprites()

        mpos = pygame.mouse.get_pos()
        for sprite in sprites:
            if isinstance(sprite, Clickable):
                sprite.handle_click(mpos)


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
            if isinstance(sprite, Hoverable):
                sprite.handle_hover(mpos)


class ButtonGroup(ClickableGroup, HoverableGroup):
    """Specialized group for handling Button components."""
