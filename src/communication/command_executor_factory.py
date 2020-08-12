from abc import ABC, abstractmethod

from src.communication.command_executor import CommandExecutor


class CommandExecutorFactory(ABC):

    @abstractmethod
    def new_command_executor(self) -> CommandExecutor:
        raise NotImplementedError
