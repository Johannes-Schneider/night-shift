import re
import shutil
from datetime import datetime, timedelta
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

STRING_TO_DATE_TIME_PATTERN: Pattern[str] = re.compile(r"^(?P<Date>(?P<Year>\d{4})[-/\s](?P<Month>\d{1,2})[-/\s](?P<Day>\d{1,2})\s?)?"
                                                       r"(?P<Time>(?P<Hour>\d{1,2})[-/:](?P<Minute>\d{1,2})(:?[-/:](?P<Second>\d{1,2}))?)?$")


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


def to_timespan(value: Any) -> timedelta:
    if isinstance(value, timedelta):
        return value

    if isinstance(value, int):
        return timedelta(seconds=value)

    if not isinstance(value, str):
        raise Exception(f"Unable to convert \"{value}\" to timespan!")

    match = STRING_TO_TIMESPAN_PATTERN.match(value)
    if not match:
        raise Exception(f"\"{value}\" is not a valid timespan!")

    value_of: Callable[[str], int] = lambda name: int(match.group(name)) if match.group(name) else 0

    return timedelta(days=value_of("Days"),
                     hours=value_of("Hours"),
                     minutes=value_of("Minutes"),
                     seconds=value_of("Seconds"))


def to_datetime(value: Any) -> datetime:
    if isinstance(value, datetime):
        return value

    if not isinstance(value, str):
        raise Exception(f"Unable to convert \"{value}\" to datetime!")

    match = STRING_TO_DATE_TIME_PATTERN.match(value)
    if not match:
        raise Exception(f"\"{value}\" is not a valid datetime!")

    value_of: Callable[[str, int], int] = lambda name, default: int(match.group(name)) if match.group(name) else default

    now: datetime = datetime.now()
    return datetime(year=value_of("Year", now.year),
                    month=value_of("Month", now.month),
                    day=value_of("Day", now.day),
                    hour=value_of("Hour", 0),
                    minute=value_of("Minute", 0),
                    second=value_of("Second", 0))


def assert_is_experiment(experiment: Any) -> Any:
    from src.experiment.experiment import Experiment
    assert isinstance(experiment, Experiment)
    return experiment
