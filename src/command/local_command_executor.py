import os
from io import TextIOWrapper
from typing import List

from src.command.base_command_executor import BaseCommandExecutor


class LocalCommandExecutor(BaseCommandExecutor):

    def execute(self, command: str) -> List[str]:
        output_stream: TextIOWrapper = os.popen(command)

        response: List[str] = output_stream.read().split("\r\n")
        self._log_response("BASH", command, response)

        return response

    def close(self) -> None:
        pass
