# PyInterfacer

A modular library for handling interfaces in pygame projects.

Build menus and interfaces for pygame projects using simple YAML descriptions and a base set of components.
Are the base components not enough? Expand on them and create your own!

# Pygame interfaces using YAML descriptions

Building interfaces for pygame projects can be tiring and cumbersome. PyInterfacer removes the tiring and cumbersome part of directly creating the interfaces and all of their components like buttons, text, inputs and whatever more by allowing all of those to be represented by simple YAML files. An interface is described in the following way:

```yaml
interface: <interface name>
background: <color | path to image>
display: <default | grid | overlay>
styles: <optional list of style classes>
components: <list of components>
```

Where:

- `interface` is the name of the interface;
- `background` is an optional attribute that can be either a string representing a color or a path to an image. If it's an image, it gets resized to the display size. Defaults to transparent;
- `display` is the interface's display type. One of 'grid', 'default' or 'overlay';
- `styles` is a list of style classes, where the attributes can be any accepted by the components. Defined as below:

```yaml
styles:
  - name: <style class name>
    attribute: value
```

- `components` is a list of components.

# Default components and modularity

PyInterfacer comes with a default set of components, including Text, Buttons, Input, Animations and Static Images, all of which you can use by simply specifying a few atributes. Here's an example:

```yaml
interface: example-interface
background: white
display: default
components:
  - type: text
    id: txt-1
    text: "Hello, world!"
    x: 50%
    y: 100

 - type: text
   id: txt-2
   text: "Look at that, a fellow component"
   x: 50%
   y: 150
```

Knowing that just having some buttons and texts all over your display is not enough when building a complete interface for your project, PyInterfacer let's you create your own custom components!

The rules are quite simple:

- Every component must inherit from the base `Component` class.
- Every custom component should set it's `subtype` attribute value to one of the types of the default components.

Here's an example of a custom component:

```py
from pyinterfacer.components import Text

class HelloWorld(Text):
    """A component that only displays Hello world."""
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.text = "Hello, world"
        self.subtype = "text"
```

In this example, our incredible `HelloWorld` component inherits from `Component` through `Text`, and specializes in displaying 'Hello, world'. By doing simply that, your custom component has access to all `Text`'s attributes, plus any it defines in it's constructor.<br>

To use this component in our project, we load it into PyInterfacer, before loading any interface file that might use it:

```py
from custom_components import HelloWorld
from pyinterfacer import PyInterfacer

PyInterfacer.add_custom_components({ "hello": HelloWorld })
```

Our `HelloWorld` component could then be referenced in the interface's YAML file as follows:

```yaml
interface: example-interface
background: white
display: default
components:
  - type: hello
    id: hello-1
    x: 50%
    y: 50%
    font_size: 64
    font_color: red
```

## Component groups

PyInterfacer relies heavily on pygame sprite groups for handling, rendering and updating all the loaded components effectively. Some utility groups come by default, to help building your interfaces. For example: `Button`'s are added by default on `ButtonGroup`s, which themselves inherit from `ClickableGroup`s and `HoverableGroup`s, allowing handling of clicks and hover events with ease.

Each interface stores it's components in a generic group, and each component is also stored in a group by their type.

Custom component groups can also be added. Let's consider our previous `HelloWorld` component. Suppose we want it in a new, custom group, for whatever reason. The first thing you should know is: just as components should inherit from `Component`, custom component groups should inherit from `ComponentGroup`. So our group can be made as follows:

```py
from pyinterfacer.groups import ComponentGroup

class HelloWorldGroup(ComponentGroup):
    pass
```

This group can then be loaded into PyInterfacer:

```py
from custom_components import HelloWorld
from custom_groups import HelloWorldGroup
from pyinterfacer import PyInterfacer

PyInterfacer.add_custom_components({ "hello": HelloWorld })
PyInterfacer.add_custom_groups({ "hello": HelloWorldGroup })
```

This means you can use any custom methods from our custom group, as the groups are stored per component type:

```py
interface = PyInterfacer.get_interface("example-interface")
hello_group = interface.get_type_group("hello")
while running:
    <pygame events>

    hello_group.do_some_magic()

    <pygame updates and drawing>
```

