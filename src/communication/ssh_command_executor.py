import logging
from pathlib import Path
from typing import List, Optional

from pexpect.pxssh import pxssh

from src.communication.command_executor import CommandExecutor
from src.communication.command_executor_factory import CommandExecutorFactory


class SSHCommandExecutor(CommandExecutor):
    class Factory(CommandExecutorFactory):

        def __init__(self, user: str, address: str, port: int, key: Path):
            self._user: str = user
            self._address: str = address
            self._port: int = port
            self._key: Path = key

        def new_command_executor(self) -> CommandExecutor:
            return SSHCommandExecutor(self._user, self._address, self._port, self._key)

    @staticmethod
    def try_connect(user: str, address: str, port: int, key: Path) -> Optional["SSHCommandExecutor"]:
        try:
            return SSHCommandExecutor(user, address, port, key)

        except ConnectionError:
            return None

    def __init__(self, user: str, address: str, port: int, key: Path):
        self._log_header: str = f"{user}@{address}:{port}"
        self._session: pxssh = pxssh()

        if not self._session.login(address, username=user, port=port, ssh_key=str(key.expanduser().absolute())):
            raise ConnectionError(f"Unable to establish SSH connection to {user}@{address}:{port}!")

        self._test_connection()

        logging.debug(f"[{self.__class__.__name__}]: Connection to {self._log_header} established.")

    def _test_connection(self) -> None:
        echo_response: List[str] = self.execute("echo Hello from Night-Shift!")
        if len(echo_response) != 1 or echo_response[0] != "Hello from Night-Shift!":
            raise ConnectionError(f"[{self.__class__.__name__}] {self._log_header}: Connection test failed!")

    @property
    def is_closed(self) -> bool:
        return self._session.closed

    def execute(self, command: str) -> List[str]:
        try:
            self._session.sendline(command)
            self._session.prompt()

            response: List[str] = self._session.before.decode("utf-8").split("\r\n")[1:]
            self._log_response(self._log_header, command, response)
            return response

        except BaseException as exception:
            logging.error(f"[{self.__class__.__name__}] {self._log_header}: Exception while sending command <COMMAND> {command} <EXCEPTION> {exception}")

    def close(self) -> None:
        self._session.close()
        logging.debug(f"[{self.__class__.__name__}] {self._log_header}: Connection closed.")
