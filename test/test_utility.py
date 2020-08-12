import os
from pathlib import Path
from typing import Callable, TextIO, List


def with_temporary_files(test_function: Callable[[List[Path], List[TextIO]], None], number_of_files: int = 1) -> None:
    paths: List[Path] = [Path(f"./.__temp_file_{file_number}__").expanduser().absolute() for file_number in range(number_of_files)]
    ios: List[TextIO] = [path.open("w+") for path in paths]
    try:
        for path in paths:
            if not path.exists():
                raise AssertionError(f"The newly created (temporary) file \"{path.expanduser().absolute()}\" does not exist!")
            if not path.is_file():
                raise AssertionError(f"The newly created (temporary) file \"{path.expanduser().absolute()}\" is not actually a file!")

            test_function(paths, ios)

    finally:
        for io in ios:
            io.close()

        for path in paths:
            os.remove(str(path))


def with_temporary_directories(test_function: Callable[[List[Path]], None], number_of_directories: int = 1) -> None:
    paths: List[Path] = [Path(f"./.__temp_directory_{directory_number}__/").expanduser().absolute() for directory_number in range(number_of_directories)]
    try:
        for path in paths:
            path.mkdir(parents=True, exist_ok=True)
            if not path.exists():
                raise AssertionError(f"The newly created (temporary) directory \"{path.expanduser().absolute()}\" does not exist!")
            if not path.is_dir():
                raise AssertionError(f"The newly created (temporary) directory \"{path.expanduser().absolute()}\" is not actually a directory!")

            test_function(paths)

    finally:
        for path in paths:
            os.removedirs(str(path))


def with_absent_files(test_function: Callable[[List[Path]], None], number_of_files: int = 1) -> None:
    paths: List[Path] = [Path(f"./.__temp_file_{file_number}__").expanduser().absolute() for file_number in range(number_of_files)]
    for path in paths:
        if path.exists():
            os.remove(str(path))

        if path.exists():
            raise AssertionError(f"The newly deleted (temporary) file \"{path.expanduser().absolute()}\" does still exist!")

        test_function(paths)


def with_absent_directories(test_function: Callable[[List[Path]], None], number_of_directories: int = 1) -> None:
    paths: List[Path] = [Path(f"./.__temp_directory_{directory_number}__/").expanduser().absolute() for directory_number in range(number_of_directories)]
    for path in paths:
        if path.exists():
            os.removedirs(str(path))

        if path.exists():
            raise AssertionError(f"The newly deleted (temporary) directory \"{path.expanduser().absolute()}\" does still exist!")

        test_function(paths)
