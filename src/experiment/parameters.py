import re
from typing import Dict, Any, List, Tuple, Optional, Union

from src.utility import assert_is_experiment


class Parameters:

    def __init__(self, experiment: Any, properties: Dict[str, Any]):
        from src.experiment.experiment import Experiment
        self._experiment: Experiment = assert_is_experiment(experiment)

        self._parameter_regex: re = re.compile(r"(?P<Frame>{{(?P<Name>[\w-]+?)}})")
        self._properties: Dict[str, Any] = properties
        self._common_parameters: Dict[str, str] = {}
        self._specific_parameters: Dict[str, Dict[str, str]] = {}

        self._initialize_parameters()

    def _initialize_parameters(self) -> None:
        self._common_parameters["experiment-name"] = self._experiment.name

        self._initialize_common_parameters()
        self._initialize_specific_parameters()

    def _initialize_common_parameters(self) -> None:
        if "common" not in self._properties:
            return

        unresolved_parameters: Dict[str, Any] = self._properties["common"]
        while len(unresolved_parameters) > 0:
            new_unresolved_parameters: Dict[str, Any] = {}

            for parameter_name in unresolved_parameters:
                parameter_value: str = str(unresolved_parameters[parameter_name])
                matches: List[Tuple[str, str]] = self._parameter_regex.findall(parameter_value)
                is_resolved: bool = True

                for block, name in matches:
                    if name not in self._common_parameters:
                        is_resolved = False
                        break

                    parameter_value = parameter_value.replace(block, self._common_parameters[name])

                if not is_resolved:
                    new_unresolved_parameters[parameter_name] = unresolved_parameters[parameter_name]
                    continue

                self._common_parameters[parameter_name] = parameter_value

            if len(new_unresolved_parameters) == len(unresolved_parameters):
                raise Exception("Cyclic dependency in common parameters detected!")

            unresolved_parameters = new_unresolved_parameters

    def _initialize_specific_parameters(self) -> None:
        if "specific" not in self._properties:
            return

        specific_parameter_collection: List[Dict[str, Any]] = self._properties["specific"]

        for host in self._experiment.hosts:
            self._specific_parameters[host] = {}

            host_parameter_indices: List[int] = [index
                                                 for index, params in enumerate(specific_parameter_collection)
                                                 if "hosts" in params and host in params["hosts"]]

            self._resolve_specific_parameters(host,
                                              Parameters._unresolved_specific_parameters(host,
                                                                                         specific_parameter_collection,
                                                                                         host_parameter_indices))

    @staticmethod
    def _unresolved_specific_parameters(host: str,
                                        specific_parameter_collection: List[Dict[str, Any]],
                                        host_parameter_indices: List[int]) -> Dict[str, str]:

        unresolved_parameters: Dict[str, str] = {}
        for index in host_parameter_indices:
            for key in specific_parameter_collection[index]:
                if key == "hosts":
                    continue

                if key in unresolved_parameters:
                    raise Exception(f"Duplicated specific parameter \"{key}\" for host \"{host}\"!")

                unresolved_parameters[key] = str(specific_parameter_collection[index][key])

        return unresolved_parameters

    def _resolve_specific_parameters(self, host: str, unresolved_parameters: Dict[str, str]) -> None:

        while len(unresolved_parameters) > 0:
            new_unresolved_parameters: Dict[str, str] = {}

            for parameter_name in unresolved_parameters:
                parameter_value: str = str(unresolved_parameters[parameter_name])
                matches: List[Tuple[str, str]] = self._parameter_regex.findall(parameter_value)
                is_resolved: bool = True

                for block, name in matches:
                    sub_value: Optional[str] = None
                    if name == "host":
                        sub_value = host
                    elif name in self._specific_parameters[host]:
                        sub_value = self._specific_parameters[host][name]
                    elif name in self._common_parameters:
                        sub_value = self._common_parameters[name]

                    if sub_value is None:
                        is_resolved = False
                        break

                    parameter_value = parameter_value.replace(block, sub_value)

                if not is_resolved:
                    new_unresolved_parameters[parameter_name] = unresolved_parameters[parameter_name]
                    continue

                self._specific_parameters[host][parameter_name] = parameter_value

            if len(new_unresolved_parameters) == len(unresolved_parameters):
                raise Exception("Cyclic dependency in common parameters detected!")

            unresolved_parameters = new_unresolved_parameters

    def value(self, host: str, parameter_name: str) -> str:
        parameter_value: Optional[str] = self._try_get_specific_value(host, parameter_name)
        if parameter_value is not None:
            return parameter_value

        return self._common_parameters[parameter_name]

    def _try_get_specific_value(self, host: str, parameter_name: str) -> Optional[str]:
        if parameter_name == "host":
            return host

        if host not in self._specific_parameters:
            return None

        if parameter_name not in self._specific_parameters[host]:
            return None

        return self._specific_parameters[host][parameter_name]

    def resolve(self, host: str, parameterized_string: Union[str, List[str]]) -> Union[str, List[str]]:
        if isinstance(parameterized_string, str):
            return self._resolve_string(host, parameterized_string)

        if isinstance(parameterized_string, list):
            return self._resolve_list_of_string(host, parameterized_string)

        raise Exception(f"Unexpected argument type!")

    def _resolve_string(self, host: str, parameterized_string: str) -> str:
        matches: List[Tuple[str, str]] = self._parameter_regex.findall(parameterized_string)
        return_value: str = parameterized_string

        for block, name in matches:
            return_value = return_value.replace(block, self.value(host, name))

        return return_value

    def _resolve_list_of_string(self, host: str, parameterized_string: List[str]) -> List[str]:
        return [self._resolve_string(host, s) for s in parameterized_string]
