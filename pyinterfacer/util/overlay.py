"""
@author: Gabriel RQ
@description: Overlay manager class.
"""

import pygame
import typing

from typing import Tuple, Optional

if typing.TYPE_CHECKING:
    from ..interface import Interface


class OverlayManager:
    """Simple manager to handle overlays."""

    def __init__(self) -> None:
        self._surface: pygame.Surface = None
        self._render_targets = {"single": [], "many": [], "interfaces": []}
        self._render_targets_backup = None
        self._opacity = 0  # ranges from 0 to 255

    def add_single_target(
        self, s: pygame.Surface, d: pygame.Rect | Tuple[int, int]
    ) -> None:
        """Adds a single Surface to be rendered on the overlay."""

        self._render_targets["single"].append((s, d))

    def add_many_targets(self, s: Tuple) -> None:
        """Adds many surfaces to be rendered on the overlay."""

        self._render_targets["many"].extend(s)

    def add_interface_target(self, i: "Interface") -> None:
        """Adds an interface to be rendered in the overlay."""

        self._render_targets["interfaces"].append(i)

    def set_overlay(self, surf: pygame.Surface) -> None:
        """Sets the overlay surface."""
        self._surface = surf

    def set_opacity(self, o: int) -> None:
        """
        Sets the opacity of the overlay. The opacity should range from 0 to 255, if a value below or above is provided, the closest value will be picked instead.

        :param o: Integer value from 0 to 255.
        """
        self._opacity = max(0, min(o, 255))

    def get_opacity(self) -> int:
        """Returns the overlay current opacity."""
        return self._opacity

    def clear(self) -> None:
        """Clears the overlay surface."""

        # Keeps a copy of the last render targets to restore
        if any(
            (
                len(self._render_targets["single"]) > 0,
                len(self._render_targets["many"]) > 0,
                len(self._render_targets["interfaces"]) > 0,
            )
        ):
            self._render_targets_backup = {
                "single": self._render_targets["single"].copy(),
                "many": self._render_targets["many"].copy(),
                "interfaces": self._render_targets["interfaces"].copy(),
            }
        self._render_targets["single"].clear()
        self._render_targets["many"].clear()
        self._render_targets["interfaces"].clear()

    def restore(self) -> None:
        """Restores the last render targets to the overlay."""

        if self._render_targets_backup is not None:
            self._render_targets = self._render_targets_backup.copy()

        self._render_targets_backup = None

    def render(self) -> Optional[pygame.Surface]:
        """Returns the overlay's surface with every render target drawn into it."""

        if self._surface is None:
            return None

        self._surface.fill(
            (0, 0, 0, self._opacity)
        )  # fills the overlay with a transparent color, to 'clean' it from previous surfaces

        for t in self._render_targets["single"]:
            self._surface.blit(*t)

        self._surface.blits(self._render_targets["many"])

        for i in self._render_targets["interfaces"]:
            i.draw(self._surface)

        return self._surface

    def update_interfaces(self) -> None:
        """Calls `Interface.update` for the interfaces rendered into the overlay."""

        for i in self._render_targets["interfaces"]:
            i.update()
