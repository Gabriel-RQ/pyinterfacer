"""
@author: Gabriel RQ
@description: Backup manager class. Serves the purpouse of keeping a backup of the data needed to restore PyInterfacer after unloading it.
"""

import os
import shelve
import yaml
import typing
from typing import Optional, List, Dict

if typing.TYPE_CHECKING:
    from ..pyinterfacer import PyInterfacer
    from ..interface import Interface
    from ..components.handled import _Component
    from ._binding import _BindingManager


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
        self.backup_path = os.path.join(
            os.path.dirname(os.path.realpath(__file__)), "backup"
        )

        self._interface_files: List[str] = []
        # list of dictionaries loaded from YAML interface declaration / unserialized from dumped file. Only used when restoring a serilized backup file.
        self._raw_interface_data: list[dict] = []

    def remember_interface_file(self, i: str) -> None:
        """
        Saves the location of a previous loaded interface file.

        :param i: Path to YAML interface file.
        """

        if i not in self._interface_files:
            self._interface_files.append(i)

    def save(self) -> None:
        """
        Persists the current PyInterfacer backup data in the pre-specified backup directory.
        This overwrites the backup each time it's called.
        """

        # Creates the backup directory, if it does not exist
        if not os.path.exists(self.backup_path):
            os.mkdir(self.backup_path)

        # Make a raw backup of the interfaces, without preserving state
        interfaces = []
        for i in self._interface_files:
            with open(i, "r") as f:
                interfaces.append(yaml.safe_load(f))

        interface_bindings = {i.name: i._bindings for i in self.interfaces.values()}

        # Save to the serialized backup
        with shelve.open(os.path.join(self.backup_path, "pyinterfacer")) as bak:
            bak.clear()

            bak["focus"] = self.focus
            bak["actions"] = self.actions
            bak["interfaces"] = interfaces
            bak["bindings"] = {}
            bak["bindings"]["keybindings"] = self.keybindings
            bak["bindings"]["interfaces"] = interface_bindings

    def load(self, pyinterfacer: "PyInterfacer") -> None:
        """
        Loads data saved in the serialized backup file into PyInterfacer.

        :param pyinterfacer: PyInterfacer's object instance.
        """

        backup_file = os.path.join(self.backup_path, "pyinterfacer")
        if not os.path.exists(backup_file):
            raise FileNotFoundError("Could not find PyInterfacer's backup file.")

        with shelve.open(backup_file) as bak:
            pyinterfacer._current_focus = bak.get("focus")
            pyinterfacer._component_action_mapping = bak.get("actions")
            pyinterfacer._interfaces = bak.get("interfaces")
            pyinterfacer._bindings = bak["bindings"]["keybindings"]

            interface_bindings = bak["bindings"]["interfaces"]
            if interface_bindings is not None:
                for interface, binding_man in interface_bindings.items():
                    pyinterfacer._interfaces[interface]._bindings = binding_man
