import pygame
from pyinterfacer import interfacer as PyInterfacer


class Bullet(pygame.sprite.Sprite):
    def __init__(
        self,
        x: int,
        y: int,
        speed_multiplier: int = 1,
        color: str = "yellow",
    ) -> None:
        super().__init__()

        self.x = x
        self.y = y
        self.speed = 6 * speed_multiplier

        self.image = pygame.Surface((4, 9))
        self.image.fill(color)
        self.rect = self.image.get_rect(center=(self.x, self.y))

    def update(self, *args, **kwargs) -> None:
        self.y -= self.speed
        self.rect = self.image.get_rect(center=(self.x, self.y))


class BulletGroup(pygame.sprite.Group):
    def update(self, *args, **kwargs) -> None:
        for sprite in self:
            if (
                sprite.rect.bottom < 0
                or sprite.rect.top > PyInterfacer.current_focus.height
            ):
                sprite.kill()
                continue

            sprite.update(*args, **kwargs)
