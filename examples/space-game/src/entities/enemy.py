import random
import pygame

from pyinterfacer import PyInterfacer
from pyinterfacer.components import SpritesheetAnimation
from .bullet import Bullet, BulletGroup
from .player import Player


class Enemy(SpritesheetAnimation):
    def __init__(self, **kwargs) -> None:
        super().__init__(
            id="_",
            type="enemy",
            spritesheet="assets/images/enemy/spaceship16x16.png",
            sprite_width=16,
            sprite_height=16,
            colorkey="black",
            width=128,
            height=128,
            delay=20,
            **kwargs,
        )

        self._bullet_group = BulletGroup()

        self._shoot_delay = 175
        self._shoot_delay_counter = 1

        self._speed = 1
        self._x_vel_modifier = 1
        self._y_vel_modifier = 1

        self._hp = 50

    def check_player_hit(self, player: Player):
        """
        Checks if player was hit, removes bullet and does damage to player.
        """
        bullet = pygame.sprite.spritecollideany(player, self._bullet_group)

        if bullet is not None:
            player.take_damage()
            self._bullet_group.remove(bullet)

    def take_damage(self) -> bool:
        """
        Returns True if the enemy is dead, else False.
        """
        self._hp -= 10

        return self._hp <= 0

    def _move(self) -> None:
        iw, ih = PyInterfacer.get_focused().size

        if self.rect.centerx < 0:
            self._x_vel_modifier = 1
        elif self.rect.centerx > iw:
            self._x_vel_modifier = -self._x_vel_modifier

        if self.rect.centery < 0:
            self._y_vel_modifier = 1
        elif self.rect.centery > (ih // 2):
            self._y_vel_modifier = -self._y_vel_modifier

        # Some bit of randomness to the enemy's movement
        self._x_vel_modifier += (random.random() - 0.5) * 0.15
        self._y_vel_modifier += (random.random() - 0.5) * 0.15

        self.x += self._speed * self._x_vel_modifier
        self.y += self._speed * self._y_vel_modifier

    def update(self) -> None:
        super().update()

        # Handle enemy movement
        self._move()

        # Handle enemy shooting
        if self._shoot_delay_counter == 0:
            self._bullet_group.add(Bullet(self.x, self.y, -0.25, color="#72cfa3"))

        self._shoot_delay_counter = (self._shoot_delay_counter + 1) % self._shoot_delay

        PyInterfacer.INTERFACES[self.interface].add_subgroup(self._bullet_group)
