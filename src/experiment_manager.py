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
                                                                     ".json": self._enqueue_json}

        self._current_experiment: Optional[Experiment] = None

    def enqueue(self, deployment_file: Path) -> None:
        file_extension: str = deployment_file.suffix

        try:
            self._enqueue_handlers.get(file_extension)(deployment_file)
        except KeyError:
            logging.error(f"Unable to enqueue \"{deployment_file.absolute()}\": "
                          f"File extension \"{file_extension}\" is not supported!")
        except BaseException as exception:
            logging.error(f"Unable to enqueue \"{deployment_file.absolute()}\":"
                          f"{exception}")

        os.remove(str(deployment_file.absolute()))

    def _enqueue_zip(self, deployment_file: Path) -> None:
        file_name: str = deployment_file.stem
        unpack_dir: Path = mkdir(self._unpack_directory, file_name)

        with ZipFile(str(deployment_file.absolute()), "r") as zip_file:
            zip_file.extractall(str(unpack_dir.absolute()))

        logging.info(f"ZIP: Successfully unpacked experiment.")
        self._try_extract_experiment(unpack_dir)

    def _enqueue_json(self, deployment_file: Path) -> None:
        file_name: str = deployment_file.stem
        tmp_dir: Path = mkdir(self._unpack_directory, file_name)
        shutil.copy(str(deployment_file.absolute()), str(tmp_dir.absolute()))

        logging.info(f"JSON: Successfully unpacked experiment.")
        self._try_extract_experiment(tmp_dir)

    def _try_extract_experiment(self, experiment_dir: Path) -> None:
        experiment_configuration: Path = Path(experiment_dir, "experiment.json")
        if not experiment_configuration.exists():
            raise Exception(f"Expected \"{experiment_configuration.absolute()}\" to exist, but it doesnt.")

        experiment: Experiment = Experiment(experiment_configuration)
        self._experiment_queue.append(experiment)

        shutil.rmtree(str(experiment_dir.absolute()))
        logging.info(f"Successfully enqueued {experiment.name}.")

    def run(self) -> None:
        if self._current_experiment is None and len(self._experiment_queue) > 0:
            self._current_experiment = self._experiment_queue.pop(0)

        if self._current_experiment is None:
            return

        if self._current_experiment.run().is_done():
            self._current_experiment = None
