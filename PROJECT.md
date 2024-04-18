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
- **FR12: Interface focus:** The library must allow that a single interface be focused.

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
- **NFR13: Serialization:** The library must allow serialization of it's state through pickle.

# Components

The library should have a set of default components, all of which must inherit from the base `Component` class.
There should also be utilities to make the use of the library easier. Notice that that library strongly rely on pygame sprite groups to render and update the components. It's totally possible to render and update them separately, without groups, but it's not advisable.<br>
Remember that the components are center aligned by default in the library, instead of the top-left pygame alignment.

The base components offered by the library are listed below:

```py
"""
Consider that the classes will have all the atributes and methods from their parents, plus their own.
"""

# All components must inherit from this class
class Component(pygame.sprite.Sprite):
    id: str,
    type: str,
    interface: str,
    x: int,
    y: int,
    width: int? = None,
    height: int? = None,
    grid_cell: int? = None,
    style: str? = None

    # Does nothing by default, should be overwritten with image preloading logic, if needed.
    def preload_image() -> None

    @override
    def update() -> None


# This component simply displays text
class Text(Component):
    text: str = "",
    font: str?,
    font_size: int? = 18,
    font_color: str? = "#000000",
    bold: bool? = False,
    italic: bool? = False,
    antialias: bool? = True,


# Display multiple lines of text
class Paragraph(Text):
    lines: List[str], # list of texts that compose each line of the paragraph
    line_height: int?


# Clickable components should all inherit from this class.
class Clickable(Component):
    action: Callable?,
    enabled: bool? = True

    def handle_click(mouse_pos: Tuple[int, int]) -> None


# Hoverable components should all inherit from this class
class Hoverable(Component):
    def handle_hover(mouse_pos: Tuple[int, int]) -> None


# If a background image is provided, the width and height atributes are not needed, and the size of the image will be used instead.
class Button(Clickable, Text, Hoverable):
    bg_image: str?,
    bg_color: str?,
    bg_alpha: int?,
    bg_focus_color: str?,
    border_radius: int?


# This component differs from a simple Button in that it's size will adjust to the size of the text, be a width and height not provided.
class TextButton(Clickable, Text, Hoverable):
    focus_color: str?


# This component allows for user input
class Input(Text, Hoverable):
    active: bool = False,
    bg_color: str?,
    bg_focus_color: str?,
    border_focus_color: str?,
    border_radius: int?,
    max_length: int?,
    hint: str?

    def handle_input(pressed_key: str) -> None


# This component displays a static image. If width and height are not provided, the image's size will be used instead.
class Image(Component):
    path: str


# This component displays images in sequence
class Animation(Component):
    delay: int,
    images: Tuple[str], # the paths to each image composing the animation
    colorkey: str?

# This component displays images loaded from a spritesheet in sequence
class SpritesheetAnimation(Animation):
    spritesheet: str,
    sprite_width: int,
    sprite_height: int

```

The `Component` class also defines a `subtype` atribute as None by default. This atribute should be set by custom components, to indicate which of the default component set types the custom component belongs to. The `subtype` is used for group handling at parsing.
Also, the following utilities are avaiable:

```py
# Classes that rely on text rendering will store their font information in an instance of this class. Mainly for use in the Text component.
class Font:
    font: str,
    font_size: int,
    font_color: str,
    bold: bool,
    italic: bool,

    def render(text: str) -> pygame.surface.Surface
```

And the following groups:

```py

# Semantic wrapper for the pygame GroupSingle
FocusGroup = pygame.sprite.GroupSingle

# Semantic wrapper for the pygame Group. Overrites drawing and updating to allow doing these operations for specific interfaces.
class ComponentGroup(pygame.sprite.Group):
    # Updates the components in the group. If '*interfaces' are provided, updates only the components present in the specified interfaces.
    def update(interfaces: Tuple[str]? = None) -> None
    # Draws the components in the group. If '*interfaces' are provided, draws only the components present in the specified interfaces.
    def draw(surface: pygame.surface.Surface, interfaces: Tuple[str]? = None) -> None


# Specialized group for handling Clickable components
class ClickableGroup(ComponentGroup):
    # Emits an activation for all the Clickable components in the group. If 'interfaces' is provided, activate only the Clickable components in the specified interfaces
    def handle_click(interfaces: Tuple[str]? = None) -> None


# Specialized group for handling Hoverable components
class HoverableGroup(ComponentGroup):
    # Calls handle_hover for each Hoverable component in the group. If 'interfaces' is provided, handle hover only for the Hoverable components in the specified interfaces
    def handle_hover(interfaces: Tuple[str]? = None) -> None


# Specialized group for handling buttons
class ButtonGroup(ClickableGroup, HoverableGroup):
    pass
```

