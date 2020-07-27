import logging
from pathlib import Path
from typing import Any, List, Dict


class PartialConfigurationFactory:

    def __init__(self):
        raise NotImplementedError

    @staticmethod
    def to_lower(properties: Dict[str, Any]) -> Dict[str, Any]:
        return {key.lower(): properties[key] for key in properties}

    @staticmethod
    def assert_is_str(config_class: type, property_name: str, property_value: Any) -> str:
        if property_value is None:
            logging.error(f"Property \"{property_name}\" of \"{config_class.__name__}\" must not be None!")
            raise Exception

        if not isinstance(property_value, str):
            logging.error(f"Property \"{property_name}\" of \"{config_class.__name__}\" must be of type string!")
            raise TypeError

        return str(property_value)

    @staticmethod
    def assert_is_int(config_class: type, property_name: str, property_value: Any) -> int:
        if property_value is None:
            logging.error(f"Property \"{property_name}\" of \"{config_class.__name__}\" must not be None!")
            raise Exception

        if not isinstance(property_value, int):
            logging.error(f"Property \"{property_name}\" of \"{config_class.__name__}\" must be of type integer!")
            raise TypeError

        return int(property_value)

    @staticmethod
    def assert_is_float(config_class: type, property_name: str, property_value: Any) -> float:
        if property_value is None:
            logging.error(f"Property \"{property_name}\" of \"{config_class.__name__}\" must not be None!")
            raise Exception

        if not isinstance(property_value, float):
            logging.error(f"Property \"{property_name}\" of \"{config_class.__name__}\" must be of type float!")
            raise TypeError

        return float(property_value)

    @staticmethod
    def assert_is_existing_file(config_class: type, property_name: str, property_value: Any) -> Path:
        path: Path = Path(PartialConfigurationFactory.assert_is_str(config_class, property_name, property_value))

        if not path.exists() or not path.is_file():
            logging.error(f"Property \"{property_name}\" of \"{config_class.__name__}\" must be an existing file!")
            raise Exception

        return path

    @staticmethod
    def assert_is_list_of_str(config_class: type, property_name: str, property_value: Any) -> List[str]:
        if property_value is None:
            logging.error(f"Property \"{property_name}\" of \"{config_class.__name__}\" must not be None!")
            raise Exception

        if not isinstance(property_value, list):
            logging.error(f"Property \"{property_name}\" of \"{config_class.__name__}\" must be of type list<string>!")
            raise TypeError

        for value in property_value:
            if value is None or not isinstance(value, str):
                logging.error(f"Property \"{property_name}\" of \"{config_class.__name__}\" must be of type list<string>!")
                raise TypeError

        return list(property_value)
