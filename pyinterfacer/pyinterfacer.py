"""
@author: Gabriel RQ
@description: Main module for the PyInterfacer library. This module contains the PyInterfacer class, which is responsible for managing the interfaces, components and bindings. The class is a Singleton.
"""

import pygame
import os
import re
import typing
import yaml

from .interface import Interface, _ConversionMapping
from .components.handled import _HandledGetInput
from .components.standalone._clickable import _Clickable
from .managers import _OverlayManager, _BackupManager, _BindingManager, _KeyBinding
from .util import Singleton
from typing import Optional, Dict, Callable, Union, Literal, overload

if typing.TYPE_CHECKING:
    from .components.handled import _Component
    from .groups import ComponentGroup


class PyInterfacer(metaclass=Singleton):
    """Main PyInterfacer class."""

    def __init__(self) -> None:

        # Stores the file paths for the interfaces queued to be loaded
        self.__interface_queue = []

        # Stores all the interfaces. Each key represents an interface name.
        self._interfaces: Dict[str, Interface] = {}
        # Stores all the components. Each key represents an id.
        self._components: Dict[str, "_Component"] = {}

        self._display: Optional[pygame.Surface] = (
            pygame.display.get_surface() if pygame.display.get_active() else None
        )

        self._overlay = _OverlayManager(
            self.display.get_size() if self.display else (0, 0)
        )
        self._bindings = _BindingManager()

        self._current_focus: Optional[Interface] = None
        self._paused = False

        # Maps a component id (key) to an action callback (value). Used to map actions easily for Clickable components
        self._component_action_mapping: Dict[str, Callable] = {}

        self._backup = _BackupManager()

    # Properties

    @property
    def display(self) -> Optional[pygame.Surface]:
        return self._display

    @display.setter
    def display(self, d: pygame.Surface) -> None:
        self._display = d
        self._overlay.change_size(self.display.get_size())

    @property
    def overlay(self) -> _OverlayManager:
        return self._overlay

    @property
    def backup(self) -> _BackupManager:
        return self._backup

    @property
    def current_focus(self) -> Optional[Interface]:
        return self._current_focus

    # Loading and parsing

    def load_all(self, path: str) -> None:
        """
        Inserts all the interface files in the specified directory in the loading queue.

        :param path: Path to the directory containing the YAML interface files.
        """

        p = os.path.abspath(path)
        if not os.path.exists(p):
            raise _InvalidInterfaceDirectoryException(path)

        for interface_file in os.listdir(p):
            self.load(os.path.join(p, interface_file))

    def load(self, file: str) -> None:
        """
        Inserts the specified interface path into the loading queue.

        :param file: Path to the YAML interface file.
        """

        if re.match(r".*\.(yaml|yml)$", file) and os.path.exists(file):
            self.__interface_queue.append(file)
            self._backup.remember_interface_file(file)

    def unload(self, backup: bool = False) -> None:
        """
        Removes all loaded interfaces, components, overlays and action mappings.

        :param backup: Whether or not a backup of the current state should be kept. If a previous backup is stored, this will not have effect.
        """

        if backup and not self._backup.have_backup:
            self._backup.backup(self)

        self._current_focus = None
        self._interfaces.clear()
        self._components.clear()
        self._component_action_mapping.clear()
        self._overlay.clear()

    def reload(self, raw: bool = False) -> None:
        """
        Reloads the previously save PyInterfacer state. For this to have any effect, the `backup` parameter of `PyInterfacer.unload` must be passed as `True`. Once restored, the backup will be cleared.

        :param raw: If `True`, the interfaces will be reloaded from the original files (state is lost). If `False`, the interfaces will be reloaded from the stored backup (state is kept).
        """

        if self._backup.have_backup:
            self._backup.reload(self, raw)
            self._backup.clear()

    def init(self) -> None:
        """
        Initializes the interfaces in the loading queue.
        """

        for interface in self.__interface_queue:
            with open(interface, "r") as interface_file:
                interface_dict: Dict = yaml.safe_load(interface_file)

                if interface_dict is None:
                    raise _EmptyInterfaceFileException()

                if (
                    "interface" not in interface_dict
                    or "components" not in interface_dict
                ):
                    raise _InvalidInterfaceFileException()

                self._parse_interface(interface_dict)

        self.__interface_queue.clear()

    @overload
    def inject(self, component: Dict, interface: str) -> None:
        """
        Allows to programatically inject a component into an existing interface.

        :param component: Dictionary containing component data.
        :param interface: Name of the interface to inject the component into.
        """

        ...

    @overload
    def inject(self, interface: Dict) -> None:
        """
        Allows to programatically inject an interface dictionary into PyInterfacer.

        :param interface: Dictionary containing interface data.
        """

        ...

    def inject(self, d: Dict, i: Optional[str] = None) -> None:
        if i is None:
            self._parse_interface(d)
        else:
            interface = self._interfaces.get(i)
            if interface is not None:
                interface._parse_components([d])

    # Update and render

    def handle(self, dt: float = 1) -> None:
        """
        Calls `Interface.handle` in the currently focused interface. Also handles the global overlay.
        """

        if self._display is None:
            return

        if self._current_focus is not None and not self._paused:
            self._current_focus.handle(self._display, dt)

        self._overlay.update_interfaces(dt)
        self._overlay.render(self._display)

    def handle_event(self, event: pygame.Event) -> None:
        """
        Handles pygame events. This let's PyInterfacer handle it's Clickable and Input components, for example.

        :param event: Pygame event.
        """

        match event.type:
            case pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if self._current_focus is not None:
                        self._current_focus.emit_click(event.pos)
            case pygame.TEXTINPUT | pygame.TEXTEDITING:
                if _HandledGetInput.IS_ANY_ACTIVE and self._current_focus is not None:
                    self._current_focus.emit_input(event)
            case pygame.KEYDOWN:
                if _HandledGetInput.IS_ANY_ACTIVE and self._current_focus is not None:
                    self._current_focus.emit_input(event)
                else:
                    self._bindings.handle_single(event.key, type_="down")
            case pygame.KEYUP:
                if not _HandledGetInput.IS_ANY_ACTIVE:
                    self._bindings.handle_single(event.key, type_="up")

    # Focus handling

    def go_to(self, interface: str) -> None:
        """
        Changes the focus to the specified interface.

        :param interface: Name of the interface to switch to.
        """

        if interface is None:
            self._current_focus = None
            return

        # If the interface does not exist, the focus will not be changed
        if interface in self._interfaces:
            self._current_focus = self._interfaces.get(interface)

    def transition_to(self, interface: str) -> None:
        """
        Changes the focus to the specified interface, with a transition effect.

        :param interface: Name of the interface to switch to.
        """

        raise NotImplementedError

    # Utilities

    def get_component(self, id_: str) -> Optional["_Component"]:
        """
        Retrieves a component instance, searching by it's `id`.

        :param id_: The component's `id`.
        :return: The component instance, if found, otherwise `None`.
        """

        return self._components.get(id_)

    def get_interface(self, name: str) -> Optional[Interface]:
        """
        Retrieves an interface instance, searching by it's name.

        :param interface: Name of the interface.
        :return: The interface instance, if found, otherwise `None`.
        """

        return self._interfaces.get(name)

    def add_custom_components(self, components: Dict[str, "_Component"]) -> None:
        """
        Inserts custom components in the component conversion table, allowing them to be used with the library. If the specified component types are already in the conversion table, they will be overwritten by the provided ones.

        :param components: A dictionary where the `keys` represent the type of the component, and the `values` represent a reference to the component class.
        """

        _ConversionMapping.extend_component_table(components)

    def add_custom_groups(self, groups: Dict[str, "ComponentGroup"]) -> None:
        """
        Inserts custom component groups for the specified component types in the group conversion table, allowing it to be used with the library. If `type` is already in the group conversion table, it will be overwritten.

        :param groups: A dictionary where the `keys` represent the type of the component, and the `values` represent a reference to the group class.
        """

        _ConversionMapping.extend_group_table(groups)

    def pause(self) -> None:
        """Halts the handling of the currently focused interface."""

        self._paused = True

    def unpause(self) -> None:
        """Resumes the handling of the currently focused interface."""

        self._paused = False

    def map_actions(self, actions: Dict[str, Callable]) -> None:
        """
        Maps a component to an action callback. Used to define actions for Clickable components. Components with the same ID will be mapped to the same action.

        :param actions: Actions mapping in the format `{id: callback}`.
        """

        self._component_action_mapping.update(actions)
        self._update_actions()

    @overload
    def bind(self, c1: str, a1: str, c2: str, a2: str):
        """
        Binds a component attribute to another component attribute.

        :param c1: ID of the component to bind.
        :param a1: Attribute of the component to bind.
        :param c2: ID of the component to bind to.
        :param a2: Attribute of the component to bind to.
        :return: The binding id.
        """

        ...

    @overload
    def bind(self, c1: str, a1: str, callback: Callable):
        """
        Binds a component attribute to a callback. The callback will receive the attribute value, and should return it's updated value.

        :param c1: ID of the component to bind.
        :param a1: Attribute of the component to bind.
        :param callback: Callback function that returns the value for the attribute.
        :return: The binding id.
        """

        ...

    def bind(
        self, c1: str, a1: str, c2: Union[str, Callable], a2: Optional[str] = None
    ):
        if isinstance(c2, str) and a2 is not None:
            if c1 in self._components and c2 in self._components:
                # binding is done at interface level
                i = self._interfaces.get(self._components[c1].interface)

                if i is not None:
                    return i.create_binding(
                        self._components[c1], a1, self._components[c2], a2
                    )
        elif callable(c2):
            if c1 in self._components:
                i = self._interfaces.get(self._components[c1].interface)

                if i is not None:
                    return i.create_binding(self._components[c1], a1, c2)

    def bind_keys(
        self, b: Dict[int, Dict[Literal["press", "release"], Callable]]
    ) -> None:
        """
        Binds a keypress to a callback.

        :param b: A mapping where the keys are integers (pygame key constants) and the values are dictionaries in the format {"press": Callback?, "release": Callback?}. At least one of the callbacks should be provided.
        """

        for k, v in b.items():
            if not isinstance(v, dict):
                continue

            bind = _KeyBinding(event=k)
            bind.on_press = v.get("press")
            bind.on_release = v.get("release")
            self._bindings.register(bind)

    # Internal methods

    def _parse_interface(self, interface_dict: Dict):
        """
        Parses an interface file from it's YAML declaration.

        :param interface_dict: Dictionary loaded from the YAML file.
        """

        # Checks if the display type is specified
        if "display" not in interface_dict or interface_dict["display"] not in (
            "default",
            "grid",
            "overlay",
        ):
            raise _InvalidDisplayTypeException(interface_dict["interface"])

        # Checks if grid display declaration is complete
        if interface_dict["display"] == "grid" and (
            "rows" not in interface_dict or "columns" not in interface_dict
        ):
            raise _InvalidDisplayTypeException(interface_dict["interface"])

        # Checks if a display has been set, if not, fallback to the display initialized from pygame.display.set_mode
        if self._display is None:
            if pygame.display.get_active():
                self.display = pygame.display.get_surface()
            else:
                raise _UndefinedDisplaySurfaceException()

        # Checks if any component style class has been defined for the interface
        if "styles" in interface_dict and len(interface_dict["styles"]) > 0:
            s = {style["name"]: style for style in interface_dict["styles"]}
        else:
            s = None

        # Creates a new interface and stores it
        i = Interface(
            name=interface_dict.get("interface"),
            background=interface_dict.get("background"),
            size=self._display.get_size(),
            components=interface_dict.get("components"),
            display=interface_dict.get("display"),
            rows=interface_dict.get("rows"),
            columns=interface_dict.get("columns"),
            styles=s,
        )
        self._interfaces[i.name] = i
        self._components.update(i.component_mapping)

        for c in i.components:
            c.after_load(i)

        # Updates actions for Clickable components
        self._update_actions()

        if i.display == "overlay":
            self._overlay.add_interface_target(i)

    def _update_actions(self) -> None:
        """
        Updates actions for Clickable components using the component action mapping.
        """

        if len(self._component_action_mapping) == 0:
            return

        for id_ in self._component_action_mapping.keys():
            c = self._components.get(id_)

            if isinstance(c, _Clickable):
                c.action = self._component_action_mapping[id_]

    # Magic operators

    def __getitem__(self, interface: str) -> Optional[Interface]:
        return self._interfaces.get(interface)


"""
Exceptions
"""


class _EmptyInterfaceFileException(Exception):
    def __init__(self) -> None:
        super().__init__("The provided YAML interface file can't be empty.")


class _InvalidInterfaceFileException(Exception):
    def __init__(self) -> None:
        super().__init__(
            "The provided YAML interface file is not in valid format. Be sure to include the interface name and the components."
        )


class _InvalidDisplayTypeException(Exception):
    def __init__(self, interface: str) -> None:
        super().__init__(
            f"The specified display type for the interface '{interface}' is invalid. It should be one of 'default', 'grid' or 'overlay'. Note that grid displays shoud provide 'rows' and 'columns'."
        )


class _InvalidInterfaceDirectoryException(Exception):
    def __init__(self, dir_: str) -> None:
        super().__init__(
            f"The specified directory ({dir_}) does not exist or is invalid. Could not load any interface."
        )


class _UndefinedDisplaySurfaceException(Exception):
    def __init__(self) -> None:
        super().__init__(
            "No Surface has been set as a display for PyInterfacer, and pygame.display.set_mode was not called. There's no fallback possible. Either provide a Surface or call pygame.display.set_mode."
        )
