"""
@author: Gabriel RQ
@description: PyInterfacer class. This is the main class of the library, and it manages all the loaded interfaces.
"""

"""
PROPOSAL: Create an action mapping where the keys are the ID of some 'Clickable' component and the values are the actions they should execute. This would make setting actions for 'Clickable' components much easier.

PROPOSAL: Make PyInterfacer save a pickle serialized file of itself when interfaces are loaded, check if this file exists before loading, and deserialize it if it does. Should be even faster than parsing every interface each time the program is executed.
"""

import pygame
import yaml
import os
import re

from typing import Optional, Dict
from enum import Enum
from .interface import Interface
from .groups import *
from .components import *


class PyInterfacer:
    """PyInterfacer interface manager."""

    _display: pygame.Surface = None
    _current_focus: Optional[Interface] = None

    # Stores all the interfaces. Each key represents an interface name.
    INTERFACES: Dict[str, Interface] = {}
    # Stores all the components. Each key represents an id.
    COMPONENTS: Dict[str, Component] = {}

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
    def set_display(cls, display: pygame.Surface) -> None:
        """
        Sets the display to render to.

        :param display: Pygame Surface.
        """
        cls._display = display

    @classmethod
    def load_all(cls, path: str) -> None:
        """
        Loads all the interface files in a directory.

        :param path: Path to the directory containing the YAML interface files.
        """

        p = os.path.abspath(path)
        if os.path.exists(p):
            for interface_file in os.listdir(p):
                cls.load(os.path.join(p, interface_file))

    @classmethod
    def load(cls, file: str) -> None:
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

                cls._parse_interface(interface_dict)

    @classmethod
    def unload(cls) -> None:
        """
        Removes all loaded interfaces. Not safe to call while updating or rendering any interface.
        """

        cls.INTERFACES.clear()
        cls.COMPONENTS.clear()

    @classmethod
    def _parse_interface(cls, interface_dict: Dict):
        """
        Parses a interface file from it's YAML declaration.

        :param interface_dict: Dictionary loaded from the YAML file.
        """

        # Checks if the display type is specified
        if "display" not in interface_dict or interface_dict["display"] not in (
            "default",
            "grid",
        ):
            raise InvalidDisplayTypeException(interface_dict["interface"])

        # Checks if grid display declaration is complete
        if interface_dict["display"] == "grid" and (
            "rows" not in interface_dict or "columns" not in interface_dict
        ):
            raise InvalidDisplayTypeException(interface_dict["interface"])

        # Sets the conversion table for the interfaces
        Interface.set_conversion_tables(
            component=cls._COMPONENT_CONVERSION_TABLE,
            group=cls._GROUP_CONVERSION_TABLE,
        )

        # Checks if a display has been set, if not, fallback to the display initialized from pygame.display.set_mode
        if cls._display is None:
            if pygame.display.get_active():
                cls._display = pygame.display.get_surface()

        # Checks if any component style class has been defined for the interface
        if "styles" in interface_dict and len(interface_dict["styles"]) > 0:
            s = {style["name"]: style for style in interface_dict["styles"]}
        else:
            s = None

        # Creates a new interface and stores it
        i = Interface(
            name=interface_dict.get("interface"),
            background=interface_dict.get("background"),
            size=cls._display.get_size(),
            components=interface_dict.get("components"),
            display=interface_dict.get("display"),
            rows=interface_dict.get("rows"),
            columns=interface_dict.get("columns"),
            styles=s,
        )
        cls.INTERFACES[i.name] = i
        cls.COMPONENTS.update(i.component_dict())

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
    def get_by_id(cls, id_: str) -> Optional[Component]:
        """
        Retrieves a component instance, searching by it's `id`.

        :param id_: The component's `id`.
        :return: The component instance, if found, otherwise `None`.
        """

        return cls.COMPONENTS.get(id_)

    @classmethod
    def update(cls) -> None:
        """
        Updates the currently currently focused interface.
        """

        if cls._current_focus is not None:
            cls._current_focus.update()

    @classmethod
    def draw(cls) -> None:
        """
        Draws the currently focused interface to the display.
        """

        if cls._current_focus is not None:
            cls._current_focus.draw(cls._display)

    @classmethod
    def handle(cls) -> None:
        """
        Updates, renders and handles hover events in the currently focused interface.
        """

        if cls._current_focus is not None:
            cls.update()
            cls.draw()
            cls.handle_hover()

    @classmethod
    def change_focus(cls, interface: str) -> None:
        """
        Changes the currently focused interface.

        :param interface: Name of the interface to give focus.
        """

        if interface in cls.INTERFACES:
            cls._current_focus = cls.INTERFACES[interface]

    @classmethod
    def get_focused(cls) -> Optional[Interface]:
        """
        Gives access to the currently focused interface instance.

        :return: Currently focused interface.
        """

        return cls._current_focus

    @classmethod
    def get_interface(cls, interface: str) -> Optional[Interface]:
        """
        Retrieves an interface instance by it's name.

        :param interface: Name of the interface.
        :return: The interface instance, if found, otherwise `None`.
        """

        return cls.INTERFACES.get(interface)

    @classmethod
    def emit_click(cls) -> None:
        """
        Emits a click event on the currently focused interface.
        """

        if cls._current_focus is not None:
            cls._current_focus.emit_click()

    @classmethod
    def emit_input(cls, event) -> None:
        """
        Emits an input event in the currently focused interface.

        :param event: Pygame KEYDOWN event.
        """

        if cls._current_focus is not None:
            cls._current_focus.emit_input(event)

    @classmethod
    def handle_hover(cls) -> None:
        """
        Handles hover in the currently focused interface.
        """

        if cls._current_focus is not None:
            cls._current_focus.handle_hover()

    @classmethod
    def bind(cls, c1: str, a1: str, c2: str, a2: str) -> None:
        """
        Binds a component attribute to another component attribute.

        :param c1: ID of the component to bind.
        :param a1: Attribute of the component to bind.
        :param c2: ID of the component to bind to.
        :param a2: Attribute of the component to bind to.
        """

        if c1 in cls.COMPONENTS and c2 in cls.COMPONENTS:
            # binding is done at interface level
            i = cls.get_interface(cls.COMPONENTS[c1].interface)
            
            if i is not None:
                i.create_binding(cls.COMPONENTS[c1], a1, cls.COMPONENTS[c2], a2)


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
            f"The specified display type for the interface '{interface}' is invalid. It should be either 'default' or 'grid'. Note that grid displays shoud provide 'rows' and 'columns'."
        )
