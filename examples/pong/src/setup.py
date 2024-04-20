import os
import pygame

from pyinterfacer import PyInterfacer
from typing import Callable
from .components import *


def setup_interfaces(exit_action: Callable, finish_game: Callable, full_screen: Callable):
    # Setup custom components and groups
    PyInterfacer.add_custom_components(
        {
            "menu-title-button": MenuTitleButton,
            "paddle": Paddle,
            "dotted-line": DottedLine,
            "ball": Ball,
        }
    )
    PyInterfacer.add_custom_groups(
        {
            "paddle": PaddleGroup,
        }
    )

    # Setup component actions
    PyInterfacer.map_actions(
        {
            "exit-btn": exit_action,
            "play-btn": lambda: PyInterfacer.change_focus("game"),
            "leave-btn": finish_game,
            "fullscreen-btn": full_screen,
        }
    )

    PyInterfacer.load_all(os.path.abspath("interfaces/"))
    PyInterfacer.change_focus("menu")

    # Setup keybindings
    player1: Paddle = PyInterfacer.get_by_id("player1")
    player2: Paddle = PyInterfacer.get_by_id("player2")

    PyInterfacer.bind_keys(
        {
            pygame.K_ESCAPE: {"press": finish_game},
            pygame.K_f: {"press": full_screen},
            pygame.K_w: {"press": lambda: player1.move("up"), "release": player1.stop},
            pygame.K_s: {
                "press": lambda: player1.move("down"),
                "release": player1.stop,
            },
            pygame.K_UP: {"press": lambda: player2.move("up"), "release": player2.stop},
            pygame.K_DOWN: {
                "press": lambda: player2.move("down"),
                "release": player2.stop,
            },
            pygame.K_SPACE: {"press": unpause_after_score},
        }
    )

    # Setup component bindings
    PyInterfacer.bind("player1", "score", "p1-score-txt", "text")
    PyInterfacer.bind("player2", "score", "p2-score-txt", "text")


def unpause_after_score():
    if (f := PyInterfacer.get_focused()) is not None and f.name not in ("menu", "victory"):
        PyInterfacer.change_focus("game")
