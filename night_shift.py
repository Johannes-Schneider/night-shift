import logging
from datetime import datetime
from pathlib import Path
from queue import Queue
from threading import Thread
from time import sleep
from typing import Tuple, Optional, List

from watchdog.events import FileSystemEvent

from src.directory_watcher import DirectoryWatcher
from src.experiment.experiment import Experiment
from src.experiment_manager import ExperimentManager
from src.utility import mkdir, to_datetime, to_timespan

SUPPORTED_FILE_EXTENSION: Tuple[str, ...] = (".zip", ".experiment")
PAUSE_UNTIL: Optional[datetime] = None


def main():
    logging.basicConfig(format="%(asctime)s : %(levelname)s : %(message)s", level=logging.INFO)

    deployment_directory: Path = mkdir("./deploy/")

    watcher: DirectoryWatcher = DirectoryWatcher(deployment_directory, SUPPORTED_FILE_EXTENSION)

    logging.info(f"Ready to queue deployments.")
    logging.info(f"Please deploy to \"{deployment_directory.absolute()}\".")
    logging.info(f"Supported file extension are {SUPPORTED_FILE_EXTENSION}.")

    experiment_manager: ExperimentManager = ExperimentManager()

    input_queue: Queue = Queue()
    input_thread: Thread = Thread(target=_read_from_stdin, args=(input_queue,), daemon=True)
    input_thread.start()

    while True:
        try:
            while not watcher.events.empty():
                event: FileSystemEvent = watcher.events.get()
                experiment_manager.enqueue(Path(event.src_path))

            if not input_queue.empty():
                line: str = input_queue.get()
                if line == "exit":
                    break

                _process_input(line, experiment_manager)

            experiment_manager.run()
            sleep(1)
        except KeyboardInterrupt:
            break

    watcher.stop()
    input_thread.join()


def _process_input(line: str, experiment_manager: ExperimentManager) -> None:
    try:
        keyword, arguments = _extract_next_keyword(line)

        if keyword == "pause":
            _pause(arguments, experiment_manager)
            return

        if keyword == "resume":
            _resume(line, experiment_manager)
            return

        logging.error(f"Unknown keyword: \"{keyword}\"!")

    except BaseException as exception:
        logging.error(f"Unable to process input: {exception}!")


def _pause(line: str, experiment_manager: ExperimentManager) -> None:
    keyword, arguments = _extract_next_keyword(line)
    until: Optional[datetime] = None
    if keyword == "until":
        until = to_datetime(arguments)
    elif keyword == "for":
        until = datetime.now() + to_timespan(arguments)

    if until is None:
        return

    Experiment.Runner.pause(until)


def _resume(line: str, experiment_manager: ExperimentManager) -> None:
    Experiment.Runner.resume()


def _extract_next_keyword(line: str) -> Tuple[str, str]:
    split: List[str] = line.split(" ")
    if len(split) >= 2:
        return split[0], " ".join(split[1:])

    if len(split) >= 1:
        return split[0], ""

    return "", ""


def _read_from_stdin(queue: Queue) -> None:
    while True:
        try:
            line: str = input()
            if not line:
                continue

            queue.put(line)

            if line == "exit":
                break

        except KeyboardInterrupt:
            break


if __name__ == "__main__":
    main()