# Display types

PyInterfacer allows for three display types to be set by interface: `default`, `grid` and `overlay`.<br>

## Default

An interface with display type of `default` means that all it's component are positioned by `x` and `y` values (which can be either absolute pixel values, or percentages). This is what you saw in the examples before:

```yaml
interface: example-interface
background: white
display: default
components: ...
```

## Grid

An interface with display type of `grid` requires two new atributes: `rows` and `columns`. It means that the components on the interface can be positioned in a grid of `rows x columns`. To do so, the attribute `grid_cell` can be specified to any avaiable cell in the grid. For example: suppose a grid of 3 x 3. There are 9 possible cells, so we can specify `grid_cell` as any value from 0 through 8. If `grid_cell` is specified, `x` and `y` are ignored.

Components in a grid displayed interface use the full size of their grid cells by default, if `width` and `height` are not specified. If percentage values are specified, they are computed relative to the grid cell size, instead of the display size. The value of `width` and `height` can also be specified as `auto` for default component based sizing behavior.<br>
In grid displays, components can also be positioned just like in default displays, by not providing `grid_cell`, and specifying `x` and `y`.<br>
Below, an example:

```yaml
interface: example-interface
background: white
display: grid
rows: 3
columns: 3
components:
  - type: text
    id: txt-1
    text: "Hello, world!"
    height: auto
    grid_cell: 4

 - type: text
   id: txt-2
   text: "Look at that, a fellow component"
   x: 50%
   y: 150

 - type: image
   id: img-1
   path: "path/to/image"
   grid_cell: 0
   height: 80%
   width: auto
```

## Overlay

An interface with display type `overlay` works just like an interface with display type `default`, but it is rendered into the global overlay, meaning it will always be rendered.

# Style classes

When representing interfaces through the YAML declarations, you may find it it's quite a repetitive task: lot's of components share the same attributes, like font information, color information, _etc_.

To solve that, PyInterfacer allows you to define style classes, that can be used in individual components:

```yaml
interface: example-interface
background: white
display: grid
rows: 3
columns: 3
styles:
  - name: txt-style
    font: Arial
    font_size: 56
    font_color: red

  - name: x-centered
    x: 50%
components:
  - type: text
    id: txt-1
    style: txt-style
    text: "Hello, world!"
    font_size: 128
    grid_cell: 4

 - type: text
   id: txt-2
   style: [x-centered, txt-style]
   text: "Look at that, a fellow component"
   y: 150
```

By doing that, our `txt-1` and `txt-2` Text components will use the font information from the `txt-style` style class. Notice that `txt-1` overwrites the `font_size` attribute, and will use 128 for it's font size, instead of 56.

Each component can define a single style class, or a list of style classes. If a list is provided, the first style class on the list will have the highest priority.

# Overlays

May you need to render anything other than components at the display, PyInterfacer allows to do so through overlays. PyInterfacer has a global overlay, allowing you to render anything above every interface. All you need to do is to add render targets to the overlay:

```py
PyInterfacer.add_to_overlay(surface, destination) # to add a single Surface
PyInterfacer.add_to_overlay(((surface, destination), ...)) # to add multiple Surfaces
```

You can also clear the overlay, restore the last overlay render targets, and set the overlay opacity, if needed:

```py
PyInterfacer.clear_overlay()
PyInterfacer.restore_overlay()
PyInterfacer.set_overlay_opacity(integer-from-1-to-255)
```

If you want a better control over what is rendered into each interface, you can also add render targets to overlays in each interface:

```py
i = PyInterfacer.get_interface("interface-name")
if i is not None:
  i.add_to_layer(surface, destionation, layer=RenderLayer.OVERLAY)
  i.add_to_layer(((surface, destination), ...), layer=RenderLayer.OVERLAY)
```

The methods to clear, restore and set opacity to the overlay also apply for interface overlays.

# Underlayers

Some times you many need to render something under the components, and above the background, like a game map, for example. For that, you can set render targets for the underlayer of each interface. Underlayers work exactly the same as overlays:

