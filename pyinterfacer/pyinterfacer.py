"""
@author: Gabriel RQ
@description: PyInterfacer class. This is the main class of the library, and it manages all the loaded interfaces.
"""

import pygame
import yaml
import os
import re

from collections import Counter, defaultdict
from typing import Optional, Dict, DefaultDict, List, Tuple
from enum import Enum
from .groups import *
from .components import *
from .util import percent_to_float


class PyInterfacer:
    """PyInterfacer interface manager."""

    WIDTH, HEIGHT = None, None

    # Keeps track of how many interfaces and components of each type are loaded
    STATS = Counter()

    # Holds the name of the interface with the current focus for rendering and updating
    _current_focus: str = None

    # Stores all the groups (general group, component type groups, interface groups)
    GROUPS = {
        "generic": ComponentGroup(),
        "interfaces": defaultdict(ComponentGroup),
        "types": {},
    }

    # Stores all the components, grouped by their interface
    COMPONENTS: DefaultDict[str, List[Component]] = defaultdict(list)

    # Maps a component type (key) a component class (value). Used to handle conversion from YAML loaded components to their instances
    _COMPONENT_CONVERSION_TABLE: Dict[str, Component] = {
        "animation": Animation,
        "button": Button,
        "clickable": Clickable,
        "component": Component,
        "hoverable": Hoverable,
        "image": Image,
        "input": Input,
        "spritesheet-animation": SpritesheetAnimation,
        "text-button": TextButton,
        "text": Text,
    }
    # Maps a component type (key) to a component group. Used to handle the creation of specific groups for some component types. Component types not in this dictionary are added to a ComponentGroup by default
    _GROUP_CONVERSION_TABLE: Dict[str, ComponentGroup] = {
        "clickable": ClickableGroup,
        "hoverable": HoverableGroup,
        "button": ButtonGroup,
        "text-button": ButtonGroup,
        "input": InputGroup,
    }

    @classmethod
    def set_size(cls, w: int, h: int) -> None:
        """
        Sets the display size.
        :param w: Display width.
        :param h: Display height.
        """
        cls.WIDTH = w
        cls.HEIGHT = h

    @classmethod
    def load_all(cls, path: str) -> None:
        """
        Loads all the interface files in a directory.

        :param path: Path to the directory containing the YAML interface files.
        """

        p = os.path.abspath(path)
        if os.path.exists(p):
            for interface_file in os.listdir(p):
                cls.load_interface(os.path.join(p, interface_file))

    @classmethod
    def load_interface(cls, file: str) -> None:
        """
        Loads the specified interface file.

        :param file: Path to the YAML interface file.
        """

        if re.match(r".*\.(yaml|yml)$", file):
            with open(file, "r") as interface_file:
                interface_dict: Dict = yaml.safe_load(interface_file)

                if interface_dict is None:
                    raise EmptyInterfaceFileException()

                if (
                    "interface" not in interface_dict
                    or "components" not in interface_dict
                ):
                    raise InvalidInterfaceFileException()

                cls._parse_components(interface_dict)

    @classmethod
    def _parse_components(cls, interface_dict: Dict) -> None:
        """
        Handles the parsing of the components loaded from the YAML interface file.

        :param interface_dict: Output of the YAML file load.
        """

        # If HEIGHT and WIDTH are not set, fallback to pygame's set display size
        if cls.WIDTH is None and cls.HEIGHT is None:
            cls.WIDTH, cls.HEIGHT = pygame.display.get_window_size()

        # Checks if the display type is specified
        if "display" not in interface_dict or interface_dict["display"] not in (
            "default",
            "grid",
        ):
            raise InvalidDisplayTypeException(interface_dict["interface"])

        display_type = interface_dict["display"]

        if display_type == "grid":
            # fallback to 'default' display if rows and columns are not specified
            if "rows" not in interface_dict or "columns" not in interface_dict:
                display_type = "default"
            else:
                # otherwise calculate the size of each grid
                grid_width = cls.HEIGHT // interface_dict["rows"]
                grid_height = cls.WIDTH // interface_dict["columns"]

        for component in interface_dict["components"]:

            # Converts percentage values
            cls._parse_percentage_values(component, grid_width, grid_height)

            if display_type == "grid":
                cls._parse_grid_values(
                    component,
                    grid_width,
                    grid_height,
                    interface_dict["columns"],
                )

            # instantiates a component according to it's type
            c = cls._COMPONENT_CONVERSION_TABLE[component["type"].lower()](
                **component,
                interface=interface_dict["interface"],
            )
            cls.COMPONENTS[interface_dict["interface"]].append(c)

            # verifies if there's not a component group for it's type yet
            if c.type not in cls.GROUPS["types"]:
                cls._handle_new_type_group(c)

            # add the component to the groups
            cls.GROUPS["generic"].add(c)
            cls.GROUPS["types"][c.type].add(c)
            cls.GROUPS["interfaces"][interface_dict["interface"]].add(c)

            # updates the stats
            cls.STATS[interface_dict["interface"]] += 1
            cls.STATS[c.type] += 1

    @classmethod
    def _parse_percentage_values(
        cls, component: Dict, gw: Optional[int] = None, gh: Optional[int] = None
    ) -> None:
        """
        Converts percentage values from a component's width, height, x and y atributes to integer values. PyInterfacer's WIDTH and HEIGHT atributes must be set for this to work.

        :param component: Dictionary representing the component.
        """

        # Use width and height values relative to the grid cell size, if component is positioned in a grid cell, otherwise relative to the window size
        width = gw if "grid_cell" in component else cls.WIDTH
        height = gh if "grid_cell" in component else cls.HEIGHT

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

    @classmethod
    def _parse_grid_values(
        cls, component: Dict, gw: int, gh: int, columns: int
    ) -> None:
        """
        Converts the grid information into actual position and size information for each component.

        :param component: Dictionary representing the component.
        :param gw: Grid cell width.
        :param gh: Grid cell height.
        :param columns: Amount of columns in the grid.
        """

        if "grid_cell" in component:
            # calculate which row and column the component is at
            row = component["grid_cell"] // columns
            column = component["grid_cell"] % columns

            # centers the component position at it's grid position
            # this should be inverted, be it don't work if it's inverted ???
            component["x"] = int((column * gh) + (gh / 2))
            component["y"] = int((row * gw) + (gw / 2))

            # if width and height are not provided, make the component use the grid's size instead; if they are provided as 'auto', use default component sizing behavior
            if "width" not in component:
                component["width"] = gw
            elif component["width"] == "auto":
                component["width"] = None
            if "height" not in component:
                component["height"] = gh
            elif component["height"] == "auto":
                component["height"] = None

    @classmethod
    def _handle_new_type_group(cls, component: Component):
        """
        Creates new component groups for component types that don't have a group yet.

        :param component: A component instance.
        """

        # Verifies if the component's type or subtype have a special group that should be used
        if component.type in cls._GROUP_CONVERSION_TABLE:
            cls.GROUPS["types"][component.type] = cls._GROUP_CONVERSION_TABLE[
                component.type
            ]()
        elif component.subtype in cls._GROUP_CONVERSION_TABLE:
            cls.GROUPS["types"][component.type] = cls._GROUP_CONVERSION_TABLE[
                component.subtype
            ]()
        else:
            cls.GROUPS["types"][
                component.type
            ] = ComponentGroup()  # otherwise use the most generic ComponentGroup

    @classmethod
    def add_custom_components(cls, components: Dict[str, Component]) -> None:
        """
        Inserts custom components in the component conversion table, allowing them to be used with the library. If the specified component types are already in the conversion table, they will be overwritten by the provided ones.

        :param components: A dictionary where the `keys` represent the type of the component, and the `values` represent a reference to the component class.
        """

        cls._COMPONENT_CONVERSION_TABLE.update(components)

    @classmethod
    def add_custom_groups(cls, groups: Dict[str, ComponentGroup]) -> None:
        """
        Inserts custom component groups for the specified component types in the group conversion table, allowing it to be used with the library. If `type` is already in the group conversion table, it will be overwritten.

        :param groups: A dictionary where the `keys` represent the type of the component, and the `values` represent a reference to the group class.
        """

        cls._GROUP_CONVERSION_TABLE.update(groups)

    @classmethod
    def get_by_id(
        cls, id_: str, interface: Optional[str] = None
    ) -> Optional[Component]:
        """
        Retrieves a component instance, searching by it's `id`. If `interface` is provided the search will consider only the specified `interface` components. Providing `interface` makes the search faster.

        :param id_: The component's `id`.
        :param interface: The component's parent `interface`.
        :return: The component instance, if found, otherwise `None`.
        """

        # if 'interface' is specified and exists in the components dict, limit the search
        if interface is not None and interface in cls.COMPONENTS:
            for component in cls.COMPONENTS[interface]:
                if component.id == id_:
                    return component
            else:
                return None

        for interface in cls.COMPONENTS:
            for component in cls.COMPONENTS[interface]:
                if component.id == id_:
                    return component

        return None

    @classmethod
    def get_by_interface(cls, interface: str) -> Optional[Tuple[Component]]:
        """
        Retrieves all the components instances for a given `interface`.

        :param interface: The interface from which the components are retrieved.
        :return: A tuple of the components instances, if any, otherwise None.
        """

        if interface in cls.COMPONENTS:
            return tuple(cls.COMPONENTS[interface])

        return None

    @classmethod
    def get_by_type(
        cls, type_: str, interface: Optional[str] = None
    ) -> Optional[Tuple[Component]]:
        """
        Retrieves all the components instances for a given component `type`. If `interface` is provided the search will consider only the specified `interface` components.

        :param type_: The `type` of components to search for.
        :param interface: The `interface` in which to search for the components.
        :return: A tuple of the components instances, if any, otherwise None.
        """

        # if 'interface' is specified and exists in the components dict, limit the search
        if interface is not None and interface in cls.COMPONENTS:
            c = tuple(
                [
                    component
                    for component in cls.COMPONENTS[interface]
                    if component.type == type_
                ]
            )

            if len(c) > 0:
                return c

            return None

        c = []
        for interface in cls.COMPONENTS:
            c.extend(
                [
                    component
                    for component in cls.COMPONENTS[interface]
                    if component.type == type_
                ]
            )

        if len(c) > 0:
            return tuple(c)

        return None

    @classmethod
    def update(cls, *interfaces: Tuple[str, ...]) -> None:
        """
        Updates all the components (Calling `Component.update` through `ComponentGroup.update`). If `interfaces` are provided, updates only the specified interface's components.

        :param interfaces: A tuple of the interfaces that should be updated.
        """

        cls.GROUPS["generic"].update(interfaces)

    @classmethod
    def draw(cls, surface: pygame.Surface, *interfaces: Tuple[str, ...]) -> None:
        """
        Renders all of the loaded components to the specified `surface`. If `interfaces` are provided, renders only the components contained in the specified `interfaces`.

        :param surface: A pygame Surface in which to render the components.
        :param interfaces: A tuple of `interfaces` whose components should be rendered.
        """

        cls.GROUPS["generic"].draw(surface, interfaces)

    @classmethod
    def change_focus(cls, interface: Optional[str]) -> None:
        """
        Changes the currently focused interface.

        :param interface: The interface that should be focused. Can be `None` in order to not set any focus.
        """

        if interface is not None and interface not in cls.GROUPS["interfaces"]:
            return

        cls._current_focus = interface

    @classmethod
    def get_focused(cls) -> str:
        """Returns the name of the currently focused interface."""
        return cls._current_focus

    @classmethod
    def update_focused(cls) -> None:
        """
        Updates all the components (Calling `Component.update` through `ComponentGroup.update`) in the currently focused interface.
        """

        if (
            cls._current_focus is not None
            and cls._current_focus in cls.GROUPS["interfaces"]
        ):
            cls.GROUPS["interfaces"][cls._current_focus].update()

    @classmethod
    def draw_focused(cls, surface: pygame.Surface) -> None:
        """
        Renders the components contained in the currently focused interface to the specified `surface`.

        :param surface: A pygame Surface in which to render the components.
        """
        if (
            cls._current_focus is not None
            and cls._current_focus in cls.GROUPS["interfaces"]
        ):
            cls.GROUPS["interfaces"][cls._current_focus].draw(surface)

    @classmethod
    def emit_click(cls, *interfaces: Tuple[str, ...]) -> None:
        """
        Calls `Clickable.handle_click` for all `Clickable` components, through `ClickableGroup.handle_click`. If `interfaces` are provided, emit the click only for the components in the specified `interfaces`. This also works to activate inputs, as a special case.

        :param interfaces: A tuple containing the names of the interfaces to limit the click event handling to.
        """

        for group in cls.GROUPS["types"]:
            if isinstance((g := cls.GROUPS["types"][group]), ClickableGroup):
                g.handle_click(interfaces)

    @classmethod
    def handle_hover(cls, *interfaces: Tuple[str, ...]) -> None:
        """
        Calls `HoverableGroup.handle_hover` for all `Hoverable` components, through `HoverableGroup.handle_hover`. If `interfaces` are provided, handles hover events only for the specified `interfaces`.

        :param interfaces: A tuple containing the name of the interfaces to limit the hover handling to.
        """

        for group in cls.GROUPS["types"]:
            if isinstance((g := cls.GROUPS["types"][group]), HoverableGroup):
                g.handle_hover(interfaces)

    @classmethod
    def emit_input(cls, event, *interfaces: Tuple[str, ...]) -> None:
        """
        Calls `Input.handle_input` for all `Input` components, through `InputGroup.handle_input`. If `interfaces` are provided, handles input events only for the specified `interfaces`.

        :param interfaces: A tuple containing the name of the interfaces to limit the input handling to.
        """

        for group in cls.GROUPS["types"]:
            if isinstance((g := cls.GROUPS["types"][group]), InputGroup):
                g.handle_input(event, interfaces)

    @classmethod
    def just_work(cls, surface: pygame.Surface) -> None:
        """
        Just works. Calls the relevant methods for a basic interface workflow. This method will call, in the following order:
            - PyInterfacer.update_focused
            - PyInterfacer.draw_focused(surface)
            - PyInterfacer.handle_hover(PyInterfacer.get_focused())

        It works with the currently focused interface.

        :param surface: The pygame `Surface` to render to.
        """

        cls.update_focused()
        cls.draw_focused(surface)
        cls.handle_hover(cls._current_focus)


class DefaultComponentTypes(Enum):
    """Types of all the components in the default component set."""

    ANIMATION = "animation"
    BUTTON = "button"
    CLICKABLE = "clickable"
    COMPONENT = "component"
    HOVERABLE = "hoverable"
    IMAGE = "image"
    INPUT = "input"
    SPRITESHEET_ANIMATION = "spritesheet-animation"
    TEXT_BUTTON = "text-button"
    TEXT = "text"


class EmptyInterfaceFileException(Exception):
    def __init__(self) -> None:
        super().__init__("The provided YAML interface file can't be empty.")


class InvalidInterfaceFileException(Exception):
    def __init__(self) -> None:
        super().__init__(
            "The provided YAML interface file is not in valid format. Be sure to include the interface name and the components."
        )


class InvalidDisplayTypeException(Exception):
    def __init__(self, interface: str) -> None:
        super().__init__(
            f"The specified display type for the interface '{interface}' is invalid. It should be either 'default' or 'grid'."
        )
