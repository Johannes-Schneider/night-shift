from pathlib import Path
from typing import Optional, List

from src.configuration.partial_configuration import PartialConfiguration


class HostConfiguration(PartialConfiguration):

    def __init__(self, parent: Optional["HostConfiguration"] = None):
        super().__init__(parent)
        self._name: Optional[str] = self._register_property(HostConfiguration.name.fget.__name__)
        self._aliases: Optional[List[str]] = self._register_property(HostConfiguration.aliases.fget.__name__)
        self._ssh_user: Optional[str] = self._register_property(HostConfiguration.ssh_user.fget.__name__)
        self._ssh_address: Optional[str] = self._register_property(HostConfiguration.ssh_address.fget.__name__)
        self._ssh_port: Optional[int] = self._register_property(HostConfiguration.ssh_port.fget.__name__)
        self._ssh_key: Optional[Path] = self._register_property(HostConfiguration.ssh_key.fget.__name__)

    @property
    def name(self) -> str:
        return self._get(HostConfiguration.name.fget.__name__)

    @name.setter
    def name(self, value: str) -> None:
        self._set(HostConfiguration.name.fget.__name__, value)

    @property
    def aliases(self) -> List[str]:
        return self._get(HostConfiguration.aliases.fget.__name__)

    @aliases.setter
    def aliases(self, value: List[str]) -> None:
        self._set(HostConfiguration.aliases.fget.__name__, value)

    @property
    def ssh_user(self) -> str:
        return self._get(HostConfiguration.ssh_user.fget.__name__)

    @ssh_user.setter
    def ssh_user(self, value: str) -> None:
        self._set(HostConfiguration.ssh_user.fget.__name__, value)

    @property
    def ssh_address(self) -> str:
        return self._get(HostConfiguration.ssh_address.fget.__name__)

    @ssh_address.setter
    def ssh_address(self, value: str) -> None:
        self._set(HostConfiguration.ssh_address.fget.__name__, value)

    @property
    def ssh_port(self) -> int:
        return self._get(HostConfiguration.ssh_port.fget.__name__)

    @ssh_port.setter
    def ssh_port(self, value: int) -> None:
        self._set(HostConfiguration.ssh_port.fget.__name__, value)

    @property
    def ssh_key(self) -> Path:
        return self._get(HostConfiguration.ssh_key.fget.__name__)

    @ssh_key.setter
    def ssh_key(self, value: Path) -> None:
        self._set(HostConfiguration.ssh_key.fget.__name__, value)
