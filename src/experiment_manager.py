import logging
import os
import shutil
from pathlib import Path
from typing import List, Any, Callable, Dict, Optional
from zipfile import ZipFile

from src.experiment.experiment import Experiment
from src.utility import mkdir


class ExperimentManager:

    def __init__(self):
        self._experiment_queue: List[Any] = []
        self._unpack_directory: Path = mkdir("./.unpack/")
        self._enqueue_handlers: Dict[str, Callable[[Path], None]] = {".zip": self._enqueue_zip,
                                                                     ".experiment": self._enqueue_experiment}

        self._current_experiment: Optional[Experiment] = None

    def enqueue(self, deployment_file: Path) -> None:
        file_extension: str = deployment_file.suffix

        try:
            if file_extension not in self._enqueue_handlers:
                logging.error(f"Unable to enqueue \"{deployment_file.absolute()}\": "
                              f"File extension \"{file_extension}\" is not supported!")
                return

            self._enqueue_handlers.get(file_extension)(deployment_file)
        except BaseException as exception:
            logging.error(f"Unable to enqueue \"{deployment_file.absolute()}\":"
                          f"{exception}")

        finally:
            os.remove(str(deployment_file.absolute()))

    def _enqueue_zip(self, deployment_file: Path) -> None:
        file_name: str = deployment_file.stem
        unpack_dir: Path = mkdir(self._unpack_directory, file_name)

        with ZipFile(str(deployment_file.absolute()), "r") as zip_file:
            zip_file.extractall(str(unpack_dir.absolute()))

        logging.info(f"ZIP: Successfully unpacked experiment.")
        self._try_extract_experiment(unpack_dir)

    def _enqueue_experiment(self, deployment_file: Path) -> None:
        file_name: str = deployment_file.stem
        tmp_dir: Path = mkdir(self._unpack_directory, file_name)
        shutil.copy(str(deployment_file.absolute()), str(tmp_dir.absolute()))

        logging.info(f"EXPERIMENT: Successfully unpacked experiment.")
        self._try_extract_experiment(tmp_dir)

    def _try_extract_experiment(self, experiment_dir: Path) -> None:
        for experiment_file in experiment_dir.glob("*.experiment"):
            experiment: Experiment = Experiment(experiment_file)
            self._experiment_queue.append(experiment)
            logging.info(f"Successfully enqueued {experiment.name}.")

        shutil.rmtree(str(experiment_dir.absolute()))

    @property
    def current_experiment(self) -> Optional[Experiment]:
        return self._current_experiment

    def run(self) -> None:
        if self._current_experiment is None and len(self._experiment_queue) > 0:
            self._current_experiment = self._experiment_queue.pop(0)

        if self._current_experiment is None:
            return

        if self._current_experiment.run().is_done():
            self._current_experiment.tear_down()
            self._current_experiment = None
