"""
@author: Gabriel RQ
@description: Backup manager class. Serves the purpouse of keeping a backup of the data needed to restore PyInterfacer after unloading it.
"""

import os
import yaml
import typing
from typing import Optional, List, Dict

if typing.TYPE_CHECKING:
    from ..pyinterfacer import PyInterfacer
    from ..interface import Interface
    from ..components.handled import _Component
    from ._binding import _BindingManager
    from ._overlay import _OverlayManager


# TODO: Implement a feature similar to the raw reload from previous versions of PyInterfacer, allowing to reload when changing window size (at the cost of losing state).

class _BackupManager:
    """
    Manager to handle PyInterfacer backups.
    """

    def __init__(self) -> None:
        self.focus: Optional[str] = None
        self.interfaces: Dict[str, "Interface"] = {}
        self.components: Dict[str, "_Component"] = {}
        self.actions = {}
        self.keybindings: Optional["_BindingManager"] = None

        self.have_backup = False

        self._interface_files: List[str] = []

    def remember_interface_file(self, i: str) -> None:
        """
        Saves the location of a previous loaded interface file.

        :param i: Path to YAML interface file.
        """

        if i not in self._interface_files:
            self._interface_files.append(i)

    def save(self, path: str) -> None:
        """
        Persists the current PyInterfacer backup data in the specified backup yaml file.
        This overwrites the backup file each time it's called.

        :param path: Path to the YAML backup file. It will be created if needed.
        """

        # Make a raw backup of the interfaces, without preserving state
        interfaces = []
        for i in self._interface_files:
            with open(i, "r") as f:
                interfaces.append(yaml.safe_load(f))

        data = {
            "focus": self.focus,
            "interfaces": interfaces,
        }
        
        with open(path, "w") as f:
            yaml.safe_dump(data, f)

    def load(self, pyinterfacer: "PyInterfacer", path: str) -> None:
        """
        Loads data saved in the YAML backup file into PyInterfacer.

        :param pyinterfacer: PyInterfacer's object instance.
        :param path: Path to the backup file.
        """

        with open(path, "r") as f:
            data = yaml.safe_load(f)

            for interface in data["interfaces"]:
                pyinterfacer._parse_interface(interface)

            pyinterfacer._current_focus = pyinterfacer._interfaces.get(data["focus"])

    def reload(self, pyinterfacer: "PyInterfacer") -> None:
        """
        Reload the last saved state.

        :param pyinterfacer: PyInterfacer's object instance.
        """

        pyinterfacer._interfaces = self.interfaces.copy()
        pyinterfacer._components = self.components.copy()
        pyinterfacer._current_focus = pyinterfacer._interfaces.get(self.focus)
        pyinterfacer._component_action_mapping = self.actions.copy()
        pyinterfacer._bindings = self.keybindings
        pyinterfacer._update_actions()
        pyinterfacer.overlay.restore()

    def clear(self) -> None:
        """Clears the runtime backups."""

        self.focus = None
        self.interfaces.clear()
        self.components.clear()
        self.actions.clear()
        self.keybindings = None
        self.have_backup = False

    def backup(self, pyinterfacer: "PyInterfacer") -> None:
        """
        Backup the current state of PyInterfacer.

        :param pyinterfacer: PyInterfacer's object instance.
        """

        self.focus = pyinterfacer._current_focus.name
        self.interfaces = pyinterfacer._interfaces.copy()
        self.components = pyinterfacer._components.copy()
        self.actions = pyinterfacer._component_action_mapping.copy()
        self.keybindings = pyinterfacer._bindings

        self.have_backup = True