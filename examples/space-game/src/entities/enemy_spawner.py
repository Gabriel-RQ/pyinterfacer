import random
import pygame

from pyinterfacer import PyInterfacer
from pyinterfacer.components import Component
from pyinterfacer.groups import ComponentGroup
from .enemy import Enemy
from .player import Player


class EnemySpawner(Component):
    def __init__(
        self,
        wave_size: int,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self.wave_size = wave_size

        self.enemy_group = EnemyGroup()

    def _spawn_enemies(self) -> None:
        iw, ih = PyInterfacer.get_focused().size

        if len(self.enemy_group) == 0:
            for _ in range(self.wave_size):
                self.enemy_group.add(
                    Enemy(
                        x=random.randrange(0, iw),
                        y=random.randrange(0, ih // 2),
                        interface=self.interface,
                    )
                )

    def handle_player_hit(self, player) -> None:
        """
        Checks if the player was hit.
        """

        self.enemy_group.handle_player_hit(player)

    def update(self) -> None:
        super().update()

        self._spawn_enemies()
        PyInterfacer.INTERFACES[self.interface].add_subgroup(self.enemy_group)


class EnemyGroup(ComponentGroup):
    def handle_player_hit(self, player: Player):
        for sprite in self.sprites():
            if isinstance(sprite, Enemy):
                sprite.check_player_hit(player)