```py
i = PyInterfacer.get_interface("interface-name")
if i is not None:
  i.add_to_layer(surface, destionation, layer=RenderLayer.UNDERLAYER)
  i.add_to_layer(((surface, destination), ...), layer=RenderLayer.UNDERLAYER)
```

# Components and attributes

Below is a list of the components avaiable in the default component set, and the attributes they can accept:

```py
Component:
  id: str # components with id equals to '_' are handled, but not added to the global component mapping.
  type: str
  interface: str
  x: int
  y: int
  width: int?
  height: int?
  grid_cell: int?
  style: str?
  alignment: "center" | "topleft" | "topright" | "midleft" | "midright" | "bottomleft" | "bottomright" # defaults to 'center', controls where (x, y) will be on the component's rect

Text:
  id: str
  type: str
  interface: str
  x: int
  y: int
  width: int?
  height: int?
  grid_cell: int?
  style: str?
  text: str
  font: str?
  font_size: int?
  font_color: str?
  bold: bool?
  italic: bool?
  antialias: bool?
  alignment: "center" | "topleft" | "topright" | "midleft" | "midright" | "bottomleft" | "bottomright"

Paragraph:
  id: str
  type: str
  interface: str
  x: int
  y: int
  width: int?
  height: int?
  grid_cell: int?
  style: str?
  text: str # this attribute will not be used by the paragraph component
  font: str?
  font_size: int?
  font_color: str?
  bold: bool?
  italic: bool?
  antialias: bool?
  lines: List[str] # each string on the list will be rendered in a line
  line_height: int?

Clickable:
  id: str
  type: str
  interface: str
  x: int
  y: int
  width: int?
  height: int?
  grid_cell: int?
  style: str?
  action: Callable? # this should not be set at the YAML declaration
  enabled: bool?
  alignment: "center" | "topleft" | "topright" | "midleft" | "midright" | "bottomleft" | "bottomright"

Hoverable:
  id: str
  type: str
  interface: str
  x: int
  y: int
  width: int?
  height: int?
  grid_cell: int?
  style: str?
  alignment: "center" | "topleft" | "topright" | "midleft" | "midright" | "bottomleft" | "bottomright"

Button:
  id: str
  type: str
  interface: str
  x: int
  y: int
  width: int?
  height: int?
  grid_cell: int?
  style: str?
  text: str
  font: str?
  font_size: int?
  font_color: str?
  bold: bool?
  italic: bool?
  antialias: bool?
  action: Callable? # this should not be set at the YAML declaration
  enabled: bool?
  alignment: "center" | "topleft" | "topright" | "midleft" | "midright" | "bottomleft" | "bottomright"

TextButton:
  id: str
  type: str
  interface: str
  x: int
  y: int
  width: int?
  height: int?
  grid_cell: int?
  style: str?
  text: str
  font: str?
  font_size: int?
  font_color: str?
  bold: bool?
  italic: bool?
  antialias: bool?
  action: Callable? # this should not be set at the YAML declaration
  enabled: bool?
  focus_color: str?
  alignment: "center" | "topleft" | "topright" | "midleft" | "midright" | "bottomleft" | "bottomright"

Input:
  id: str
  type: str
  interface: str
  x: int
  y: int
  width: int?
  height: int?
  grid_cell: int?
  style: str?
  text: str
  font: str?
  font_size: int?
  font_color: str?
  bold: bool?
  italic: bool?
  antialias: bool?
  active: bool = False
  bg_color: str?
  bg_focus_color: str?
  border_focus_color: str?
  border_radius: int?
  max_length: int?
  hint: str?
  alignment: "center" | "topleft" | "topright" | "midleft" | "midright" | "bottomleft" | "bottomright"

Image:
  id: str
  type: str
  interface: str
  x: int
  y: int
  width: int?
  height: int?
  grid_cell: int?
  style: str?
  path: str
  alignment: "center" | "topleft" | "topright" | "midleft" | "midright" | "bottomleft" | "bottomright"

Animation:
  id: str
  type: str
  interface: str
  x: int
  y: int
  width: int?
  height: int?
  grid_cell: int?
  style: str?
  delay: int
  images: Tuple[str] # paths to each sprite
  colorkey: str?
  alignment: "center" | "topleft" | "topright" | "midleft" | "midright" | "bottomleft" | "bottomright"

SpritesheetAnimation:
  id: str
  type: str
  interface: str
  x: int
  y: int
  width: int?
  height: int?
  grid_cell: int?
  style: str?
  delay: int
  images: Tuple[str] # this is automatically set based on the spritesheet, don't use it for this component
  colorkey: str?
  spritesheet: str
  sprite_width: int,
  sprite_height: int
  alignment: "center" | "topleft" | "topright" | "midleft" | "midright" | "bottomleft" | "bottomright"
```

