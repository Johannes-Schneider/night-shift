import getpass
import logging
from pathlib import Path
from typing import Optional, List, Any, Dict

from src.configuration.partial_configuration import PartialConfiguration


class HostConfiguration(PartialConfiguration):

    def __init__(self, parent: Optional["HostConfiguration"] = None):
        super().__init__(parent)
        self._name: Optional[str] = self._register_property(self.name.__name__)
        self._aliases: Optional[List[str]] = self._register_property(self.aliases.__name__)
        self._ssh_user: Optional[str] = self._register_property(self.ssh_user.__name__)
        self._ssh_address: Optional[str] = self._register_property(self.ssh_address.__name__)
        self._ssh_port: Optional[int] = self._register_property(self.ssh_port.__name__)
        self._ssh_key: Optional[Path] = self._register_property(self.ssh_key.__name__)

    @property
    def name(self) -> str:
        return self._get(self.name.__name__)

    @name.setter
    def name(self, value: str) -> None:
        self._set(self.name.__name__, value)

    @property
    def aliases(self) -> List[str]:
        return self._get(self.aliases.__name__)

    @aliases.setter
    def aliases(self, value: List[str]) -> None:
        self._set(self.aliases.__name__, value)

    @property
    def ssh_user(self) -> str:
        return self._get(self.ssh_user.__name__)

    @ssh_user.setter
    def ssh_user(self, value: str) -> None:
        self._set(self.ssh_user.__name__, value)

    @property
    def ssh_address(self) -> str:
        return self._get(self.ssh_address.__name__)

    @ssh_address.setter
    def ssh_address(self, value: str) -> None:
        self._set(self.ssh_address.__name__, value)

    @property
    def ssh_port(self) -> int:
        return self._get(self.ssh_port.__name__)

    @ssh_port.setter
    def ssh_port(self, value: int) -> None:
        self._set(self.ssh_port.__name__, value)

    @property
    def ssh_key(self) -> Path:
        return self._get(self.ssh_key.__name__)

    @ssh_key.setter
    def ssh_key(self, value: Path) -> None:
        self._set(self.ssh_key.__name__, value)
