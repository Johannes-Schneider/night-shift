from typing import List

from src.experiment.status.base_status import BaseStatus


class AwaitAllStatus(BaseStatus):

    def __init__(self, status: List[BaseStatus]):
        self._status: List[BaseStatus] = status

    def is_done(self) -> bool:
        new_status: List[BaseStatus] = []
        for status in self._status:
            if not status.is_done():
                new_status.append(status)

        self._status = new_status
        return len(self._status) == 0
