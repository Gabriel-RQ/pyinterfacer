# PyInterfacer

Python library for building interfaces for pygame projects, using YAML files to represent said interfaces.

# Requirements

## Functional Requirements

- **FR01: Interface representation:** The interfaces must be representable by YAML files.
- **FR02: Interface loading:** The library must be able to parse and load the YAML interface files.
- **FR03: Component conversion:** Each component in the YAML interface file must be converted to it's corresponding class and instantiated.
- **FR04: Multiple interfaces:** The library must be able to load multiple interface files and store all the components.
- **FR05: Rendering and updates:** The library must be able to draw and update all it's components.
- **FR06: Interface rendering and updates:** The library must be able to draw and update components of a specific interface.
- **FR07: Component search by ID:** The library must be able to search components by their ID.
- **FR08: Component search by interface:** The library must be able to search components by their interface.
- **FR09: Component search by type:** The library must be able to search components by their type.
- **FR10: Default components:** The library must provide a set of default, extendable components.
- **FR11: Interface design:** The interfaces must represent a single screen, serving as a container to it's inner components.
- **FR12: Serialization:** The library must allow serialization of it's state through pickle.

## Nonfunctional Requirements

- **NFR01: Component storage:** The library must store all the components instances in a static dictionary, grouped by their interfaces.
- **NFR02: Component groups:** The library must add all the components to a static pygame group.
- **NFR03: Components groups by type:** The library must add all the components to a group specific for their type.
- **NFR04: Interface groups:** The library must add all the components to a group specific to their interface domain.
- **NFR05: Modularity:** The library must be modular, allowing user defined components to be created and used.
- **NFR06: Click events:** The library must be able to handle click events to it's clickable components.
- **NFR07: Hover events:** The library must be able to handle hover events to it's hoverable components.
- **NFR08: Stats:** The library must store the amount of components loaded, grouped by type.
- **NFR09: Component handling:** The library must allow changes to it's components atributes at runtime.
- **NFR10: Simplicity:** The library should be simple to use.
- **NFR11: Performance:** The library should prioritize performance.
- **NFR12: Compatibility:** The library should work consistently across different platforms where python and pygame are supported.

# Components

The library should have a set of default components, all of which must inherit from the base `Component` class.
There should also be utilities to make the use of the library easier. Notice that that library strongly rely on pygame sprite groups to render and update the components. It's totally possible to render and update them separately, without groups, but it's not advisable.<br>
Remember that the components are center aligned by default in the library, instead of the top-left pygame alignment.

The base components offered by the library are listed below:

```py
"""
Consider that the classes will have all the atributes and methods from their parents, plus their own.
Also consider that the atributes of each class below are the same used in the YAML interface file.
"""

# All components must inherit from this class
class Component(pygame.sprite.Sprite):
    id: int,
    type: str,
    interface: str,
    x: int,
    y: int,
    width: int? = None,
    height: int? = None,
    image: pygame.Surface,
    rect: pygame.Rect,
    groups: tuple[pygame.Group]? = None

    @override
    def update() -> None


class Text(Component):
    text: str,
    font: str,
    font_size: int,
    font_color: str,
    bold: bool,
    italic: bool,
    underline: bool,


# Clickable components should all inherit from this class.
class Clickable(Component):
    action: Callable?

    def handle_click(mouse_pos: Tuple[int, int]) -> None


# Hoverable components should all inherit from this class
class Hoverable(Component):
    def handle_hover(mouse_pos: Tuple[int, int]) -> None


# If a background image is provided, the width and height atributes are not needed, and the size of the image will be used instead.
class Button(Clickable, Text, Hoverable):
    bg_image: str,
    bg_color: str


# This component differs from a simple Button in that it's size will adjust to the size of the text, be a width and height not provided.
class TextButton(Clickable, Text, Hoverable):
    focus_color: str


# This component allows for user input
class Input(Component, Text, Hoverable):
    max_length: int,
    min_length: int,

    def handle_input(pressed_key: str) -> None


# This component displays a static image. If width and height are not provided, the image's size will be used instead.
class Image(Component):
    pass


# This component displays images in sequence
class Animation(Component):
    frames: int,
    delay: int,
    images: Tuple[str] # the paths to each image composing the animation
```

Also, the following utilities are avaiable:

```py
# Classes that rely on text rendering will store their font information in an instance of this class. Mainly for use in the Text component.
class Font:
    font: str,
    font_size: int,
    font_color: str,
    bold: bool,
    italic: bool,
    underline: bool

    def render(text: str) -> pygame.surface.Surface
```

And the following groups:

```py
# Semantic wrapper for the pygame Group. Overrites drawing and updating to allow doing these operations for specific interfaces.
class ComponentGroup(pygame.sprite.Group):
    # Updates the components in the group. If '*interfaces' are provided, updates only the components present in the specified interfaces.
    def update(*interfaces? = None) -> None
    # Draws the components in the group. If '*interfaces' are provided, draws only the components present in the specified interfaces.
    def draw(surface: pygame.surface.Surface, *interfaces? = None) -> None


# Specialized group for handling Clickable components
class ClickableGroup(ComponentGroup):
    # Emits an activation for all the Clickable components in the group. If 'interfaces' is provided, activate only the Clickable components in the specified interfaces
    def activate(interfaces: List[str]?) -> None


# Specialized group for handling Hoverable components
class HoverableGroup(ComponentGroup):
    # Calls handle_hover for each Hoverable component in the group. If 'interfaces' is provided, handle hover only for the Hoverable components in the specified interfaces
    def handle_hover(interfaces: List[str]?) -> None


# Specialized group for handling buttons
class ButtonGroup(ClickableGroup, HoverableGroup):
    pass
```

# Interface handling

The interfaces must be handled by a single class. It's definition is described below:

```py
# This class handles all the interfaces.
class PyInterfacer:
    STATS: Counter,
    COMPONENTS: Mapping[str, List[Component]], # store all the components, grouped by their interfaces
    GROUPS: Dict[str, ComponentGroup], # store all the groups (general group, component types groups, interface groups)
    _COMPONENT_CONVERSION_MAPPING: Dict[str, Component] # maps a type (key) to a component class (value). Used to handle conversion from YAML atributes to component instances

    # Loads all the interface files in a directory
    def load_all(path: str) -> None
    # Loads a single interface from a file
    def load_interface(file: str) -> None

    # Adds a custom component to be used in the interface. If 'type_' is the type of an existing component, it will be overriden.
    def add_custom_component(type_: str, class_: Component) -> None

    # Retrieves a component instance by it's ID. If 'interface' is provided, the search will look directly under the interface scope.
    def get_by_id(id_: str, interface: str? = None) -> Component
    # Retrieves all the components in an interface
    def get_by_interface(interface: str) -> Component
    # Retrieves all the components for a type. If 'interface' is provided, the search will look directly under the interface scope.
    def get_by_type(type_: str, interface: str? = None)

    # Updates all the loaded interfaces. If '*interfaces' are provided, update only the specified interfaces.
    def update(*interfaces: str) -> None
    # Draw all the loaded interfaces. If '*interfaces' are provided, draw only the specified interfaces.
    def draw(*interfaces: str) -> None
```
