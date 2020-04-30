from src.experiment.status.base_status import BaseStatus


class DoneStatus(BaseStatus):

    def is_done(self) -> bool:
        return True
