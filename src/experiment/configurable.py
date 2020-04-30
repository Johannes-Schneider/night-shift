from abc import ABC, abstractmethod
from typing import Any, Dict, Callable, Optional


class Configurable(ABC):

    def __init__(self, properties: Dict[str, Any]):
        self._properties: Dict[str, Any] = {}

        for item in properties:
            self._properties[item.lower()] = properties[item]

        self._cached_properties: Dict[str, Any] = {}
        self._initialize_cache()

    @abstractmethod
    def _initialize_cache(self):
        raise NotImplementedError

    def _fill_cache(self,
                    property_name: str,
                    property_initializer: Optional[Callable[[str], Any]] = None,
                    default_value: Any = None) -> None:
        property_name = property_name.lower()
        property_value: Any = default_value

        if property_name in self._properties:
            property_value = self._properties[property_name]

        if property_initializer and property_value:
            property_value = property_initializer(property_value)

        self._cached_properties[property_name] = property_value

    def _cached_property_value(self, key: str) -> Any:
        return self._cached_properties[key.lower()]
