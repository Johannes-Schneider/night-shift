from typing import List, Optional

from src.command.base_command_executor import BaseCommandExecutor


class DummyCommandExecutor(BaseCommandExecutor):

    def __init__(self, emulate_ssh: bool, ssh_user: Optional[str] = None, ssh_host: Optional[str] = None):
        self._emulate_ssh: bool = emulate_ssh
        self._ssh_user: Optional[str] = ssh_user
        self._ssh_host: Optional[str] = ssh_host

    def execute(self, command: str) -> List[str]:
        header: str = "DUMMY"
        if self._emulate_ssh:
            header += f" SSH -> {self._ssh_user}@{self._ssh_host}"

        self._log_response(header, command, [])

        return []

    def close(self) -> None:
        pass
