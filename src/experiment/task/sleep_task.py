from datetime import timedelta, datetime
from typing import Any

from src.experiment.status.base_status import BaseStatus
from src.experiment.task.base_task import BaseTask
from src.utility import to_timespan


class SleepTask(BaseTask):
    class Status(BaseStatus):

        def __init__(self, done_after: timedelta):
            self._end: datetime = datetime.now() + done_after

        def is_done(self) -> bool:
            return datetime.now() >= self._end

    @staticmethod
    def type() -> str:
        return "sleep"

    def _validate_parameters(self) -> None:
        self._validate_parameter("time", str)

    def execute(self, experiment: Any) -> BaseStatus:
        return SleepTask.Status(to_timespan(experiment.parameters.resolve(self.host, self.parameters["time"])))
