import logging
from abc import ABC, abstractmethod
from typing import List


class BaseCommandExecutor(ABC):

    @abstractmethod
    def execute(self, command: str) -> List[str]:
        raise NotImplementedError

    @staticmethod
    def _log_response(header: str, command: str, response: List[str]) -> None:
        response_as_string: str = "<new line>".join(response) if len(response) > 0 else "<no response>"
        logging.debug(f"{header}: {command} >> {response_as_string}")

    @abstractmethod
    def close(self) -> None:
        raise NotImplementedError
