import pygame


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

    def update(self) -> None:
        self.y -= self.speed
        self.rect = self.image.get_rect(center=(self.x, self.y))


class BulletGroup(pygame.sprite.Group):
    def update(self) -> None:
        for sprite in self.sprites():
            if sprite.rect.bottom < 0:
                self.remove(sprite)
                continue

            sprite.update()
