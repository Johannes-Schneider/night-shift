from typing import Dict, Any

from src.command.base_command_executor import BaseCommandExecutor
from src.experiment.task.base_task import BaseTask
from src.experiment.status.base_status import BaseStatus
from src.experiment.status.done_status import DoneStatus
from src.utility import assert_is_experiment


class MkDirTask(BaseTask):

    @staticmethod
    def type() -> str:
        return "mkdir"

    def __init__(self, host: str, properties: Dict[str, Any]):
        super().__init__(host, properties)

    def _validate_parameters(self) -> None:
        self._validate_parameter("paths", list)

    def execute(self, experiment: Any) -> BaseStatus:
        from src.experiment.experiment import Experiment
        experiment: Experiment = assert_is_experiment(experiment)

        cmd: BaseCommandExecutor = experiment.get_command_executor(self)
        for unresolved_path in self.parameters["paths"]:
            resolved_path: str = experiment.parameters.resolve(self.host, unresolved_path)
            cmd.execute(f"mkdir -p {resolved_path} && rm -rf {resolved_path}/*")

        return DoneStatus()
