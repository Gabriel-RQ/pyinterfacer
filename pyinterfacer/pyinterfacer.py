"""
@author: Gabriel RQ
@description: PyInterfacer class. This is the main class of the library, and it manages all the loaded interfaces.
"""

import pygame
import yaml
import os
import re

from typing import Optional, Dict, Callable, Union, Tuple, Literal, overload
from enum import Enum
from .interface import Interface
from .groups import *
from .components import *
from .util import OverlayManager


"""
PROPOSAL: Add display type 'overlay' to interfaces. Interfaces with this display type would be rendered into the overlay, effectively being always rendered.

PROPOSAL: Add a way to 'inject' programatically created components into an interface. That would allow to create components when the data needed to create them is dynamic.

PROPOSAL: Add a 'reload' method, allowing to completely reload all the interfaces. Could be used when changing resolution, for example.

PROPOSAL: Add a callback to run after initializing each component, allowing to execute code directly after instantiating a component.

PROPOSAL: Add a 'when' callback. It should receive a condition, and when it is true, a callback is executed.

TODO: Looks like PyInterfaceer.update() -> Interface.update() -> Component.update() is not setting Component.image when first called (how?). Steps to reproduce:
    - Run pong example
    - Let one of the sides score
    - The game will break: TypeError: Source objects must be a surface
    - Printing each sprite and it's image attribute in Interface.draw shows that Component.image is None when Pong tries to change focus.
    - Calling self.update (presumably self.preload_image as well) on the listed components with no image solves the issue.
OBS: Defined Component.image and Component.rect at the constructor. It fixed the issue. It seems that when PyInterfacer.change_focus is called, the handling of the current focus continue wherever it stoped, instead of restarting through the .update() methods, which can cause it to resume on .draw() when there was no image and rect defined for the Component.
"""


