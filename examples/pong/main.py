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

        setup_interfaces(exit_action=self.stop, finish_game=self.finish_game)

    def finish_game(self):
        PyInterfacer.unload()
        setup_interfaces(exit_action=self.stop, finish_game=self.finish_game)

    def stop(self):
        self._running = False

    def run(self) -> None:

        while self._running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self._running = False

                PyInterfacer.handle_event(event)

            PyInterfacer.handle()
            pygame.display.flip()
            self._clock.tick(self._FPS)


if __name__ == "__main__":
    Main().run()
    pygame.quit()
