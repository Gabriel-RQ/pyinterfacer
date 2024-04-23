"""
@author: Gabriel RQ
@description: This file declares the bindings used in PyInterfacer.
"""

import typing

from typing import Literal, Callable, Any, Tuple, Union
from uuid import uuid4

if typing.TYPE_CHECKING:
    from ..components import Component
    from uuid import UUID


class _Binding:
    """Base Binding class."""

    def __init__(self) -> None:
        self._id = uuid4()

    @property
    def identifier(self):
        return self._id

    def handle(self, *args, **kwargs) -> Union[None, "UUID"]: ...

    @staticmethod
    def unregister(id_: "UUID", bindings: dict) -> None:
        """
        Unregister the binding from the bindings mapping.

        :param id_: ID of the binding to be unregistered.
        :param bindings: A mapping of bindings.
        """

        del bindings[id_]


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
