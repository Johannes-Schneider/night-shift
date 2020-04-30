import json
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

from src.command.base_command_executor import BaseCommandExecutor
from src.command.dummy_command_executor import DummyCommandExecutor
from src.command.local_command_executor import LocalCommandExecutor
from src.command.ssh_command_executor import SSHCommandExecutor
from src.experiment.configurable import Configurable
from src.experiment.parameters import Parameters
from src.experiment.phase import Phase
from src.experiment.status.base_status import BaseStatus
from src.experiment.status.done_status import DoneStatus
from src.experiment.status.not_done_status import NotDoneStatus
from src.experiment.task.base_task import BaseTask


class Experiment(Configurable):
    class Runner(Configurable):

        _pause_until: Optional[datetime] = None
        _log_pause: bool = False

        @staticmethod
        def pause(until: datetime) -> None:
            if datetime.now() >= until:
                return

            Experiment.Runner._pause_until = until
            Experiment.Runner._log_pause = True
            logging.info(f"Pause until {until} scheduled.")

        @staticmethod
        def resume() -> None:
            Experiment.Runner._pause_until = None

        def __init__(self, experiment: "Experiment", properties: Dict[str, Any]):
            super().__init__(properties)
            self._experiment: "Experiment" = experiment
            self._current_run: int = 0
            self._current_pipeline: List[str] = []
            self._current_phase_status: Optional[BaseStatus] = None

        def _initialize_cache(self):
            self._fill_cache("repeat", lambda value: int(value), 1)
            self._fill_cache("pipeline", lambda value: list(value))

        @property
        def runs(self) -> int:
            return self._cached_property_value("repeat")

        @property
        def pipeline(self) -> List[str]:
            return self._cached_property_value("pipeline")

        def run(self) -> BaseStatus:
            if not self._current_phase_is_done():
                return NotDoneStatus()

            if self._try_start_next_phase():
                return NotDoneStatus()

            return DoneStatus()

        def _current_phase_is_done(self) -> bool:
            if self._current_phase_status is None:
                return True

            return self._current_phase_status.is_done()

        def _try_start_next_phase(self) -> bool:
            if len(self._current_pipeline) == 0:
                self._current_run += 1
                self._current_pipeline = [phase_name for phase_name in self.pipeline]

            if self._pause_until and datetime.now() < self._pause_until:
                if self._log_pause:
                    logging.info(f"EXPERIMENT {self._experiment.name} ({self._current_run} / {self.runs}): Paused until {self._pause_until}")
                    self._log_pause = False

                return True

            if self._current_run > self.runs or len(self._current_pipeline) == 0:
                return False

            next_phase: Phase = self._experiment.phases[self._current_pipeline.pop(0)]
            logging.info(f"EXPERIMENT {self._experiment.name} ({self._current_run} / {self.runs}): {next_phase.name}")
            self._current_phase_status = next_phase.run()
            return True

    def __init__(self, experiment_file: Path):
        with experiment_file.open("r") as input_file:
            super().__init__(json.load(input_file))

        self._ssh_connections: Dict[str, SSHCommandExecutor] = {}

    def _initialize_cache(self):
        self._fill_cache("name")
        self._fill_cache("hosts", lambda value: list(value))
        self._fill_cache("parameters", lambda value: Parameters(self, value))
        self._fill_cache("phases", lambda value: {config["name"]: Phase(self, config) for config in value})
        self._fill_cache("run", lambda value: Experiment.Runner(self, value))

    @property
    def name(self) -> str:
        return self._cached_property_value("name")

    @property
    def hosts(self) -> List[str]:
        return self._cached_property_value("hosts")

    @property
    def parameters(self) -> Parameters:
        return self._cached_property_value("parameters")

    @property
    def phases(self) -> Dict[str, Phase]:
        return self._cached_property_value("phases")

    @property
    def runner(self) -> "Experiment.Runner":
        return self._cached_property_value("run")

    def get_command_executor(self, task: BaseTask) -> BaseCommandExecutor:
        host: str = task.host
        return DummyCommandExecutor(task.use_ssh, self.parameters.value(host, "ssh-user"), host)

        if not task.use_ssh:
            return LocalCommandExecutor()

        if host not in self._ssh_connections:
            self._ssh_connections[host] = SSHCommandExecutor(host, self.parameters.value(host, "ssh-user"))

        return self._ssh_connections[host]

    def run(self) -> BaseStatus:
        return self.runner.run()
