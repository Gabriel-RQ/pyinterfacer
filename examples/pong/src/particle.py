import pygame
import random

from typing import Tuple, Callable, Optional


class Particle(pygame.sprite.Sprite):
    def __init__(
        self, x: int, y: int, r: int, color: str, dir_x: int = 1, dir_y: int = 1
    ) -> None:
        super().__init__()

        self.x = x
        self.y = y
        self.r = r
        self.color = color

        self._vx = random.uniform(0.75, 2.75)
        self._vy = random.uniform(0.75, 2.75)

        self._x_modifier = dir_x
        self._y_modifier = dir_y

        self.image = pygame.Surface((self.r * 2, self.r * 2), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(self.x, self.y))

        pygame.draw.circle(self.image, self.color, (self.r, self.r), self.r)

    def update(self) -> None:
        self.rect.center = (self.x, self.y)

        if self._x_modifier == 0:
            self.x += self._vx * random.uniform(-5, 5)
        else:
            self.x += self._vx * self._x_modifier

        if self._y_modifier == 0:
            self.y += self._vy * random.uniform(-5, 5)
        else:
            self.y += self._vy * self._y_modifier

        self._vx -= random.uniform(0.01, 0.05)
        self._vy -= random.uniform(0.01, 0.05)

        self._vx = max(0, self._vx)
        self._vy = max(0, self._vy)


class ParticleGroup(pygame.sprite.Group):
    def update(self) -> None:
        for sprite in self.sprites():
            if sprite._vx == 0 and sprite._vy == 0:
                self.remove(sprite)
            else:
                sprite.update()


class ParticleManager:
    def __init__(self, color: str, radius_function: Optional[Callable] = None) -> None:
        self.color = color
        self._define_radius = (
            radius_function
            if radius_function is not None
            else lambda: random.uniform(0.75, 3.75)
        )
        self._particles = ParticleGroup()

    @property
    def group(self) -> ParticleGroup:
        return self._particles

    def clear(self) -> None:
        self._particles.clear()

    def generate(
        self,
        amount: int,
        where: Tuple[int, int],
        direction_modifier: Tuple[int, int] = (1, 1),
    ) -> None:
        self._particles.add(
            *[
                Particle(
                    x=where[0],
                    y=where[1],
                    r=self._define_radius(),
                    color=self.color,
                    dir_x=direction_modifier[0],
                    dir_y=direction_modifier[1],
                )
                for _ in range(amount)
            ]
        )

    @property
    def is_empty(self) -> bool:
        return len(self._particles) == 0

    def handle(self, display: pygame.Surface) -> None:
        self._particles.draw(display)
        self._particles.update()
