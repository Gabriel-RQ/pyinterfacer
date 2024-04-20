import pygame

from pyinterfacer import PyInterfacer
from src.setup import setup_interfaces

pygame.init()


class Main:
    def __init__(self) -> None:
        pygame.display.set_caption("Pong")

        self._size = self._width, self._height = 800, 600
        self._display = pygame.display.set_mode(self._size, pygame.SCALED, 32)

        self._clock = pygame.time.Clock()
        self._FPS = 120

        self._running = True
        self._fullscreen = False

        setup_interfaces(exit_action=self.stop, finish_game=self.finish_game, full_screen=self.full_screen)

    def finish_game(self):
        PyInterfacer.unload()
        setup_interfaces(exit_action=self.stop, finish_game=self.finish_game, full_screen=self.full_screen)

    def full_screen(self):
        self._fullscreen = not self._fullscreen

        if self._fullscreen:
            self._size = self._width, self._height = pygame.display.get_window_size()
            self._display = pygame.display.set_mode(self._size, pygame.FULLSCREEN, 32)
        else:
            self._size = self._width, self._height = 800, 600
            self._display = pygame.display.set_mode(self._size, pygame.SCALED, 32)

        self.finish_game()

    def stop(self):
        self._running = False

    def run(self) -> None:
        paddle_group = PyInterfacer.get_interface("game").get_type_group("paddle")

        while self._running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self._running = False

                PyInterfacer.handle_event(event)

            PyInterfacer.handle()
            paddle_group.handle_victory()

            pygame.display.flip()
            self._clock.tick(self._FPS)


if __name__ == "__main__":
    Main().run()
    pygame.quit()
