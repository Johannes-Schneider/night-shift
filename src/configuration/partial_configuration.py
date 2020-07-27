import logging
from abc import ABC
from typing import Optional, Dict, Any


class PartialConfiguration(ABC):

    def __init__(self, parent: Optional["PartialConfiguration"] = None):
        self._parent: Optional[PartialConfiguration] = parent
        self._properties: Dict[str, Any] = {}

    def _register_property(self, property_name: str) -> Optional[Any]:
        if property_name in self._properties:
            logging.error(f"Trying to register a new property named \"{property_name}\" on \"{self.__class__.__name__}\" but the name is already in use!")
            raise Exception

        self._properties[property_name] = None
        return None

    def _get(self, property_name: str) -> Any:
        if property_name not in self._properties:
            logging.error(f"Trying to get value of property \"{property_name}\" in \"{self.__class__.__name__}\" but the property has not been registered!")
            raise Exception

        if self._properties[property_name] is not None:
            return self._properties[property_name]

        if self._parent:
            return self._parent._get(property_name)

        logging.error(f"Trying to get value of property \"{property_name}\" in \"{self.__class__.__name__}\" but the property has not been set!")
        raise Exception

    def _set(self, property_name: str, property_value: Any) -> None:
        if property_name not in self._properties:
            logging.error(f"Trying to set value of property \"{property_name}\" in \"{self.__class__.__name__}\" but the property has not been registered!")
            raise Exception

        if property_value is None:
            logging.warning(f"Trying to set value of property \"{property_name}\" in \"{self.__class__.__name__}\" to None.")
            self._clear(property_name)
            return

        self._properties[property_name] = property_value

    def _clear(self, property_name: str) -> None:
        if property_name not in self._properties:
            logging.error(f"Trying to clear value of property \"{property_name}\" in \"{self.__class__.__name__}\" but the property has not been registered!")
            raise Exception

        self._properties[property_name] = None
