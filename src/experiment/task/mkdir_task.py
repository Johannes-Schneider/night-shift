from typing import Dict, Any

from src.command.base_command_executor import BaseCommandExecutor
from src.experiment.task.base_task import BaseTask
from src.experiment.status.base_status import BaseStatus
from src.experiment.status.done_status import DoneStatus
from src.utility import assert_is_experiment, to_bool


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

        clean: bool = to_bool(self.parameters["clean"]) if "clean" in self.parameters else True

        cmd: BaseCommandExecutor = experiment.get_command_executor(self)
        for unresolved_path in self.parameters["paths"]:
            resolved_path: str = experiment.parameters.resolve(self.host, unresolved_path)
            command: str = f"mkdir -p {resolved_path}"
            if clean:
                command += f" && rm -rf {resolved_path}/*"

            cmd.execute(command)

        return DoneStatus()
