import random

from pyinterfacer import interfacer as PyInterfacer
from pyinterfacer.components.handled import _Component
from pyinterfacer.groups import ComponentGroup
from .enemy import Enemy
from .player import Player


class EnemySpawner(_Component):
    def __init__(
        self,
        wave_size: int,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self.wave_size = wave_size

        self.enemy_group = EnemyGroup()

    def _spawn_enemies(self) -> None:
        iw, ih = PyInterfacer.current_focus.size

        if len(self.enemy_group) == 0:
            for _ in range(self.wave_size):
                self.enemy_group.add(
                    Enemy(
                        pos=(random.randrange(0, iw), random.randrange(0, ih // 2)),
                        interface=self.interface,
                    )
                )

    def after_load(self, interface) -> None:
        interface.add_subgroup(self.enemy_group)

    def handle_player_hit(self, player) -> None:
        """
        Checks if the player was hit.
        """

        self.enemy_group.handle_player_hit(player)

    def update(self, *args, **kwargs) -> None:
        super().update()

        self._spawn_enemies()


class EnemyGroup(ComponentGroup):
    def handle_player_hit(self, player: Player):
        for sprite in self.sprites():
            if isinstance(sprite, Enemy):
                sprite.check_player_hit(player)
