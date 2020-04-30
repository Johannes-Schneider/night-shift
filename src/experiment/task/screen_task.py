from datetime import timedelta, datetime
from typing import Any, List

from src import utility
from src.command.base_command_executor import BaseCommandExecutor
from src.experiment.task.base_task import BaseTask
from src.experiment.status.base_status import BaseStatus
from src.experiment.status.done_status import DoneStatus
from src.utility import assert_is_experiment, to_bool, to_timespan


class ScreenTask(BaseTask):
    class Status(BaseStatus):

        def __init__(self, cmd: BaseCommandExecutor, screen_name: str, check_interval: str, timeout: str):
            self._cmd: BaseCommandExecutor = cmd
            self._screen_name: str = screen_name
            self._is_done: bool = False
            self._check_interval: timedelta = to_timespan(check_interval)
            self._force_quit: datetime = datetime.now() + to_timespan(timeout)
            self._next_check: datetime = datetime.now()

        def is_done(self) -> bool:
            now: datetime = datetime.now()

            if self._is_done or now < self._next_check:
                return self._is_done

            response: List[str] = self._cmd.execute(f"screen -ls '{self._screen_name}' | grep '{self._screen_name}'")
            self._is_done = len(response) == 0
            self._next_check += self._check_interval

            if not self._is_done and now >= self._force_quit:
                self._cmd.execute(f"screen -X -S '{self._screen_name}' quit")
                self._is_done = True

            return self._is_done

    @staticmethod
    def type() -> str:
        return "screen"

    def _validate_parameters(self) -> None:
        self._validate_parameter("name", str)
        self._validate_parameter("command", str)
        self._validate_parameter("timeout", str, utility.STRING_TO_TIMESPAN_PATTERN)

    def execute(self, experiment: Any) -> BaseStatus:
        from src.experiment.experiment import Experiment
        experiment: Experiment = assert_is_experiment(experiment)

        name: str = experiment.parameters.resolve(self.host, self.parameters["name"])
        command: str = experiment.parameters.resolve(self.host, self.parameters["command"])
        wait_for_termination: bool = to_bool(self.parameters["wait-for-termination"]) if "wait-for-termination" in self.parameters else True
        check_termination_interval: str = self.parameters["check-termination-interval"] if "check-termination-interval" in self.parameters else "1m"
        timeout: str = self.parameters["timeout"]

        cmd: BaseCommandExecutor = experiment.get_command_executor(self)
        cmd.execute(f"screen -m -d -S '{name}' bash -c '{command}'")

        if not wait_for_termination:
            return DoneStatus()

        return ScreenTask.Status(cmd,
                                 name,
                                 experiment.parameters.resolve(self.host, check_termination_interval),
                                 experiment.parameters.resolve(self.host, timeout))
