import pygame
import os

pygame.init()

from pyinterfacer import interfacer as PyInterfacer
from src.entities import Player, EnemySpawner


class Main:
    def __init__(self) -> None:

        pygame.display.set_caption("Space Pew Pew")

        self._width, self._height = 600, 800
        self._display = pygame.display.set_mode((self._width, self._height))

        PyInterfacer.add_custom_components(
            {"player": Player, "enemy-spawner": EnemySpawner}
        )
        PyInterfacer.load_all(os.path.abspath("interfaces/"))
        PyInterfacer.init()
        PyInterfacer.go_to("menu")

        self._player: Player = PyInterfacer.get_component("player")

        self._clock = pygame.time.Clock()
        self._FPS = 120

        self._running = True

        self.setup_components()

    def setup_components(self) -> None:
        PyInterfacer.map_actions(
            {
                "menu-start-btn": lambda: PyInterfacer.go_to("game"),
                "menu-exit-btn": self.stop,
                "game-menu-btn": lambda: PyInterfacer.go_to("menu"),
                "menu-info-btn": lambda: PyInterfacer.go_to("info"),
                "info-menu-btn": lambda: PyInterfacer.go_to("menu"),
                "game-over-menu-btn": lambda: PyInterfacer.go_to("menu"),
            }
        )

        PyInterfacer.bind_keys(
            {
                pygame.K_ESCAPE: {"press": lambda: PyInterfacer.go_to("menu")},
            }
        )

        PyInterfacer.bind("player", "hp", "player-hp-txt", "text")

    def stop(self) -> None:
        self._running = False

    def run(self) -> None:
        enemy_spawner: EnemySpawner = PyInterfacer.get_component("enemy-spawner")

        while self._running:

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.stop()
                elif event.type == pygame.KEYDOWN:
                    self._player.handle_movement(event, state="k_down")
                elif event.type == pygame.KEYUP:
                    self._player.handle_movement(event, state="k_up")

                PyInterfacer.handle_event(event)

            PyInterfacer.handle()

            self._player.handle_enemy_hit(enemy_spawner.enemy_group)
            enemy_spawner.handle_player_hit(self._player)

            pygame.display.flip()
            self._clock.tick(self._FPS)


if __name__ == "__main__":
    # https://opengameart.org/content/space-music
    bg_sound = pygame.mixer.Sound(
        os.path.abspath(os.path.join("assets", "sound", "spaceship.wav"))
    )
    bg_sound.set_volume(0.1)

    bg_sound.play(loops=-1)
    Main().run()
    bg_sound.stop()

    pygame.quit()
