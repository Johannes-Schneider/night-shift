import logging
from pathlib import Path
from time import sleep
from typing import Tuple

from watchdog.events import FileSystemEvent

from src.directory_watcher import DirectoryWatcher
from src.experiment_manager import ExperimentManager
from src.utility import mkdir

SUPPORTED_FILE_EXTENSION: Tuple[str, ...] = (".zip", ".json")


def main():
    logging.basicConfig(format="%(asctime)s : %(levelname)s : %(message)s", level=logging.INFO)

    deployment_directory: Path = mkdir("./deploy/")

    watcher: DirectoryWatcher = DirectoryWatcher(deployment_directory, SUPPORTED_FILE_EXTENSION)

    logging.info(f"Ready to queue deployments.")
    logging.info(f"Please deploy to \"{deployment_directory.absolute()}\".")
    logging.info(f"Supported file extension are {SUPPORTED_FILE_EXTENSION}.")

    experiment_manager: ExperimentManager = ExperimentManager()

    while True:
        try:
            while not watcher.events.empty():
                event: FileSystemEvent = watcher.events.get()
                experiment_manager.enqueue(Path(event.src_path))

            experiment_manager.run()
            sleep(1)
        except KeyboardInterrupt:
            watcher.stop()
            break


if __name__ == "__main__":
    main()