class PyInterfacer:
    """PyInterfacer interface manager."""

    _display: pygame.Surface = None
    _overlay = OverlayManager()
    _current_focus: Optional[Interface] = None

    # Stores all the interfaces. Each key represents an interface name.
    INTERFACES: Dict[str, Interface] = {}
    # Stores all the components. Each key represents an id.
    COMPONENTS: Dict[str, Component] = {}

    # Stores all the key bindings. Each key represents a pygame key constant.
    _KEY_BINDINGS: Dict[int, Callable] = {}
    _KEYUP_BINDINGS: Dict[int, Callable] = {}

    # Maps a component type (key) a component class (value). Used to handle conversion from YAML loaded components to their instances
    _COMPONENT_CONVERSION_TABLE: Dict[str, Component] = {
        "animation": Animation,
        "button": Button,
        "clickable": Clickable,
        "component": Component,
        "hoverable": Hoverable,
        "image": Image,
        "input": Input,
        "paragraph": Paragraph,
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

    # Maps a component id (key) to an action callback (value). Used to map actions easily for Clickable components
    _COMPONENT_ACTION_MAPPING: Dict[str, Callable] = {}

    @classmethod
    def set_display(cls, display: pygame.Surface) -> None:
        """
        Sets the display to render to.

        :param display: Pygame Surface.
        """

        cls._display = display
        cls._overlay.set_overlay(
            pygame.Surface((cls._display.get_size()), pygame.SRCALPHA).convert_alpha()
        )

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
        else:
            raise InvalidInterfaceDirectoryException(path)

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

        cls._current_focus = None
        cls._overlay = None
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
                cls.set_display(pygame.display.get_surface())
            else:
                raise UndefinedDisplaySurfaceException()

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

        for c in i.components:
            c.after_load(i)

        # Updates actions for Clickable components
        cls._update_actions()

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

        if cls._overlay is not None:
            if (o := cls._overlay.render()) is not None:
                cls._display.blit(o, (0, 0))

    @overload
    @classmethod
    def add_to_overlay(
        cls, source: pygame.Surface, dest: pygame.Rect | Tuple[int, int]
    ) -> None:
        """
        Renders a surface to the global overlay using `pygame.Surface.blit`.

        :param source: A pygame Surface.
        :param dest: A pygame Rect or a Coordinate (x, y).
        """

        ...

    @overload
    @classmethod
    def add_to_overlay(cls, blit_sequence: Tuple[Tuple, ...]) -> None:
        """
        Renders many images to the global overlay using `pygame.Surface.blits`.

        :param blit_sequence: Tuples in the format (source, dest, area?, special_flags?).
        """

        ...

    @classmethod
    def add_to_overlay(
        cls,
        p1: Tuple | pygame.Surface,
        p2: Optional[pygame.Rect | Tuple[int, int]] = None,
    ) -> None:
        if cls._overlay is None:
            return

        # if drawing many images
        if isinstance(p1, tuple) and p2 is None:
            cls._overlay.add_many_targets(p1)
        elif isinstance(p1, pygame.Surface) and p2 is not None:
            cls._overlay.add_single_target(p1, p2)

    @classmethod
    def clear_overlay(cls) -> None:
        """
        Clears the overlay surface.
        """

        if cls._overlay is not None:
            cls._overlay.clear()

    @classmethod
    def set_overlay_opacity(cls, o: int) -> None:
        """
        Sets the overlay opacity.

        :param o: An integer value ranging from 0 to 255.
        """

        if cls._overlay is not None:
            cls._overlay.set_opacity(o)

    @classmethod
    def get_overlay_opacity(cls) -> int:
        """Returns the overlay opacity. If the overlay is not set, returns '-1'."""

        if cls._overlay is None:
            return -1

        return cls._overlay.get_opacity()

    @classmethod
    def restore_overlay(cls) -> None:
        """Restores the last rendered surfaces to the overlay."""

        if cls._overlay is not None:
            cls._overlay.restore()

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
    def change_focus(cls, interface: Optional[str]) -> None:
        """
        Changes the currently focused interface.

        :param interface: Name of the interface to give focus.
        """

        if interface is None:
            cls._current_focus = None
            return

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
    def bind_keys(
        cls, b: Dict[int, Dict[Literal["press", "release"], Callable]]
    ) -> None:
        """
        Binds a keypress to a callback.

        :param b: A mapping where the keys are integers (pygame key constants) and the values are dictionaries in the format {"press": Callback?, "release": Callback?}. At least one of the callbacks should be provided.
        """

        for k, v in b.items():
            if not isinstance(v, dict):
                continue

            if "press" in v and callable((d := v["press"])):
                cls._KEY_BINDINGS[k] = d
            if "release" in v and callable((u := v["release"])):
                cls._KEYUP_BINDINGS[k] = u

    @classmethod
    def handle_event(cls, event: pygame.Event) -> None:
        """
        Handles pygame events. This let's PyInterfacer handle it's Clickable and Input components, for example.

        :param event: Pygame event.
        """

        match event.type:
            case pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    cls.emit_click()
            case pygame.TEXTINPUT | pygame.TEXTEDITING:
                if Input.IS_ANY_ACTIVE:
                    cls.emit_input(event)
            case pygame.KEYDOWN:
                if Input.IS_ANY_ACTIVE:
                    cls.emit_input(event)
                else:
                    if (b := cls._KEY_BINDINGS.get(event.key)) is not None:
                        b()
            case pygame.KEYUP:
                if (
                    not Input.IS_ANY_ACTIVE
                    and (b := cls._KEYUP_BINDINGS.get(event.key)) is not None
                ):
                    b()

    @classmethod
    def handle_hover(cls) -> None:
        """
        Handles hover in the currently focused interface.
        """

        if cls._current_focus is not None:
            cls._current_focus.handle_hover()

    @overload
    @classmethod
    def bind(cls, c1: str, a1: str, c2: str, a2: str) -> None:
        """
        Binds a component attribute to another component attribute.

        :param c1: ID of the component to bind.
        :param a1: Attribute of the component to bind.
        :param c2: ID of the component to bind to.
        :param a2: Attribute of the component to bind to.
        """

        ...

    @overload
    @classmethod
    def bind(cls, c1: str, a1: str, callback: Callable) -> None:
        """
        Binds a component attribute to a callback. The callback will receive the attribute value, and should return it's updated value.

        :param c1: ID of the component to bind.
        :param a1: Attribute of the component to bind.
        :param callback: Callback function that returns the value for the attribute.
        """

        ...

    @classmethod
    def bind(
        cls, c1: str, a1: str, c2: Union[str, Callable], a2: Optional[str] = None
    ) -> None:
        if isinstance(c2, str) and a2 is not None:
            if c1 in cls.COMPONENTS and c2 in cls.COMPONENTS:
                # binding is done at interface level
                i = cls.get_interface(cls.COMPONENTS[c1].interface)

                if i is not None:
                    i.create_binding(cls.COMPONENTS[c1], a1, cls.COMPONENTS[c2], a2)
        elif callable(c2):

            if c1 in cls.COMPONENTS:
                i = cls.get_interface(cls.COMPONENTS[c1].interface)

                if i is not None:
                    i.create_binding(cls.COMPONENTS[c1], a1, c2)

    @classmethod
    def map_actions(cls, actions: Dict[str, Callable]) -> None:
        """
        Maps a component to an action callback. Used to define actions for Clickable components.

        :param actions: Actions mapping in the format `{id: callback}`.
        """

        cls._COMPONENT_ACTION_MAPPING.update(actions)
        cls._update_actions()

    @classmethod
    def _update_actions(cls) -> None:
        """
        Updates actions for Clickable components using the component action mapping.
        """

        if len(cls._COMPONENT_ACTION_MAPPING) == 0:
            return

        for id_ in cls._COMPONENT_ACTION_MAPPING.keys():
            c = cls.COMPONENTS.get(id_)

            if isinstance(c, Clickable):
                c.action = cls._COMPONENT_ACTION_MAPPING[id_]


class DefaultComponentTypes(Enum):
    """Types of all the components in the default component set."""

    ANIMATION = "animation"
    BUTTON = "button"
    CLICKABLE = "clickable"
    COMPONENT = "component"
    HOVERABLE = "hoverable"
    IMAGE = "image"
    INPUT = "input"
    PARAGRAPH = "paragraph"
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


class InvalidInterfaceDirectoryException(Exception):
    def __init__(self, dir_: str) -> None:
        super().__init__(
            f"The specified directory ({dir_}) does not exist or is invalid. Could not load any interface."
        )


class UndefinedDisplaySurfaceException(Exception):
    def __init__(self) -> None:
        super().__init__(
            "No Surface has been set as a display for PyInterfacer, and pygame.display.set_mode was not called. There's no fallback possible. Either provide a Surface or call pygame.display.set_mode."
        )