## Bindings

Some times you may need some component's attribute value to be the same as another component's attribute value, and the changes in the first component's attribute value to be reflected in the second component's attribute value. For example: we have a Player component, with an `hp` attribute, and Text component, with it's `text` attribute; we want the Text component to display the player's current HP, dynamically; instead of manually updating the Text component `text` value to be the same as the Player's component `hp` value, we can bind them both, and let PyInterfacer take care of that.

Here's our example in code:

```py
import pygame
from pyinterfacer import PyInterfacer

pygame.init()

display = pygame.display.set_mode(size, flags, depth)

PyInterfacer.load("interface.yaml")

# Consider 'interface.yaml' to have components with id 'player' and 'player-hp-txt'
# We them bind the 'player' component 'hp' attribute value to the 'player-hp-txt' component 'text' attribute value. Now any changes on the player 'hp' value will be updated in the player hp text as well.
PyInterfacer.bind("player", "hp", "player-hp-txt", "text")

<handle game loop>
```

You can also bind a component's attribute value to a callback, instead of another component. The callback will receive the attribute's value, and should return it's updated value. For example:

```py
import pygame
from pyinterfacer import PyInterfacer

pygame.init()

display = pygame.display.set_mode(size, flags, depth)
clock = pygame.time.Clock()

PyInterfacer.load("interface.yaml")

def bind_fps(v):
  return f"FPS: {int(clock.get_fps())}

PyInterfacer.bind("fps-txt", "text", bind_fps)

<handle game loop>
```

# Examples

More examples can be found at [examples/](./examples/).

Below, an example project:

```py
import pygame
from pyinterfacer import PyInterfacer

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
FPS = 120

# set display for rendering (defaults to the display initialized by pygame.screen.set_mode if not set)
PyInterfacer.set_display(screen)

PyInterfacer.load("example-interface.yaml")
PyInterfacer.change_focus("example-interface")

running = True
while running:
    screen.fill("white")

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                # handles clicks on Clickable components
                PyInterfacer.emit_click()
        elif event.type == pygame.KEYDOWN:
            # handles input to any Input component
            PyInterfacer.emit_input(event)

    # update should come before draw, as most components set their image and rect at the update method
    PyInterfacer.update()
    PyInterfacer.draw()
    PyInterfacer.handle_hover()

    pygame.display.flip()
    clock.tick(FPS)
```

An example with button interactions:

```py
import pygame
from pyinterfacer import PyInterfacer

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
FPS = 120

PyInterfacer.load_all("interfaces/")

# gets a reference to the button components
gotomenu_btn = PyInterfacer.get_by_id("gotomenu_btn")
gotomain_btn = PyInterfacer.get_by_id("gotomain_btn")
exit_btn = PyInterfacer.get_by_id("exit_btn")

# verifies if they are loaded and set their action
if gotomenu_btn:
  gotomenu_btn.action = lambda: PyInterfacer.change_focus("menu-interface")
if gotomain_btn:
  gotomain_btn.action = lambda: PyInterfacer.change_focus("main-interface")
if exit_btn:
  exit_btn.action = exit

# set the current focus
PyInterfacer.change_focus("main-interface")

running = True
while running:
  screen.fill("white")

  for event in pygame.event.get():
    if event.type == pygame.QUIT:
      running = False
    elif event.type == pygame.MOUSEBUTTONDOWN:
      if event.button == 1:
        # emit a click event in the currently focused interface
        PyInterfacer.emit_click(PyInterfacer.get_focused())

  # updates, renders and handles hover in the currently focused interface
  PyInterfacer.handle()

  pygame.display.flip()
  clock.tick(FPS)

pygame.quit()
```
