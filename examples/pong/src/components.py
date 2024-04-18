import pygame
import math

from pyinterfacer import PyInterfacer, DefaultComponentTypes
from pyinterfacer.components import TextButton, Component
from pyinterfacer.groups import ComponentGroup
from typing import Literal


class MenuTitleButton(TextButton):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.subtype = DefaultComponentTypes.BUTTON.value

    def hover_action(self) -> None:
        super().hover_action()

        i = PyInterfacer.get_interface("menu")
        if i is None:
            return

        if self._hovered:
            i.set_background("#c1c1c1")
        else:
            i.set_background("#1c1c1c")


class DottedLine(Component):
    def __init__(
        self,
        color: str,
        thickness: int = 1,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)

        self.color = color
        self.thickness = thickness
        self.width = self.thickness

        self.preload_image()

    def preload_image(self) -> None:
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self._align()

        for i in range(0, self.height, 15):
            pygame.draw.line(
                surface=self.image,
                color=self.color,
                start_pos=(0, i),
                end_pos=(0, i + 10),
                width=self.thickness,
            )

    def update(self) -> None:
        return


class Entity(Component):
    def __init__(self, color: str, speed: int, **kwargs) -> None:
        super().__init__(**kwargs)

        self.color = color
        self.speed = speed
        self.subtype = DefaultComponentTypes.COMPONENT.value


class Paddle(Entity):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

        self._moving = {"up": False, "down": False}

    def move(self, where: Literal["up", "down"]) -> None:
        self._moving[where] = True

    def stop(self) -> None:
        self._moving["up"] = False
        self._moving["down"] = False

    def update(self) -> None:
        self.image = pygame.Surface((self.width, self.height))
        self.rect = self.image.get_rect()
        self._align()

        self.image.fill(self.color)

        if self._moving["up"]:
            self.y -= self.speed
        elif self._moving["down"]:
            self.y += self.speed

        _, height = PyInterfacer.get_interface(self.interface).size
        if self.y < 0:
            self.y = height
        elif self.y > height:
            self.y = 0


class Ball(Entity):
    def __init__(self, radius: int, **kwargs) -> None:
        super().__init__(**kwargs)

        self.radius = radius
        self.diameter = self.radius**2

        self._x_modifier = 1
        self._y_modifier = 1

        self.preload_image()

    def preload_image(self) -> None:
        self.image = pygame.Surface((self.diameter, self.diameter), pygame.SRCALPHA)
        self.rect = self.image.get_rect()

        pygame.draw.circle(self.image, self.color, self.rect.center, self.radius)

    def update(self) -> None:
        self._align()

        width, height = PyInterfacer.get_interface(self.interface).size

        self.x += self.speed * self._x_modifier
        self.y += self.speed * self._y_modifier

        if self.y < 0 or self.y > height:
            self._y_modifier *= -1

        if self.x < 0 or self.x > width:
            self._x_modifier *= -1


class PaddleGroup(ComponentGroup): ...
