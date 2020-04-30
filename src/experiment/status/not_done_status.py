from src.experiment.status.base_status import BaseStatus


class NotDoneStatus(BaseStatus):

    def is_done(self) -> bool:
        return False
