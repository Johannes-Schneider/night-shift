import getpass
import logging
from enum import Enum
from pathlib import Path
from typing import Dict, Callable, Any, Optional, List

from src.configuration.host_configuration import HostConfiguration
from src.configuration.partial_configuration_factory import PartialConfigurationFactory


class HostConfigurationFactory(PartialConfigurationFactory):
    class PropertyKey:
        Hosts: str = "hosts"

        HostName: str = "name"
        HostAliases: str = "aliases"
        SSHUser: str = "ssh-user"
        SSHAddress: str = "ssh-address"
        SSHPort: str = "ssh-port"
        SSHKey: str = "ssh-key"

        SharedProperties: str = "common"

    __SHARABLE_PROPERTIES: List[str] = [
        PropertyKey.SSHUser,
        PropertyKey.SSHPort,
        PropertyKey.SSHKey,
    ]

    __PROPERTY_VALIDATION: Dict[str, Callable[[type, str, Any], Any]] = {
        PropertyKey.HostName: PartialConfigurationFactory.assert_is_str,
        PropertyKey.HostAliases: PartialConfigurationFactory.assert_is_list_of_str,
        PropertyKey.SSHUser: PartialConfigurationFactory.assert_is_str,
        PropertyKey.SSHAddress: PartialConfigurationFactory.assert_is_str,
        PropertyKey.SSHPort: PartialConfigurationFactory.assert_is_int,
        PropertyKey.SSHKey: PartialConfigurationFactory.assert_is_existing_file,
    }

    __PROPERTY_SETTER: Dict[str, Callable[[HostConfiguration, Any], None]] = {
        PropertyKey.HostName: HostConfiguration.name.fset,
        PropertyKey.HostAliases: HostConfiguration.aliases.fset,
        PropertyKey.SSHUser: HostConfiguration.ssh_user.fset,
        PropertyKey.SSHAddress: HostConfiguration.ssh_address.fset,
        PropertyKey.SSHPort: HostConfiguration.ssh_port.fset,
        PropertyKey.SSHKey: HostConfiguration.ssh_key.fset,
    }

    def __init__(self):
        super().__init__()
        raise NotImplementedError

    @staticmethod
    def default() -> HostConfiguration:
        config: HostConfiguration = HostConfiguration()
        config.aliases = []
        config.ssh_user = getpass.getuser()
        config.ssh_port = 22
        config.ssh_key = Path("~/.ssh/id_rsa").expanduser()

        return config

    @staticmethod
    def extract_all_configurations(properties: Dict[str, Any]) -> List[HostConfiguration]:
        properties = PartialConfigurationFactory.to_lower(properties)

        configs: List[HostConfiguration] = []
        base_config: HostConfiguration = HostConfigurationFactory.extract_shared_configuration(properties)

        if HostConfigurationFactory.PropertyKey.Hosts not in properties:
            logging.error(f"Mandatory property \"{HostConfigurationFactory.PropertyKey.Hosts}\" was not found!")
            raise Exception

        hosts: Any = properties[HostConfigurationFactory.PropertyKey.Hosts]
        if not isinstance(hosts, list):
            logging.error(f"Property \"{HostConfigurationFactory.PropertyKey.Hosts}\" must be of type list!")
            raise Exception

        for host in hosts:
            if isinstance(host, str):
                config: HostConfiguration = HostConfiguration(base_config)
                config.name = host
                config.ssh_address = host
                config.aliases = []

                configs.append(config)

            elif isinstance(host, dict):
                configs.append(HostConfigurationFactory.extract_single_configuration(host, base_config))

            else:
                logging.error(f"Entries within the \"{HostConfigurationFactory.PropertyKey.Hosts}\" must be of type string or dict!")
                raise Exception

        return configs

    @staticmethod
    def extract_shared_configuration(properties: Dict[str, Any]) -> HostConfiguration:
        properties = PartialConfigurationFactory.to_lower(properties)

        config: HostConfiguration = HostConfigurationFactory.default()

        if HostConfigurationFactory.PropertyKey.SharedProperties not in properties:
            return config

        if not isinstance(properties[HostConfigurationFactory.PropertyKey.SharedProperties], dict):
            logging.error(f"Property \"{HostConfigurationFactory.PropertyKey.SharedProperties}\" must be of type dict!")
            raise Exception

        config = HostConfiguration(config)
        HostConfigurationFactory._set_configuration_properties(config,
                                                               properties[HostConfigurationFactory.PropertyKey.SharedProperties],
                                                               HostConfigurationFactory.__SHARABLE_PROPERTIES)

        return config

    @staticmethod
    def extract_single_configuration(properties: Dict[str, Any], parent: Optional[HostConfiguration] = None) -> HostConfiguration:
        properties = PartialConfigurationFactory.to_lower(properties)

        config: HostConfiguration = HostConfiguration(parent)
        HostConfigurationFactory._set_configuration_properties(config, properties)

        return config

    @staticmethod
    def _set_configuration_properties(config: HostConfiguration, properties: Dict[str, Any], supported_properties: Optional[List[str]] = None) -> None:
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
