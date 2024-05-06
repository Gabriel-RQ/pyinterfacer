"""
@author: Gabriel RQ
@description: Defines the components handled by PyInterfacer.
"""

import typing

from ..standalone._standalone_component import _StandaloneComponent
from ..standalone._clickable import _Clickable
from ..standalone._hoverable import _Hoverable
from ..standalone._static_text import _StaticText
from ..standalone._get_input import _GetInput
from ..standalone import *
from enum import Enum
from typing import Literal, Tuple, Optional

if typing.TYPE_CHECKING:
    from ...interface import Interface

_DefaultComponentTypes = Literal[
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


class _HandledComponent:
    def __init__(
        self,
        id: str,
        type: str,
        interface: str,
        grid_cell: Optional[int] = None,
        style: Optional[str | Tuple[str, ...]] = None,
        **kwargs,
    ) -> None:
        self.id = id
        self.type = type
        self.interface = interface
        self.grid_cell = grid_cell
        self.style_classes = tuple(style) if style is not None else None

        self.subtype: DefaultComponentTypes | _DefaultComponentTypes = (
            DefaultComponentTypes.COMPONENT
        )  # Should be set by custom components, to indicate which of the default component set type the custom component belong to (used for group handling)

    def __repr__(self) -> str:
        return f"<{self.type.capitalize()} component | id: {self.id} ; interface: {self.interface} ; subtype: {self.subtype} ; in ({len(self.groups())}) groups>"

    def after_load(self, interface: "Interface") -> None:
        """
        This method is called directly after the component's interface is loaded, and does nothing by default. This can be used to execute any logic that should be run after the interface and it's components are loaded.

        :param interface: The interface instance the component was loaded into.
        """

        pass


class _HandledClickable(_HandledComponent, _Clickable):
    def __init__(self, **kwargs) -> None:
        _HandledComponent.__init__(self, **kwargs)
        _Clickable.__init__(self, **kwargs)


class _HandledHoverable(_HandledComponent, _Hoverable):
    def __init__(self, **kwargs) -> None:
        _HandledComponent.__init__(self, **kwargs)
        _Hoverable.__init__(self, **kwargs)


class _HandledStaticText(_HandledComponent, _StaticText):
    def __init__(self, **kwargs) -> None:
        _HandledComponent.__init__(self, **kwargs)
        _StaticText.__init__(self, **kwargs)


class _HandledGetInput(_HandledComponent, _GetInput):
    def __init__(self, **kwargs) -> None:
        _HandledComponent.__init__(self, **kwargs)
        _GetInput.__init__(self, **kwargs)


class _Component(_HandledComponent, _StandaloneComponent):
    def __init__(self, **kwargs) -> None:
        _HandledComponent.__init__(self, **kwargs)
        _StandaloneComponent.__init__(self, **kwargs)


class _Animation(_HandledComponent, Animation):
    def __init__(self, **kwargs) -> None:
        _HandledComponent.__init__(self, **kwargs)
        Animation.__init__(self, **kwargs)


class _Button(_HandledComponent, Button):
    def __init__(self, **kwargs) -> None:
        _HandledComponent.__init__(self, **kwargs)
        Button.__init__(self, **kwargs)


class _Image(_HandledComponent, Image):
    def __init__(self, **kwargs) -> None:
        _HandledComponent.__init__(self, **kwargs)
        Image.__init__(self, **kwargs)


class _Input(_HandledComponent, Input):
    def __init__(self, **kwargs) -> None:
        _HandledComponent.__init__(self, **kwargs)
        Input.__init__(self, **kwargs)


class _Paragraph(_HandledComponent, Paragraph):
    def __init__(self, **kwargs) -> None:
        _HandledComponent.__init__(self, **kwargs)
        Paragraph.__init__(self, **kwargs)


class _SpritesheetAnimation(_HandledComponent, SpritesheetAnimation):
    def __init__(self, **kwargs) -> None:
        _HandledComponent.__init__(self, **kwargs)
        SpritesheetAnimation.__init__(self, **kwargs)


class _TextButton(_HandledComponent, TextButton):
    def __init__(self, **kwargs) -> None:
        _HandledComponent.__init__(self, **kwargs)
        TextButton.__init__(self, **kwargs)


class _Text(_HandledComponent, Text):
    def __init__(self, **kwargs) -> None:
        _HandledComponent.__init__(self, **kwargs)
        Text.__init__(self, **kwargs)