# Interface handling (1.0 New proposal)

This proposal aims to enhance and simplify what's been defined in the first proposal, including, but not limited to the following:

- New Interface class to store interface related information
- Each interface creates it's own Surface
- Each interface allows for the creation of reusable style classes
- PyInterfacer receives the "display" (screen to render to) as an attribute, instead of width and height, and use it to render

```py
# This class handles all the interfaces
class PyInterfacer:
    _display: pygame.Surface # Where to render everything
    _overlay: OverlayManager # Controls the global overlay surface
    _current_focus: Interface? # Controls the current focused interface


    INTERFACES: Dict[str, Interface] # Stores all the interfaces, by their name
    COMPONENTS: Dict[str, Component] # Stores all the components, by their id

    # Stores all the key bindings. Each key represents a pygame key constant.
    _KEY_BINDINGS: Dict[int, Callable] = {}
    _KEYUP_BINDINGS: Dict[int, Callable] = {}

    _COMPONENT_CONVERSION_TABLE: Dict[str, Component] # maps a type (key) to a component class (value). Used to handle conversion from YAML atributes to component instances
    _GROUP_CONVERSION_TABLE: Dict[str, ComponentGroup] # Maps a component type (key) to a component group. Used to handle the creation of specific groups for some component types

    # Maps a component id (key) to an action callback (value). Used to map actions easily for Clickable components
    _COMPONENT_ACTION_MAPPING: Dict[str, Callable] = {}

    # Configures the display to render to (by default, pygame.display.get_surface())
    def set_display(display: pygame.Surface) -> None

    # Loads all the interface files in a directory
    def load_all(path: str) -> None
    # Loads a single interface from a file
    def load(file: str) -> None
    # Unloads all interfaces. Should not be called while still updating or rendering any interface.
    def unload() -> None

    # Adds new, custom components to be used in the interface. If 'type_' is the type of an existing component, it will be overridden. The parameter 'components' is a dictionary of 'component types : component classes'
    def add_custom_components(components: Dict[str, Component]) -> None
    # Adds new, custom component groups for the specified component types. This allows control over what type of group will be created for default and custom components. The paramenter 'groups' is a dictionary of 'component types : component groups'
    def add_custom_groups(groups: Dict[str, ComponentGroup]) -> None

    # Retrieves a component instance by it's ID. If 'interface' is provided, the search will look directly under the interface scope.
    def get_by_id(id_: str, interface: str? = None) -> Component?

    # Updates the currently focused interface
    def update() -> None
    # Draws the currently focused interface.
    def draw() -> None
    # Updates, draws and handles hover in the currently focused interface
    def handle() -> None

    # Changes the focus to the specified interface
    def change_focus(interface: str) -> None
    # Returns the currently focused interface
    def get_focused() -> Interface
    # Returns the instance of the provided `interface`, if found, otherwise None.
    def get_interface(interface: str) -> Interface?

    # Emits a call to handle a click for the Clickable components in the currently focused interface.
    def emit_click(cls) -> None
    # Emits a call to handle an input for the Input components in the currently focused interface.
    def emit_input(cls, event)
    # Handles hover events for all of the Hoverable components in the currently focused interface.
    def handle_hover(cls) -> None

    # Binds a component's attribute to another component's attribute
    @overload
    def bind(cls, c1: str, a1: str, c2: str, a2: str) -> None
    # Binds a component's attribute to a callback return value (the callback receives the attribute value as a parameter).
    @overload
    def bind(cls, c1: str, a1: str, callback: Callable) -> None

    # Maps actions to components, using their id
    def map_actions(cls, actions: Dict[str, Callable]) -> None

    # Adds a single surface to be rendered into the overlay
    @overload
    def add_to_overlay(cls, source: pygame.Surface, dest: pygame.Rect | Tuple[int, int]) -> None
    # Adds many surfaces to be rendered into the overlay
    @overload
    def add_to_overlay(cls, blit_sequence: Tuple) -> None
    # Clears the overlay surface
    def clear_overlay(cls) -> None
    # Restores the last overlay surface
    def restore_overlay(cls) -> None
    # Sets the overlay surface opacity
    def set_overlay_opacity(cls, o: int) -> None
    # Returns the current overlay opacity
    def get_overlay_opacity(cls) -> int

    # Handles pygame events
    def handle_event(cls, event: pygame.Event) -> None

    # Binds a keypress to a callback
    def bind_keys(cls, b: Dict[int, Dict[Literal["release", "press"], Callable]]) -> None

# This class handles a single interface
class Interface:
    COMPONENT_CONVERSION_TABLE: Dict[str, Component]
    GROUP_COMPONENT_TABLE: Dict[str, ComponentGroup]

    name: str
    display: "default" | "grid"
    rows: int?
    columns: int?
    width: int?
    height: int?

    surface: pygame.Surface
    _group: pygame.sprite.Group
    _type_groups: Dict[str, ComponentGroup] # Groups components (values) by type (keys)
    _components: List[Component]
    _style_classes: Dict[str, Dict] # Maps a style class (key) to it's information (value)
    _bindings: List[_ComponentBinding]

    # Updates the interface
    def update() -> None
    # Renders the interface
    def draw(surface: pygame.Surface) -> None
    # Renders and updates the interface to the display
    def handle(surface: pygame.Surface) -> None

    # Sets the interface background
    def set_background(self, bg: str) -> None

    # Returns a dictionary containg the components of the interface, grouped by their 'id'
    def component_dict() -> Dict[str, Component]

    # Emits a call to handle a click for the Clickable components in the interface.
    def emit_click(cls) -> None
    # Emits a call to handle an input for the Input components in the interface.
    def emit_input(cls, event)
    # Handles hover events for all of the Hoverable components in the interface.
    def handle_hover(cls) -> None

    # Sets the mappings for component conversion from YAML description
    def set_conversion_tables(component: Dict[str, Component]?, group: Dict[str, Component]?) -> None

    # Adds a subgroup to the interface. Subgroups are updated alongside the interface group, and rendered into the interface surface.
    def add_subgroup(self, group: pygame.sprite.Group) -> None

    # Binds a component's attribute to another component's attribute.
    @overload
    def create_binding(self, c1: Component, a1: str, c2: Component, a2: str) -> None
    # Binds a component's attribute to a callback
    @overload
    def create_binding(self, c1: Component, a1: str, callback: Callable) -> None

    # Adds a single surface to be rendered into the interface's overlay or underlayer
    @overload
    def add_to_layer(self, source: pygame.Surface, dest: pygame.Rect | Tuple[int, int], *, layer: RenderLayer) -> None
    # Renders many surfaces to be rendered into the interface's overlay or underlayer
    @overload
    def add_to_layer(self, blit_sequence: Tuple[Tuple, ...], *, layer: RenderLayer) -> None
    # Clears the interface's overlay or underlayer surface
    def clear_layer(self, layer: RenderLayer) -> None
    # Sets the opacity of the interface's overlay or underlayer
    def set_layer_opacity(self, o: int, layer: RenderLayer) -> None
    # Returns the opacity of the interface's overlay and underlayer
    def get_layer_opacity(self, layer: RenderLayer) -> int
    # Restores the interfac's overlay or underlayer last surface
    def restore_layer(self, layer: RenderLayer) -> None
```

