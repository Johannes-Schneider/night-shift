import datetime
import re
import shutil
from pathlib import Path
from typing import Any, Dict, Callable, Pattern

STRING_TO_BOOL_CONVERTER: Dict[str, bool] = {"true": True,
                                             "yes": True,
                                             "1": True,
                                             "false": False,
                                             "no": False,
                                             "0": False}

STRING_TO_TIMESPAN_PATTERN: Pattern[str] = re.compile(
    r"^(?:(?P<Days>\d+)d)?(?:(?P<Hours>\d+)h)?(?:(?P<Minutes>\d+)m)?(:?(?P<Seconds>\d+)s)?$")


def mkdir(*args) -> Path:
    directory: Path = Path(*args)
    if directory.exists():
        shutil.rmtree(directory.absolute())

    directory.mkdir(parents=True, exist_ok=True)
    return directory


def to_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value

    if isinstance(value, int):
        return value > 0

    if not isinstance(value, str):
        return False

    string: str = value.lower()
    if string not in STRING_TO_BOOL_CONVERTER:
        return False

    return STRING_TO_BOOL_CONVERTER[string]


def to_timespan(value: Any) -> datetime.timedelta:
    if isinstance(value, datetime.timedelta):
        return value

    if isinstance(value, int):
        return datetime.timedelta(seconds=value)

    if not isinstance(value, str):
        raise Exception(f"Unable to convert \"{value}\" to timespan!")

    match = STRING_TO_TIMESPAN_PATTERN.match(value)
    if not match:
        raise Exception(f"\"{value}\" does is not a valid timespan!")

    value_of: Callable[[str], int] = lambda name: int(match.group(name)) if match.group(name) else 0

    return datetime.timedelta(days=value_of("Days"),
                              hours=value_of("Hours"),
                              minutes=value_of("Minutes"),
                              seconds=value_of("Seconds"))


def assert_is_experiment(experiment: Any) -> Any:
    from src.experiment.experiment import Experiment
    assert isinstance(experiment, Experiment)
    return experiment
