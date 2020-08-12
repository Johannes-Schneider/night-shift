import logging
from abc import ABC, abstractmethod
from typing import List


class CommandExecutor(ABC):

    def _log_response(self, header: str, command: str, response: List[str]) -> None:
        response_lines: str = "<NEW LINE>".join(response) if len(response) > 0 else "<NO RESPONSE>"
        logging.debug(f"[{self.__class__.__name__}] {header}: <COMMAND> {command} <RESPONSE> {response_lines}")

    @abstractmethod
    @property
    def is_closed(self) -> bool:
        raise NotImplementedError

    @abstractmethod
    def execute(self, command: str) -> List[str]:
        raise NotImplementedError

    @abstractmethod
    def close(self) -> None:
        raise NotImplementedError