# Interface handling (First Proposal)

The interfaces must be handled by a single class. It's definition is described below:

```py
# This class handles all the interfaces.
class PyInterfacer:
    # The size of the screen
    WIDTH: int?
    HEIGHT: int?

    STATS: Counter # Keeps track of how many interfaces and components of each type are loaded
    _current_focus: str # Controls the current focused interface
    GROUPS: Dict[str, ComponentGroup] # store all the groups (general group, component types groups, interface groups)
    COMPONENTS: Dict[str, List[Component]] # store all the components, grouped by their interfaces
    _COMPONENT_CONVERSION_TABLE: Dict[str, Component] # maps a type (key) to a component class (value). Used to handle conversion from YAML atributes to component instances
    _GROUP_CONVERSION_TABLE: Dict[str, ComponentGroup] # Maps a component type (key) to a component group. Used to handle the creation of specific groups for some component types

    # Loads all the interface files in a directory
    def load_all(path: str) -> None
    # Loads a single interface from a file
    def load_interface(file: str) -> None
    # Unloads all interfaces. Should not be called while still updating or rendering any interface.
    def unload() -> None

    # Adds new, custom components to be used in the interface. If 'type_' is the type of an existing component, it will be overridden. The parameter 'components' is a dictionary of 'component types : component classes'
    def add_custom_components(components: Dict[str, Component]) -> None
    # Adds new, custom component groups for the specified component types. This allows control over what type of group will be created for default and custom components. The paramenter 'groups' is a dictionary of 'component types : component groups'
    def add_custom_groups(groups: Dict[str, ComponentGroup]) -> None

    # Retrieves a component instance by it's ID. If 'interface' is provided, the search will look directly under the interface scope.
    def get_by_id(id_: str, interface: str? = None) -> Component?
    # Retrieves all the components in an interface
    def get_by_interface(interface: str) -> Tuple[Component]?
    # Retrieves all the components for a type. If 'interface' is provided, the search will look directly under the interface scope.
    def get_by_type(type_: str, interface: str? = None) -> Tuple[Component]?

    # Updates all the loaded interfaces. If '*interfaces' are provided, update only the specified interfaces.
    def update(*interfaces: str) -> None
    # Draw all the loaded interfaces. If '*interfaces' are provided, draw only the specified interfaces.
    def draw(surface: pygame.surface.Surface, *interfaces: str) -> None

    # Changes the focus to the specified interface
    def change_focus(interface: str) -> None
    # Returns the currently focused interface name
    def get_focused() -> str
    # Updates only the currently focused interface
    def update_focused() -> None
    # Draws only the currently focused interface
    def draw_focused(surface: pygame.surface.Surface) -> None

    # Emits a call to handle a click for the Clickable components. If '*interfaces' are provided, limit the event to the specified interfaces.
    def emit_click(cls, *interfaces: Tuple[str, ...]) -> None
    # Handles hover events for all of the Hoverable components. If '*interfaces' are provided, limit the handling to the specified interfaces.
    def handle_hover(cls, *interfaces: Tuple[str, ...]) -> None
    # Emits an input event for the Input components. If '*interfaces' are provided, limit the event to the specified interfaces.
    def emit_input(cls, event, *interfaces: Tuple[str, ...]) -> None

    # Update and render all the components in the currently focused interface.
    def just_work(cls, surface: pygame.Surface) -> None
```

