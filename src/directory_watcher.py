import logging
from pathlib import Path
from queue import Queue
from threading import Thread
from time import sleep
from typing import Optional, Tuple, Union

from watchdog.events import PatternMatchingEventHandler, \
    DirCreatedEvent, FileCreatedEvent
from watchdog.observers import Observer


class DirectoryWatcher:
    class EventHandler(PatternMatchingEventHandler):

        def __init__(self, file_extensions: Optional[Tuple[str, ...]] = None):
            super().__init__()
            self._file_extensions: Tuple[str, ...] = file_extensions or (".zip", ".json")
            self._event_queue: "Queue[FileCreatedEvent]" = Queue()
            self._thread: Optional[Thread] = None

        def on_created(self, event: Union[DirCreatedEvent, FileCreatedEvent]) -> None:
            if not isinstance(event, FileCreatedEvent):
                return

            if not event.src_path.endswith(self._file_extensions):
                return

            logging.info(f"File \"{event.src_path}\" was just created.")
            self._event_queue.put(event)

        def start(self) -> None:
            if self._thread:
                self._thread.join()

            self._thread = Thread(target=DirectoryWatcher.EventHandler._sleep, daemon=True)
            self._thread.start()

        @staticmethod
        def _sleep() -> None:
            while True:
                sleep(1)

        @property
        def events(self) -> "Queue[FileCreatedEvent]":
            return self._event_queue

    def __init__(self, directory: Path, file_extensions: Optional[Tuple[str, ...]] = None):
        self._directory: Path = directory
        self._event_handler: DirectoryWatcher.EventHandler = DirectoryWatcher.EventHandler(file_extensions)
        self._observer: Observer = Observer()
        self._observer.schedule(self._event_handler, str(directory.absolute()))
        self._observer.start()

    def stop(self) -> None:
        self._observer.stop()

    @property
    def events(self) -> "Queue[FileCreatedEvent]":
        return self._event_handler.events
