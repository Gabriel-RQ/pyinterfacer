"""
@author: Gabriel RQ
@description: Backup manager class. Serves the purpouse of keeping a backup of the data needed to restore PyInterfacer after unloading it.
"""

import pickle
import yaml
import typing
from typing import Optional

if typing.TYPE_CHECKING:
    from ..pyinterfacer import PyInterfacer


class _BackupManager:
    """
    Manager to handle PyInterfacer backups.
    Able to backup and restore:
        - current focus
        - loaded interfaces
        - loaded components
        - mapped actions
    """

    def __init__(self) -> None:
        self._focus: Optional[str] = None
        self._interface_files: list[str] = []
        # list of dictionaries loaded from YAML interface declaration / unserialized from dumped file. Only used when restoring a serilized backup file.
        self._raw_interface_data: list[dict] = []
        self._interfaces = {}
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

    def dump(self, to: str) -> None:
        """
        Serializes the backup data with pickle and dumps it to the specified location.

        :param to: Path to dump the data.
        """

        data = {
            "focus": self._focus,
            "actions": self._actions_mapping,
            "interfaces": [],
        }

        for i in self._interface_files:
            with open(i, "r") as f:
                data["interfaces"].append(yaml.safe_load(f))

        with open(to, "bw") as f:
            pickle.dump(data, f)

    def load(self, path: str) -> None:
        """
        Loads interface data from a previously dumped backup file. This overwrites current backup data.

        :param path: Path to the backup file.
        """

        with open(path, "rb") as f:
            data = pickle.load(f)

        if all((data is not None, isinstance(data, dict), len(data) > 0)):
            focus = data.get("focus")
            actions = data.get("actions")
            interfaces = data.get("interfaces")

            if focus is not None:
                self._focus = focus
            if actions is not None:
                self._actions_mapping = actions
            if interfaces is not None:
                self._raw_interface_data = interfaces

            if any((focus, actions, interfaces)):
                self.have_backup = True

    def clear(self) -> None:
        """Clears the backups."""

        # Interface files locations are not cleared, otherwise it wouldnt be possible to
        # retrieve them again without using PyInterfacer.load or PyInterfacer.load_all
        self._focus = None
        self._interfaces.clear()
        self._raw_interface_data.clear()
        self._components.clear()
        self._actions_mapping.clear()
        self.have_backup = False

    def restore(
        self, pyinterfacer: "PyInterfacer", raw: bool = False, from_dump: bool = False
    ) -> None:
        """
        Restores PyInterfacer to the backed up data state.

        :param pyinterfacer: Reference to PyInterfacer class.
        :param raw: Wether to reload from saved state or from raw YAML loaded data.
        """

        pyinterfacer._COMPONENT_ACTION_MAPPING = self._actions_mapping.copy()

        if from_dump:  # loads the interfaces from unserialized interface data
            for interface_dict in self._raw_interface_data:
                pyinterfacer._parse_interface(interface_dict)
            pyinterfacer._update_actions()
        elif raw:  # reloads the interfaces from the YAML files
            for interface in self._interface_files:
                pyinterfacer.load(interface)
            pyinterfacer._update_actions()
        else:  # just restores the previously loaded instances
            pyinterfacer.INTERFACES = self.interfaces.copy()
            pyinterfacer.COMPONENTS = self.components.copy()

        pyinterfacer._overlay.restore()  # if going fullscreen, the overlay probably wont change size right now
        pyinterfacer._current_focus = pyinterfacer.get_interface(self._focus)
