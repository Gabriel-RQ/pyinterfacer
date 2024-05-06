import pygame
import random

from pyinterfacer.util import Font
from typing import Tuple, Callable, Optional


class Particle(pygame.sprite.Sprite):
    """Simple particle class that moves in a direction and fades out over time."""

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

    def update(self, *args, **kwargs) -> None:
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


class TextParticle(pygame.sprite.Sprite):
    """Text particle that fades out over time."""

    def __init__(self, text: str, color: str, x: int, y: int) -> None:
        super().__init__()

        self.x = x
        self.y = y
        self.color = color

        self.text = text
        self._font_size = 32

        self._angle = random.randint(-45, 45)
        self.font = Font(
            "Arial",
            24,
            self.color,
            bold=True,
            italic=False,
            antialiased=True,
            rotation=self._angle,
        )

        self._x_modifier = random.choice([-1, 1])
        self._y_modifier = 0

        self._scale_modifier = random.uniform(0.75, 1.25)

    def update(self, *args, **kwargs) -> None:
        self.image, _ = self.font.render(self.text)
        self.image = pygame.transform.smoothscale_by(self.image, self._scale_modifier)
        self.rect = self.image.get_rect(center=(self.x, self.y))

        # gives the text a "floating" effect
        self.x += random.uniform(-2, 2) * self._x_modifier
        self.y += random.uniform(-2, 2) * self._y_modifier

        self._scale_modifier -= 0.0075
        self._scale_modifier = max(0, self._scale_modifier)


class ParticleGroup(pygame.sprite.Group):
    def update(self, *args, **kwargs) -> None:
        for sprite in self.sprites():
            if isinstance(sprite, Particle):
                if sprite._vx == 0 and sprite._vy == 0:
                    self.remove(sprite)
                else:
                    sprite.update()
            elif isinstance(sprite, TextParticle):
                if sprite._scale_modifier == 0:
                    self.remove(sprite)
                else:
                    sprite.update()


class ParticleManager:
    def __init__(self, color: str) -> None:
        self.color = color
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
        radius_func: Optional[Callable] = None,
    ) -> None:
        """
        Generate circle particles that fade over time.

        :param amount: The amount of particles to generate each frame.
        :param where: The position where the particles will be generated.
        :param direction_modifier: The direction the particles will move in.
        :param radius_func: A function that returns a random radius for the particles.
        """
        define_radius = lambda: random.uniform(0.75, 3.75)

        self._particles.add(
            *[
                Particle(
                    x=where[0],
                    y=where[1],
                    r=radius_func() if radius_func else define_radius(),
                    color=self.color,
                    dir_x=direction_modifier[0],
                    dir_y=direction_modifier[1],
                )
                for _ in range(amount)
            ]
        )

    def spawn_text(self, text: str, where: Tuple[int, int]) -> None:
        self._particles.add(TextParticle(text, self.color, where[0], where[1]))

    @property
    def is_empty(self) -> bool:
        return len(self._particles) == 0

    def handle(self, display: pygame.Surface) -> None:
        self._particles.draw(display)
        self._particles.update()
