# PyInterfacer

A modular library for handling interfaces in pygame projects.

Build menus and interfaces for pygame projects using simple YAML descriptions and a base set of components.
Are the base components not enough? Expand on them and create your own!

# Pygame interfaces using YAML descriptions

Building interfaces for pygame projects can be tiring and cumbersome. PyInterfacer removes the tiring and cumbersome part of directly creating the interfaces and all of their components like buttons, text, inputs and whatever more by allowing all of those to be represented by simple YAML files. An interface is described in the following way:

```yaml
interface: <interface name>
display: <default | grid>
components: <list of components>
```

# Default components and modularity

PyInterfacer comes with a default set of components, including Text, Buttons, Input, Animations and Static Images, all of which you can use by simply specifying a few atributes. Here's an example:

```yaml
interface: example-interface
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

PyInterfacer saves all the loaded components in a `generic` group, specific groups for all `interfaces` and even more specific groups for all `types` of components. All of which can be found at `PyInterfacer.GROUPS` dictionary.

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
while running:
    <pygame events>

    PyInterfacer.GROUPS["types"]["hello"].do_some_magic()

    <pygame updates and drawing>
```

# Display types

PyInterfacer allows for two display types to be set by interface: `default` and `grid`.<br>

## Default

An interface with display type of `default` means that all it's component are positioned by `x` and `y` values (which can be either absolute pixel values, or percentages). This is what you saw in the examples before:

```yaml
interface: example-interface
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

# Components and attributes

Below is a list of the components avaiable in the default component set, and the attributes they can accept:

```py
Component:
  id: str
  type: str
  interface: str
  x: int
  y: int
  width: int?
  height: int?
  grid_cell: int?

Text:
  id: str
  type: str
  interface: str
  x: int
  y: int
  width: int?
  height: int?
  grid_cell: int?
  text: str
  font: str?
  font_size: int?
  font_color: str?
  bold: bool?
  italic: bool?
  antialias: bool?

Clickable:
  id: str
  type: str
  interface: str
  x: int
  y: int
  width: int?
  height: int?
  grid_cell: int?
  action: Callable? # this should not be set at the YAML declaration
  enabled: bool?

Hoverable:
  id: str
  type: str
  interface: str
  x: int
  y: int
  width: int?
  height: int?
  grid_cell: int?

Button:
  id: str
  type: str
  interface: str
  x: int
  y: int
  width: int?
  height: int?
  grid_cell: int?
  text: str
  font: str?
  font_size: int?
  font_color: str?
  bold: bool?
  italic: bool?
  antialias: bool?
  action: Callable? # this should not be set at the YAML declaration
  enabled: bool?

TextButton:
  id: str
  type: str
  interface: str
  x: int
  y: int
  width: int?
  height: int?
  grid_cell: int?
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

Input:
  id: str
  type: str
  interface: str
  x: int
  y: int
  width: int?
  height: int?
  grid_cell: int?
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

Image:
  id: str
  type: str
  interface: str
  x: int
  y: int
  width: int?
  height: int?
  grid_cell: int?
  path: str

Animation:
  id: str
  type: str
  interface: str
  x: int
  y: int
  width: int?
  height: int?
  grid_cell: int?
  delay: int
  images: Tuple[str] # paths to each sprite
  colorkey: str?

SpritesheetAnimation:
  id: str
  type: str
  interface: str
  x: int
  y: int
  width: int?
  height: int?
  grid_cell: int?
  delay: int
  images: Tuple[str] # this is automatically set based on the spritesheet, don't use it for this component
  colorkey: str?
  spritesheet: str
  sprite_width: int,
  sprite_height: int
```

# Examples

Below, an example project:

```py
import pygame
from pyinterfacer import PyInterfacer

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
FPS = 120

# set display size (used in computing percentage values)
PyInterfacer.set_size(WIDTH, HEIGHT)

PyInterfacer.load("example-interface.yaml")

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
    PyInterfacer.draw(screen)
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
gotomenu_btn = PyInterfacer.get_by_id("gotomenu_btn", "main-interface")
gotomain_btn = PyInterfacer.get_by_id("gotomain_btn", "menu-interface")
exit_btn = PyInterfacer.get_by_id("exit_btn", "menu-interface")

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
  PyInterfacer.just_work(screen)

  pygame.display.flip()
  clock.tick(FPS)

pygame.quit()
```
