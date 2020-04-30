import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Callable, Optional, Pattern

from src.experiment.configurable import Configurable
from src.experiment.status.base_status import BaseStatus
from src.utility import to_bool


class BaseTask(Configurable, ABC):

    @staticmethod
    def sub_task_factory() -> Dict[str, Callable[[str, Dict[str, Any]], "BaseTask"]]:
        from src.experiment.task.bash_task import BashTask
        from src.experiment.task.echo_task import EchoTask
        from src.experiment.task.mkdir_task import MkDirTask
        from src.experiment.task.screen_task import ScreenTask
        from src.experiment.task.sleep_task import SleepTask

        return {
            BashTask.type(): BashTask,
            EchoTask.type(): EchoTask,
            MkDirTask.type(): MkDirTask,
            ScreenTask.type(): ScreenTask,
            SleepTask.type(): SleepTask,
        }

    @staticmethod
    def try_create(host: str, properties: Dict[str, Any]) -> Optional["BaseTask"]:
        if "type" not in properties:
            return None

        factory: Dict[str, Callable[[str, Dict[str, Any]], "BaseTask"]] = BaseTask.sub_task_factory()

        if properties["type"] not in factory:
            logging.warning(f"\"{properties['type']}\" is not a known TaskType. Task will be ignored.")
            return None

        return factory[properties["type"]](host, properties)

    @staticmethod
    @abstractmethod
    def type() -> str:
        raise NotImplementedError

    def __init__(self, host: str, properties: Dict[str, Any]):
        super().__init__(properties)
        self._host: str = host

        self._validate_parameters()

    def _initialize_cache(self):
        self._fill_cache("ssh", to_bool, True)
        self._fill_cache("parameters")

    @abstractmethod
    def _validate_parameters(self) -> None:
        raise NotImplementedError

    def _validate_parameter(self,
                            parameter_name: str,
                            parameter_type: Any,
                            pattern: Optional[Pattern[str]] = None) -> None:
        if parameter_name not in self.parameters:
            raise Exception(f"Parameter \"{parameter_name}\" missing for task \"{self.type()}\"!")

        if not isinstance(self.parameters[parameter_name], parameter_type):
            raise Exception(f"Parameter \"{parameter_name}\" of \"{self.type()}\" task must be of type \"{parameter_type}\"!")

        if not pattern:
            return

        if not pattern.match(str(self.parameters[parameter_name])):
            raise Exception(f"Value of parameter \"{parameter_name}\" (\"{self.parameters[parameter_name]}\") must match \"{pattern}\"!")

    @property
    def host(self) -> str:
        return self._host

    @property
    def use_ssh(self) -> bool:
        return self._cached_property_value("ssh")

    @property
    def parameters(self) -> Dict[str, Any]:
        return self._cached_property_value("parameters")

    @abstractmethod
    def execute(self, experiment: Any) -> BaseStatus:
        raise NotImplementedError
