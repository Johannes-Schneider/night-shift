from typing import Any

from src.command.base_command_executor import BaseCommandExecutor
from src.experiment.status.base_status import BaseStatus
from src.experiment.status.done_status import DoneStatus
from src.experiment.task.base_task import BaseTask
from src.utility import assert_is_experiment, to_bool


class EchoTask(BaseTask):

    @staticmethod
    def type() -> str:
        return "echo"

    def _validate_parameters(self) -> None:
        self._validate_parameter("file", str)
        self._validate_parameter("lines", list)

    def execute(self, experiment: Any) -> BaseStatus:
        from src.experiment.experiment import Experiment
        experiment: Experiment = assert_is_experiment(experiment)

        overwrite: bool = to_bool(self.parameters["overwrite"]) if "overwrite" in self.parameters else False
        file: str = experiment.parameters.resolve(self.host, self.parameters["file"])
        lines: str = experiment.parameters.resolve(self.host, list(self.parameters["lines"]))
        operator: str = ">" if overwrite else ">>"

        cmd: BaseCommandExecutor = experiment.get_command_executor(self)
        is_first: bool = True
        for line in lines:
            if not is_first:
                operator = ">>"

            cmd.execute(f"echo \"{line}\" {operator} {file}")
            is_first = False

        return DoneStatus()
