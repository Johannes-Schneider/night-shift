import logging
from typing import List

from pexpect import pxssh

from src.command.base_command_executor import BaseCommandExecutor


class SSHCommandExecutor(BaseCommandExecutor):

    def __init__(self, host: str, user: str):
        self._host: str = host
        self._user: str = user
        self._ssh_session: pxssh.pxssh = pxssh.pxssh()
        if not self._ssh_session.login(host, user):
            raise Exception(f"Unable to login to \"{host}\"!")

        logging.debug(f"SSH -> {self._user}@{self._host}: Logged in.")

    def execute(self, command: str) -> List[str]:
        self._ssh_session.sendline(command)
        self._ssh_session.prompt()

        response: List[str] = list(filter(None, self._ssh_session.before.decode("utf-8").split("\r\n")[1:]))
        self._log_response(f"SSH -> {self._user}@{self._host}", command, response)

        return response

    def close(self) -> None:
        logging.debug(f"SSH -> {self._user}@{self._host}: Close.")
        self._ssh_session.close()
