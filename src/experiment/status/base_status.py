from abc import ABC, abstractmethod


class BaseStatus(ABC):

    @abstractmethod
    def is_done(self) -> bool:
        raise NotImplementedError
