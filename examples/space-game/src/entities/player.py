import pygame
import os

from typing import Literal
from pyinterfacer import PyInterfacer
from pyinterfacer.components import SpritesheetAnimation
from pyinterfacer.groups import ComponentGroup
from .bullet import Bullet, BulletGroup

# https://pixabay.com/sound-effects/laser-gun-shot-sound-future-sci-fi-lazer-wobble-chakongaudio-174883/
laser_shot_sound = pygame.mixer.Sound(
    os.path.abspath(os.path.join("assets", "sound", "laser-shot-chakongaudio.mp3"))
)
laser_shot_sound.set_volume(0.1)


class Player(SpritesheetAnimation):
    def __init__(
        self,
        speed: int,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)

        self.speed = speed
        self.hp = 100
        self.score = 0

        self._moving = {"left": False, "right": False}
        self._shooting = False
        self._shoot_delay = 50
        self._shoot_delay_counter = 0
        self._bullet_group = BulletGroup()

    def handle_enemy_hit(self, enemy_group: ComponentGroup) -> None:
        """
        Checks if any enemy got hit, do damage to enemies hit and remove the dead ones.
        """

        enemies_hit = pygame.sprite.groupcollide(
            self._bullet_group,
            enemy_group,
            dokilla=True,
            dokillb=False,
        )

        for i in enemies_hit.values():
            for enemy in i:
                dead = enemy.take_damage()

                if dead:
                    self.score += 1
                    enemy_group.remove(enemy)

    def handle_movement(
        self, event: pygame.Event, *, state: Literal["k_up", "k_down"]
    ) -> None:
        match event.key:
            case pygame.K_a | pygame.K_LEFT:
                self._moving["left"] = True if state == "k_down" else False
            case pygame.K_d | pygame.K_RIGHT:
                self._moving["right"] = True if state == "k_down" else False
            case pygame.K_SPACE:
                self._shooting = True if state == "k_down" else False
                self._shoot_delay_counter = 0

    def take_damage(self) -> None:
        self.hp -= 5

        if self.hp == 0:
            PyInterfacer.get_by_id("player-score").text = f"Score: {self.score}"
            PyInterfacer.change_focus("game-over")
            self.hp = 100
            self.score = 0

    def update(self) -> None:
        super().update()

        # Movement handling
        if self._moving["left"]:
            self.x -= self.speed
        elif self._moving["right"]:
            self.x += self.speed

        # Shooting handling
        if self._shooting and self._shoot_delay_counter == 0:
            laser_shot_sound.play()
            self._bullet_group.add(Bullet(self.x, self.y))

        self._shoot_delay_counter = (self._shoot_delay_counter + 1) % self._shoot_delay

        PyInterfacer.INTERFACES[self.interface].add_subgroup(self._bullet_group)

        # Sides collision handling
        iw, _ = PyInterfacer.INTERFACES[self.interface].size
        if self.rect.centerx < 0:
            self.x = iw
        elif self.rect.centerx > iw:
            self.x = 0
