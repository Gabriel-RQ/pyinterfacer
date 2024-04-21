import pygame
import math
import random

from pyinterfacer import PyInterfacer, DefaultComponentTypes
from pyinterfacer.components import TextButton, Component
from pyinterfacer.groups import ComponentGroup
from .particle import ParticleManager
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
    def __init__(self, score: int = 0, **kwargs) -> None:
        super().__init__(**kwargs)

        self.score = score

        self._moving = {"up": False, "down": False}

    def reset_pos(self) -> None:
        i = PyInterfacer.get_interface(self.interface)
        width, height = i.size

        self.y = height // 2

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
            self.y -= self.speed * PyInterfacer.get_delta_time()
        elif self._moving["down"]:
            self.y += self.speed * PyInterfacer.get_delta_time()

        _, height = PyInterfacer.get_interface(self.interface).size
        if (self.y + self.height) < 0:
            self.y = height
        elif (self.y - self.height) > height:
            self.y = 0


class Ball(Entity):
    def __init__(self, radius: int, **kwargs) -> None:
        super().__init__(**kwargs)

        self.radius = radius
        self.diameter = self.radius * 2

        self._vx = self.speed
        self._vy = self.speed
        # Starts the ball in a random direction
        self._x_modifier = random.choice([-1, 1])
        self._y_modifier = 0

        self._particles = ParticleManager(color=self.color)


        self.preload_image()

    def after_load(self, interface) -> None:
        self._interface_instance = interface
        self._paddle_group: PaddleGroup = interface.get_type_group("paddle")
        self._p1: Paddle = PyInterfacer.get_by_id("player1")
        self._p2: Paddle = PyInterfacer.get_by_id("player2")

        # adds the particles to be rendered
        interface.add_subgroup(self._particles.group)
        
    def reset(self) -> None:
        self.x = self._interface_instance.width // 2
        self.y =  self._interface_instance.height // 2

        self._vx = self.speed
        self._vy = self.speed
        self._x_modifier = random.choice([-1, 1])
        self._y_modifier = 0

    def preload_image(self) -> None:
        self.image = pygame.Surface((self.diameter, self.diameter), pygame.SRCALPHA)
        self.rect = self.image.get_rect()

        pygame.draw.circle(self.image, self.color, self.rect.center, self.radius)

    def update(self) -> None:
        self._align()

        # Ball movement
        self.x += self._vx * self._x_modifier * PyInterfacer.get_delta_time()
        self.y += self._vy * self._y_modifier * PyInterfacer.get_delta_time()

        # Collision detection
        if self.y < 0 or self.y > self._interface_instance.height:
            self._y_modifier *= -1
            self._particles.generate(
                35,
                where=(self.x, self.y),
                direction_modifier=(-self._x_modifier, self._y_modifier),
            )

        if self.x < 0:
            self._x_modifier = 1
            self._p2.score += 1
            self.reset()
            self._p1.reset_pos()
            self._p2.reset_pos()
            PyInterfacer.change_focus("score-pause")
        elif self.x > self._interface_instance.width:
            self._x_modifier = -1
            self._p1.score += 1
            self.reset()
            self._p1.reset_pos()
            self._p2.reset_pos()
            PyInterfacer.change_focus("score-pause")

        collided_paddle: Paddle = self._paddle_group.ball_collided(self)
        if collided_paddle:
            # Reflect the ball based on where it hit the paddle
            offset = (self.y - collided_paddle.y) / (
                (collided_paddle.height + self.diameter) / 2
            )
            angle = (
                max(min(offset, 0.7), -0.7) * math.pi / 4
            )  # limit the angle to between -45 and 45 degrees

            self._x_modifier *= -1
            self._y_modifier = math.sin(angle)

            # Add a fixed offset to the ball's position to ensure it's not still colliding with the paddle
            if self._x_modifier > 0:
                self.x = collided_paddle.x + collided_paddle.width + self.diameter
            else:
                self.x = collided_paddle.x - (self.diameter * 2)

            # Spawn particles when hitting the paddle
            self._particles.generate(
                15,
                where=(collided_paddle.x, collided_paddle.y),
                direction_modifier=(self._x_modifier, 0),
            )
            self._particles.spawn_text(random.choice(["Ping!", "Pong!"]), (self.x, self.y))

        self._particles.generate(1, self.rect.center, direction_modifier=(self._x_modifier, self._y_modifier), radius_func=lambda: random.uniform(0.75, 1.25))


class PaddleGroup(ComponentGroup):
    def ball_collided(self, ball: Ball):
        """Returns the paddle the ball collided with."""

        return pygame.sprite.spritecollideany(ball, self)
    
    def handle_victory(self) -> None:
        p1: Paddle = PyInterfacer.get_by_id("player1")
        p2: Paddle = PyInterfacer.get_by_id("player2")

        score_diff = abs(p1.score - p2.score)

        if score_diff >= 2:
            if p1.score == 5:
                PyInterfacer.get_by_id("winner-txt").text = "Player 1 wins!"
                PyInterfacer.change_focus("victory")
            elif p2.score == 5:
                PyInterfacer.get_by_id("winner-txt").text = "Player 2 wins!"
                PyInterfacer.change_focus("victory")
        elif score_diff == 1:
            # If the diff is 1, the score should reset to 0 and the game should continue until the diff is 2, reseting to 0 every time it reaches 2 with a diff of 1. But that would be too much for this example, so i keep it simple: whoever reaches 6 first wins.
            if p1.score == 6:
                PyInterfacer.get_by_id("winner-txt").text = "Player 1 wins!"
                PyInterfacer.change_focus("victory")
            elif p2.score == 6:
                PyInterfacer.get_by_id("winner-txt").text = "Player 2 wins!"
                PyInterfacer.change_focus("victory")            
