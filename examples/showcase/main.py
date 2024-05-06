import pygame

pygame.init()

from pyinterfacer import PyInterfacer

WINDOW_SIZE = WIDTH, HEIGHT = 800, 600
display = pygame.display.set_mode(WINDOW_SIZE, 0, 32)

interfacer = PyInterfacer()
interfacer.load("interface.yaml")
interfacer.init()
interfacer.go_to("interface")

i = interfacer.current_focus


def draw_grid(surf: pygame.Surface):
    cell_width = i.width // i.columns
    cell_height = i.height // i.rows

    for row in range(0, i.width, cell_width):
        for column in range(0, i.height, cell_height):
            r = pygame.Rect(row, column, cell_width, cell_height)
            pygame.draw.rect(surf, "#c1c1c1", r, width=1)


running = True
while running:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        interfacer.handle_event(event)

    interfacer.handle()
    draw_grid(display)

    pygame.display.flip()

pygame.quit()
