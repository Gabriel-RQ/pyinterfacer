"""
@author: Gabriel RQ
@description: Describes an interface.
"""

import pygame
import os

from ..components import Component
from ..groups import ComponentGroup, ClickableGroup, HoverableGroup, InputGroup
from ..util import percent_to_float
from typing import List, Dict, Literal, Optional, Tuple


class Interface:
    COMPONENT_CONVERSION_TABLE = None
    GROUP_CONVERSION_TABLE = None

    def __init__(
        self,
        name: str,
        background: str,
        size: Tuple[int, int],
        components: List[Dict],
        display: Literal["default", "grid"],
        rows: Optional[int] = None,
        columns: Optional[int] = None,
        styles: Optional[Dict[str, Dict]] = None,
    ) -> None:
        self.name = name
        self.display = display
        self.rows = rows
        self.columns = columns
        self.size = size

        self.surface = pygame.Surface(self.size).convert()
        self._bg_color = "black"
        self._bg_image: Optional[pygame.Surface] = None

        self._group = pygame.sprite.Group()
        self._type_groups: Dict[str, ComponentGroup] = {}
        self._subgroups: List[pygame.sprite.Group] = (
            []
        )  # subgroups to be rendered in this interface

        self._components: List[Component] = []
        self._style_classes = styles

        self._parse_background(background)
        self._parse_components(components)

    @classmethod
    def set_conversion_tables(
        cls,
        component: Optional[Dict[str, Component]],
        group: Optional[Dict[str, ComponentGroup]],
    ) -> None:
        """
        Sets up the tables for component conversion.

        :param component: Component conversion table.
        :param group: Group conversion table.
        """

        cls.COMPONENT_CONVERSION_TABLE = component
        cls.GROUP_CONVERSION_TABLE = group

    def _parse_background(self, bg) -> None:
        """
        Tries to load the 'background' interface attribute as an image, if it fails, considers it a color and uses it to fill the surface.
        """

        try:
            img = pygame.image.load(os.path.abspath(bg)).convert()
            img = pygame.transform.scale(img, self.size)
            self._bg_image = img
        except:
            if bg is not None:
                self._bg_color = bg

    def _parse_components(self, components: List[Dict]) -> None:
        """
        Handles the parsing of the components loaded from the YAML interface file.

        :param interface_dict: Output of the YAML file load.
        """

        if self.display == "grid":
            # Calculate the size of a grid cell
            grid_width = self.size[0] // self.columns
            grid_height = self.size[1] // self.rows
        else:
            grid_width = grid_height = None

        for component in components:
            # Converts style class values
            self._parse_style_classes(component)

            # Converts percentage values
            self._parse_percentage_values(component, grid_width, grid_height)

            # Converts grid values
            self._parse_grid_values(
                component,
                grid_width,
                grid_height,
                self.columns,
            )

            # instantiates a component according to it's type
            c = Interface.COMPONENT_CONVERSION_TABLE[component["type"].lower()](
                **component,
                interface=self.name,
            )
            self._components.append(c)

            # verifies if there's not a component group for it's type yet
            if c.type not in self._type_groups:
                self._handle_new_type_group(c)

            # adds the component to it's groups
            self._type_groups[c.type].add(c)
            self._group.add(c)

    def _parse_percentage_values(
        self, component: Dict, gw: Optional[int] = None, gh: Optional[int] = None
    ) -> None:
        """
        Converts percentage values from a component's width, height, x and y atributes to integer values. PyInterfacer's WIDTH and HEIGHT atributes must be set for this to work.

        :param component: Dictionary representing the component.
        """

        # Use width and height values relative to the grid cell size, if component is positioned in a grid cell, otherwise relative to the window size
        width = gw if "grid_cell" in component else self.size[0]
        height = gh if "grid_cell" in component else self.size[1]

        if "width" in component and type(w := component["width"]) is str:
            if "%" in w:
                component["width"] = int(width * percent_to_float(w))
        if "height" in component and type(h := component["height"]) is str:
            if "%" in h:
                component["height"] = int(height * percent_to_float(h))

        # X and Y values are not taken into account for components with a grid cell specified, as they are always centered in their own cell
        if "x" in component and type(x := component["x"]) is str:
            if "%" in x:
                component["x"] = int(width * percent_to_float(x))
        if "y" in component and type(y := component["y"]) is str:
            if "%" in y:
                component["y"] = int(height * percent_to_float(y))

    def _parse_grid_values(
        self, component: Dict, gw: int, gh: int, columns: int
    ) -> None:
        """
        Converts the grid information into actual position and size information for each component.

        :param component: Dictionary representing the component.
        :param gw: Grid cell width.
        :param gh: Grid cell height.
        :param columns: Amount of columns in the grid.
        """

        if self.display != "grid":
            return

        if "grid_cell" in component:
            # calculate which row and column the component is at
            row = component["grid_cell"] // columns
            column = component["grid_cell"] % columns

            # centers the component position at it's grid position
            component["x"] = int((column * gw) + (gw / 2))
            component["y"] = int((row * gh) + (gh / 2))

            # if width and height are not provided, make the component use the grid's size instead; if they are provided as 'auto', use default component sizing behavior
            if "width" not in component:
                component["width"] = gw
            elif component["width"] == "auto":
                component["width"] = None
            if "height" not in component:
                component["height"] = gh
            elif component["height"] == "auto":
                component["height"] = None

    def _parse_style_classes(self, component: Dict) -> None:
        """
        Updates the component with it's style class attributes.

        :param component: Dictionary representing the component.
        """

        # Verifies if the component sets a valid style class
        if "style" in component and (s := component["style"]) in self._style_classes:
            # Use only the styles defined in the style class that are not "overwritten" in the component declaration
            for attr, value in self._style_classes[s].items():
                if attr not in component:
                    component[attr] = value

    def _handle_new_type_group(self, component: Component) -> None:
        """
        Creates new component groups for component types that don't have a group yet.

        :param component: A component instance.
        """

        # Verifies if the component's type or subtype have a special group that should be used
        if component.type in self.GROUP_CONVERSION_TABLE:
            self._type_groups[component.type] = Interface.GROUP_CONVERSION_TABLE[
                component.type
            ]()
        elif component.subtype in self.GROUP_CONVERSION_TABLE:
            self._type_groups[component.type] = Interface.GROUP_CONVERSION_TABLE[
                component.subtype
            ]()
        else:
            self._type_groups[component.type] = (
                ComponentGroup()
            )  # otherwise use the most generic ComponentGroup

    def update(self) -> None:
        """
        Updates the interface through `pygame.sprite.Group.update()`.
        """
        self._group.update()

        if len(self._subgroups) > 0:
            for group in self._subgroups:
                group.update()

    def draw(self, surface: pygame.Surface) -> None:
        """
        Draws this interface to `surface`.

        :param surface: Pygame Surface to render this interface to.
        """

        if self._bg_image:
            self.surface.blit(self._bg_image, (0, 0))
        else:
            self.surface.fill(self._bg_color)

        self._group.draw(self.surface)

        if len(self._subgroups) > 0:
            for group in self._subgroups:
                group.draw(self.surface)

        surface.blit(self.surface, (0, 0))

    def handle(self, surface: pygame.Surface) -> None:
        """
        Renders and updates the interface.

        :param surface: Pygame surface to render the interface to.
        """

        self.update()
        self.draw(surface)

    def emit_click(self) -> None:
        """
        Calls `Clickable.handle_click` for all `Clickable` components in the interface, through `ClickableGroup.handle_click`.
        """

        for group in self._type_groups:
            if isinstance((g := self._type_groups[group]), ClickableGroup):
                g.handle_click((self.name,))

    def emit_input(self, event) -> None:
        """
        Calls `Input.handle_input` for all `Input` components in the interface, through `InputGroup.handle_input`.

        :param event: Pygame KEYDOWN event.
        """

        for group in self._type_groups:
            if isinstance((g := self._type_groups[group]), InputGroup):
                g.handle_input(event, (self.name,))

    def handle_hover(self) -> None:
        """
        Calls `HoverableGroup.handle_hover` for all `Hoverable` components in the interface, through `HoverableGroup.handle_hover`
        """

        for group in self._type_groups:
            if isinstance((g := self._type_groups[group]), HoverableGroup):
                g.handle_hover((self.name,))

    def component_dict(self) -> Dict[str, Component]:
        """
        Returns a dictionary of the components in the interface, where `key` is the component ID, and `value` is the component instance.

        :returns: Components dictionary.
        """

        return {c.id: c for c in self._components}

    def add_subgroup(self, group: pygame.sprite.Group) -> None:
        """
        Adds a subgroup to the interface. Subgroups are rendered to the interface surface and updated. If the `group` was already added, ignore.

        :param group: A pygame Group to add to the subgroups.
        """

        if group not in self._subgroups:
            self._subgroups.append(group)
