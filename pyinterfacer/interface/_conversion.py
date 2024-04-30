from ..components.handled import (
    _Component,
    _Animation,
    _Button,
    _Image,
    _Input,
    _Paragraph,
    _SpritesheetAnimation,
    _TextButton,
    _Text,
)
from typing import Dict
from ..groups import *


class _ConversionMapping:
    """Defines mappings to convert PyInterfacer components and groups loaded from YAML interface files."""

    # Maps a component type (key) a component class (value). Used to handle conversion from YAML loaded components to their instances
    COMPONENT_CONVERSION_TABLE: Dict[str, _Component] = {
        "animation": _Animation,
        "button": _Button,
        "image": _Image,
        "input": _Input,
        "paragraph": _Paragraph,
        "spritesheet-animation": _SpritesheetAnimation,
        "text-button": _TextButton,
        "text": _Text,
    }
    # Maps a component type (key) to a component group. Used to handle the creation of specific groups for some component types. Component types not in this dictionary are added to a ComponentGroup by default
    GROUP_CONVERSION_TABLE: Dict[str, ComponentGroup] = {
        "clickable": ClickableGroup,
        "hoverable": HoverableGroup,
        "button": ButtonGroup,
        "text-button": ButtonGroup,
        "input": InputGroup,
    }

    @classmethod
    def extend_component_table(cls, components: Dict[str, _Component]) -> None:
        """
        Updates the component conversion table with new custom components.

        :param components: A dictionary where the `keys` represent the type of the component, and the `values` represent a reference to the component class.
        """

        cls.COMPONENT_CONVERSION_TABLE.update(components)

    @classmethod
    def extend_group_table(cls, groups: Dict[str, ComponentGroup]) -> None:
        """
        Updates the group conversion table with new custom groups.

        :param groups: A dictionary where the `keys` represent the type of the component, and the `values` represent a reference to the group class.
        """

        cls.GROUP_CONVERSION_TABLE.update(groups)

    @classmethod
    def convert_component(cls, type_: str, interface: str, **data) -> _Component:
        """
        Converts data loaded from an YAML interface declaration to a component instance.

        :param type_: Component type.
        :param interface: Interface name.
        :param **data: Component data.
        """

        c = cls.COMPONENT_CONVERSION_TABLE.get(type_)

        if c is not None:
            return c(**data, interface=interface)
