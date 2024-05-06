import pygame
from pyinterfacer import PyInterfacer

pygame.init()

display_sizes = pygame.display.list_modes()
display = pygame.display.set_mode(display_sizes[len(display_sizes) // 2], pygame.SCALED)
clock = pygame.time.Clock()
FPS = 120

interfacer = PyInterfacer()

# Loads the interface and focus in the initial screen
interfacer.load_all("interfaces/")
interfacer.init()
interfacer.go_to("menu")

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
interfacer.bind("counter-txt", "text", lambda _: str(counter))
interfacer.map_actions(
    {
        "exit-btn": exit_game,
        "start-counter-btn": lambda: interfacer.go_to("counter"),
        "goto-menu-btn": lambda: interfacer.go_to("menu"),
        "add-btn": increment_counter,
        "subtract-btn": decrement_counter,
        "fullscreen-btn": lambda: pygame.display.toggle_fullscreen(),
    }
)
interfacer.bind_keys(
    {
        pygame.K_PLUS: {"press": increment_counter},
        pygame.K_KP_PLUS: {"press": increment_counter},
        pygame.K_MINUS: {"press": decrement_counter},
        pygame.K_KP_MINUS: {"press": decrement_counter},
        pygame.K_f: {"press": pygame.display.toggle_fullscreen},
        pygame.K_ESCAPE: {"press": lambda: interfacer.go_to("menu")},
    }
)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        interfacer.handle_event(event)

    interfacer.handle()
    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
