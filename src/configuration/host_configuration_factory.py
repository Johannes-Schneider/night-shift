import getpass
import logging
from pathlib import Path
from typing import Dict, Callable, Any, Optional, List

from src.configuration.host_configuration import HostConfiguration
from src.configuration.partial_configuration_factory import PartialConfigurationFactory


class HostConfigurationFactory(PartialConfigurationFactory):
    __SHARED_PROPERTY_KEY: str = "common"
    __HOSTS_PROPERTY_KEY: str = "hosts"

    __SHARABLE_PROPERTY_NAMES: List[str] = [
        HostConfiguration.ssh_user.__name__,
        HostConfiguration.ssh_port.__name__,
        HostConfiguration.ssh_key.__name__,
    ]

    __PROPERTY_VALIDATION: Dict[str, Callable[[type, str, Any], Any]] = {
        HostConfiguration.name.__name__: PartialConfigurationFactory.assert_is_str,
        HostConfiguration.aliases.__name__: PartialConfigurationFactory.assert_is_list_of_str,
        HostConfiguration.ssh_user.__name__: PartialConfigurationFactory.assert_is_str,
        HostConfiguration.ssh_address.__name__: PartialConfigurationFactory.assert_is_str,
        HostConfiguration.ssh_port.__name__: PartialConfigurationFactory.assert_is_int,
        HostConfiguration.ssh_key.__name__: PartialConfigurationFactory.assert_is_existing_file,
    }

    __PROPERTY_SETTER: Dict[str, Callable[[HostConfiguration, Any], None]] = {
        HostConfiguration.name.__name__: HostConfiguration.name,
        HostConfiguration.aliases.__name__: HostConfiguration.aliases,
        HostConfiguration.ssh_user.__name__: HostConfiguration.ssh_user,
        HostConfiguration.ssh_address.__name__: HostConfiguration.ssh_address,
        HostConfiguration.ssh_port.__name__: HostConfiguration.ssh_port,
        HostConfiguration.ssh_key.__name__: HostConfiguration.ssh_key,
    }

    @staticmethod
    def default() -> HostConfiguration:
        config: HostConfiguration = HostConfiguration()
        config.aliases = []
        config.ssh_user = getpass.getuser()
        config.ssh_port = 22
        config.ssh_key = Path("~/.ssh/id_rsa").expanduser()

        return config

    @staticmethod
    def all_from_json(properties: Dict[str, Any]) -> List[HostConfiguration]:
        properties = PartialConfigurationFactory.to_lower(properties)

        configs: List[HostConfiguration] = []
        base_config: HostConfiguration = HostConfigurationFactory.shared_from_json(properties)

        if HostConfigurationFactory.__HOSTS_PROPERTY_KEY not in properties:
            logging.error(f"Mandatory property \"{HostConfigurationFactory.__HOSTS_PROPERTY_KEY}\" was not found!")
            raise Exception

        hosts: Any = properties[HostConfigurationFactory.__HOSTS_PROPERTY_KEY]
        if not isinstance(hosts, list):
            logging.error(f"Property \"{HostConfigurationFactory.__HOSTS_PROPERTY_KEY}\" must be of type list!")
            raise Exception

        for host in hosts:
            if isinstance(host, str):
                config: HostConfiguration = HostConfiguration(base_config)
                config.name = host
                config.ssh_address = host
                config.aliases = []

                configs.append(config)

            elif isinstance(host, dict):
                configs.append(HostConfigurationFactory.from_json(host, base_config))

            else:
                logging.error(f"Entries within the \"{HostConfigurationFactory.__HOSTS_PROPERTY_KEY}\" must be of type string or dict!")
                raise Exception

        return configs

    @staticmethod
    def shared_from_json(properties: Dict[str, Any]) -> HostConfiguration:
        properties = PartialConfigurationFactory.to_lower(properties)

        config: HostConfiguration = HostConfigurationFactory.default()

        if HostConfigurationFactory.__SHARED_PROPERTY_KEY not in properties:
            return config

        if not isinstance(properties[HostConfigurationFactory.__SHARED_PROPERTY_KEY], dict):
            logging.error(f"Property \"{HostConfigurationFactory.__SHARED_PROPERTY_KEY}\" must be of type dict!")
            raise Exception

        config = HostConfiguration(config)
        HostConfigurationFactory._set_config_properties(config,
                                                        properties[HostConfigurationFactory.__SHARED_PROPERTY_KEY],
                                                        HostConfigurationFactory.__SHARABLE_PROPERTY_NAMES)

        return config

    @staticmethod
    def from_json(properties: Dict[str, Any], parent: Optional[HostConfiguration] = None) -> HostConfiguration:
        properties = PartialConfigurationFactory.to_lower(properties)

        config: HostConfiguration = HostConfiguration(parent)
        HostConfigurationFactory._set_config_properties(config, properties)

        return config

    @staticmethod
    def _set_config_properties(config: HostConfiguration, properties: Dict[str, Any], supported_properties: Optional[List[str]] = None) -> None:
        unused_properties: List[str] = []

        for property_name in properties:
            if supported_properties and property_name not in supported_properties:
                unused_properties.append(property_name)
                continue

            if property_name.lower() not in HostConfigurationFactory.__PROPERTY_VALIDATION:
                unused_properties.append(property_name)
                continue

            validation: Callable[[type, str, Any], Any] = HostConfigurationFactory.__PROPERTY_VALIDATION[property_name]
            property_value: Any = validation(config.__class__, property_name, properties[property_name])

            setter: Callable[[HostConfiguration, Any], None] = HostConfigurationFactory.__PROPERTY_SETTER[property_name]
            setter(config, property_value)

        if len(unused_properties) > 0:
            logging.warning(f"Following properties are not supported in the current context: {', '.join(unused_properties)}.")
