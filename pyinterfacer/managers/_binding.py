"""
@author: Gabriel RQ
@description: This module declares the bindings used in PyInterfacer.
"""

import typing

from typing import Literal, Callable, Any, Tuple, Union, Optional, Dict
from uuid import UUID, uuid4

if typing.TYPE_CHECKING:
    from ..components import Component


class _BindingManager:
    """Simple manager to handle bindings."""

    def __init__(self) -> None:
        self._bindings: Dict[UUID, _Binding] = {}

    def register(self, b: "_Binding") -> UUID:
        """
        Register a new binding to be handled.

        :param b: Binding.
        """

        self._bindings[b.identifier] = b
        return b.identifier

    def unregister(self, id_: UUID) -> None:
        """
        Unregister the binding from the bindings mapping.

        :param id_: ID of the binding to be unregistered.
        """

        if id_ in self._bindings:
            del self._bindingsd[id_]

    def clear(self) -> None:
        """Clears the binding mapping."""

        self._bindings.clear()

    def handle(self, *args, **kwargs) -> None:
        """Handles all bindings."""

        for b in self._bindings.values():
            id_ = b.handle(*args, **kwargs)

            # Check if the binding should be unregistered
            if id_ is not None:
                self.unregister(id_)

    def handle_single(self, id_: UUID, *args, **kwargs) -> None:
        """
        Handles a single binding.

        :param id_: The id of the binding to handle.
        """

        b = self._bindings.get(id_)

        if b is not None:
            bid = b.handle(*args, **kwargs)

            if bid is not None:
                self.unregister(bid)


class _Binding:
    """Base Binding class."""

    def __init__(self) -> None:
        self._id = uuid4()

    @property
    def identifier(self):
        return self._id

    # Bindings should return their identifier in handle when they are to be unregistered after executed
    def handle(self, *args, **kwargs) -> Union[None, "UUID"]: ...


class _ComponentBinding(_Binding):
    """Binds a component to another, or a component to a callback."""

    def __init__(self, type_: Literal["component", "callback"]) -> None:
        super().__init__()

        self._type = type_
        self._callback: Callable = None

        self._from_component: "Component" = None
        self._to_component: "Component" = None
        self._from_attr: str = None
        self._to_attr: str = None

    def set_component_binding(
        self, from_: Tuple["Component", str], to: Tuple["Component", str]
    ) -> None:
        """
        Sets the configuration for a component to component binding.

        :param from_: Tuple where the first index is the Component instance and the second index the component's attribute.
        :param to: Tuple where the first index is the Component instance  and the second index the component's attribute to bind to.
        """

        self._from_component = from_[0]
        self._from_attr = from_[1]
        self._to_component = to[0]
        self._to_attr = to[1]

    def set_callback_binding(
        self, from_: Tuple["Component", str], callback: Callable[[Any], Any]
    ) -> None:
        """
        Sets a configuration for a component to callback binding.

        :param from_: Tuple where the first index is the Component instance and the second index the component's attribute.
        :parma callback: Callback to bind the attribute to.
        """

        self._to_component = from_[0]
        self._to_attr = from_[1]
        self._callback = callback

    def handle(self, *args, **kwargs) -> None:
        """
        Handles the binding operation. Commonly called at the `Interface.update`.
        """

        if self._type == "component":
            # the binding must convert the value to the type of the attribute it's binding to
            to_type = type(getattr(self._to_component, self._to_attr))
            setattr(
                self._to_component,
                self._to_attr,
                to_type(getattr(self._from_component, self._from_attr)),
            )
        elif self._type == "callback":
            # it will set the attribute value to it's updated version, returned by the callback
            setattr(
                self._to_component,
                self._to_attr,
                self._callback(getattr(self._to_component, self._to_attr)),
            )


class _ConditionBinding(_Binding):
    """Binds a condition to a callback."""

    def __init__(
        self,
        condition: Callable[[None], bool],
        callback: Callable[[None], None],
        keep: bool = False,
    ) -> None:
        super().__init__()

        self._condition = condition
        self._callback = callback
        self._keep = keep

    def handle(self, *args, **kwargs):
        """Tests for the condition and executes the callback if truthy. Commonly caleed at `Interface.update`."""

        if self._condition():
            self._callback()

            if not self._keep:
                return self.identifier


class _KeyBinding(_Binding):
    """Binds a pygame key event to a callback. The identifier of a _KeyBindings is the event."""

    def __init__(
        self,
        event: int,
        on_kup: Optional[Callable] = None,
        on_kdown: Optional[Callable] = None,
    ) -> None:
        super().__init__()

        self._id = event  # keybindings will use the pygame key event as their id, allowing for easier access
        self._event = event
        self._on_kup: Callable = on_kup
        self._on_kdown: Callable = on_kdown

    @property
    def event(self) -> int:
        return self._event

    @property
    def on_release(self) -> Optional[Callable]:
        return self._on_kup

    @on_release.setter
    def on_release(self, c: Callable) -> None:
        self._on_kup = c

    @property
    def on_press(self) -> Optional[Callable]:
        return self._on_kdown

    @on_press.setter
    def on_press(self, c: Callable) -> None:
        self._on_kdown = c

    def handle(self, *args, **kwargs) -> None | UUID:
        """
        Calls the callback for the event type.

        :param type_: The event type. Either "up" or "down.
        """

        e: Literal["up", "down"] = kwargs.get("type_")

        if e is not None:
            if all((e == "up", self._on_kup is not None, callable(self._on_kup))):
                self._on_kup()
            elif all(
                (e == "down", self._on_kdown is not None, callable(self._on_kdown))
            ):
                self._on_kdown()
