from typing import Dict, Any, List

from src.experiment.configurable import Configurable
from src.experiment.status.await_all_status import AwaitAllStatus
from src.experiment.status.base_status import BaseStatus
from src.experiment.task.base_task import BaseTask
from src.utility import assert_is_experiment


class Phase(Configurable):
    def __init__(self, experiment: Any, properties: Dict[str, Any]):
        from src.experiment.experiment import Experiment
        self._experiment: Experiment = assert_is_experiment(experiment)

        super().__init__(properties)

        self._common_tasks: Dict[str, List[BaseTask]] = {}
        self._specific_tasks: Dict[str, List[BaseTask]] = {}

        self._initialize_tasks()

    def _initialize_cache(self):
        self._fill_cache("name")
        self._fill_cache("do")

    @property
    def name(self) -> str:
        return self._cached_property_value("name")

    @property
    def do(self) -> Dict[str, Any]:
        return self._cached_property_value("do")

    def _initialize_tasks(self) -> None:
        self._initialize_common_tasks()
        self._initialize_specific_tasks()

    def _initialize_common_tasks(self) -> None:
        tasks: List[Dict[str, Any]] = []
        if "common" in self.do:
            tasks = self.do["common"]

        for host in self._experiment.hosts:
            self._common_tasks[host] = self._create_tasks(host, tasks)

    def _initialize_specific_tasks(self) -> None:
        tasks: List[Dict[str, Any]] = []
        if "specific" in self.do:
            tasks = self.do["specific"]

        for properties in tasks:
            if "hosts" not in properties:
                continue

            for host in properties["hosts"]:
                if host not in self._specific_tasks:
                    self._specific_tasks[host] = []

                self._specific_tasks[host] += self._create_tasks(host, [properties])

    @staticmethod
    def _create_tasks(host: str, task_properties: List[Dict[str, Any]]) -> List[BaseTask]:
        tasks: List[BaseTask] = []
        for properties in task_properties:
            task: BaseTask = BaseTask.try_create(host, properties)
            if not task:
                continue

            tasks.append(task)

        return tasks

    def run(self) -> BaseStatus:
        status: List[BaseStatus] = self._run_tasks(self._common_tasks) + self._run_tasks(self._specific_tasks)
        return AwaitAllStatus(status)

    def _run_tasks(self, tasks: Dict[str, List[BaseTask]]) -> List[BaseStatus]:
        status: List[BaseStatus] = []
        for host in tasks:
            for task in tasks[host]:
                status.append(task.execute(self._experiment))

        return status
