"""
@author: Gabriel RQ
@description: Backup manager class. Serves the purpouse of keeping a backup of the data needed to restore PyInterfacer after unloading it.
"""

import typing
from typing import Optional

if typing.TYPE_CHECKING:
    from ..pyinterfacer import PyInterfacer
    from ..interface import Interface


class _BackupManager:
    """Manager to handle PyInterfacer backups."""

    def __init__(self) -> None:
        self._focus: Optional["Interface"] = None
        self._interfaces = {}
        self._components = {}
        self._action_mappings = {}
        self.have_backup = False

    @property
    def focus(self) -> Optional["Interface"]:
        return self._focus

    @focus.setter
    def focus(self, f: "Interface") -> None:
        self._focus = f

    @property
    def interfaces(self) -> dict:
        return self._interfaces

    @interfaces.setter
    def interfaces(self, i: dict) -> None:
        self._interfaces = i

    @property
    def components(self) -> dict:
        return self._components

    @components.setter
    def components(self, c: dict) -> None:
        self._components = c

    @property
    def actions(self) -> dict:
        return self._action_mappings

    @actions.setter
    def actions(self, a: dict) -> None:
        self._action_mappings = a

    def clear(self) -> None:
        """Clears the backups."""

        self._focus = None
        self._interfaces.clear()
        self._components.clear()
        self._action_mappings.clear()
        self.have_backup = False

    def restore(self, pyinterfacer: "PyInterfacer") -> None:
        """
        Restores PyInterfacer to the backed up data state.

        :param pyinterfacer: Reference to PyInterfacer class.
        """

        pyinterfacer._current_focus = self.focus
        pyinterfacer.INTERFACES = self.interfaces.copy()
        pyinterfacer.COMPONENTS = self.components.copy()
        pyinterfacer._COMPONENT_ACTION_MAPPING = self._action_mappings.copy()
        pyinterfacer._overlay.restore()
