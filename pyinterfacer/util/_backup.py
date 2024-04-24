"""
@author: Gabriel RQ
@description: Backup manager class. Serves the purpouse of keeping a backup of the data needed to restore PyInterfacer after unloading it.
"""

import typing
from typing import Optional

if typing.TYPE_CHECKING:
    from ..pyinterfacer import PyInterfacer


class _BackupManager:
    """Manager to handle PyInterfacer backups."""

    def __init__(self) -> None:
        self._focus: Optional[str] = None
        self._interfaces = {}
        self._interface_files: list[str] = []
        self._components = {}
        self._actions_mapping = {}
        self.have_backup = False

    @property
    def focus(self) -> Optional[str]:
        return self._focus

    @focus.setter
    def focus(self, f: str) -> None:
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
        self._actions_mapping = a

    def remember_interface_file(self, i: str) -> None:
        """
        Saves the location of a previous loaded interface file.

        :param i: Path to YAML interface file.
        """

        if i not in self._interface_files:
            self._interface_files.append(i)

    def clear(self) -> None:
        """Clears the backups."""

        self._focus = None
        self._interfaces.clear()
        self._components.clear()
        self._actions_mapping.clear()
        self.have_backup = False

    def restore(self, pyinterfacer: "PyInterfacer", raw: bool = False) -> None:
        """
        Restores PyInterfacer to the backed up data state.

        :param pyinterfacer: Reference to PyInterfacer class.
        :param raw: Wether to reload from saved state or from raw YAML loaded data.
        """

        pyinterfacer._COMPONENT_ACTION_MAPPING = self._actions_mapping.copy()
        if raw:
            for interface in self._interface_files:
                pyinterfacer.load(interface)
            pyinterfacer._update_actions()
        else:
            pyinterfacer.INTERFACES = self.interfaces.copy()
            pyinterfacer.COMPONENTS = self.components.copy()

        pyinterfacer._overlay.restore()
        pyinterfacer._current_focus = pyinterfacer.get_interface(self._focus)