# Interface files

Each interface must be represented by a single YAML file. The file structure should be defined as below:

```yaml
interface: interface-name
background: color-or-image # optional, default to 'black'
display: display-type
rows: rows-amount-if-grid
columns: columns-amount-if-grid
styles: # styles are optional
    - name: style-class-name
      attribute: value
components:
    - type: component-type
      atribute: value

    - type: component-type
      atribute: value

    ...
```

Each component and it's atributes must be listed under `components`. Invalid atributes are ignored during conversion. For `width`, `height`, `x` and `y` atributes, percentage values are accepted and will be converted at parsing. For that to work, `PyInterface.WIDTH` and `PyInterfacer.HEIGHT` must be set.

# Modularity

Every component should inherit from `Component`. To allow for better group handling, each custom component should define the `self.subtype` atribute to the type of one of the default components. If not defined, the component will be placed in a simple `ComponentGroup`. The default component types should be made avaiable from the enum `DefaultComponentTypes`.

# Interface display types

A display type of `default` or `grid` can be specified to each interface. For interfaces of display type `grid`, `rows` and `columns` attributes must also be specified. If a interface is of display type `default`, it's components should be positioned simply by providing `x` and `y` attributes; if it's display type is `grid`, each component can also be positioned by default `x` and `y` attributes, but the atribute `grid_cell` can be specified to the number of a specific cell in the grid, in which the component will be positioned at the center. Components with the `grid_cell` attribute will have their `x` and `y` attributes ignored.

If `width` and `height` attributes are specified as percentage values to components in a grid cell, the component's size will be calculated relative to the grid cell size, instead of the window size, otherwise, if `width` and `height` are not specified, the component will fill it's grid cell; `width` and `height` can also be specified as `auto` for the components in a grid_cell, which will make the component use it's default sizing behavior (for example, using the size of it's internal text, for a `TextButton`, or just completely disappearing for a `Button`).
