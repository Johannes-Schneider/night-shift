from typing import Any

from src.command.base_command_executor import BaseCommandExecutor
from src.experiment.task.base_task import BaseTask
from src.experiment.status.base_status import BaseStatus
from src.experiment.status.done_status import DoneStatus
from src.utility import assert_is_experiment


class BashTask(BaseTask):

    @staticmethod
    def type() -> str:
        return "bash"

    def _validate_parameters(self) -> None:
        self._validate_parameter("command", str)

    def execute(self, experiment: Any) -> BaseStatus:
        from src.experiment.experiment import Experiment
        experiment: Experiment = assert_is_experiment(experiment)

        cmd: BaseCommandExecutor = experiment.get_command_executor(self)
        cmd.execute(experiment.parameters.resolve(self.host, self.parameters["command"]))

        return DoneStatus()
