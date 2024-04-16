import pygame
from pyinterfacer import PyInterfacer

pygame.init()

display_sizes = pygame.display.list_modes()
display = pygame.display.set_mode(display_sizes[len(display_sizes) // 2], pygame.SCALED)
clock = pygame.time.Clock()
FPS = 120

# Loads the interface and focus in the initial screen
PyInterfacer.load_all("interfaces/")
PyInterfacer.change_focus("menu")

counter = 0


# Declare functions to handle actions to Clickable components
def exit_game():
    global running
    running = False


def increment_counter():
    global counter
    counter += 1


def decrement_counter():
    global counter

    if counter > 0:
        counter -= 1


# Bind the counter variable to the text of the counter-txt component, and map the actions to the buttons
PyInterfacer.bind("counter-txt", "text", lambda _: str(counter))
PyInterfacer.map_actions(
    {
        "exit-btn": exit_game,
        "start-counter-btn": lambda: PyInterfacer.change_focus("counter"),
        "goto-menu-btn": lambda: PyInterfacer.change_focus("menu"),
        "add-btn": increment_counter,
        "subtract-btn": decrement_counter,
        "fullscreen-btn": lambda: pygame.display.toggle_fullscreen(),
    }
)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            PyInterfacer.emit_click()
        elif event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_PLUS, pygame.K_KP_PLUS):
                increment_counter()
            elif event.key in (pygame.K_MINUS, pygame.K_KP_MINUS):
                decrement_counter()
            elif event.key == pygame.K_ESCAPE:
                PyInterfacer.change_focus("menu")
            elif event.key == pygame.K_f:
                pygame.display.toggle_fullscreen()

    PyInterfacer.handle()
    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
