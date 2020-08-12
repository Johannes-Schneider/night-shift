import getpass
import os
from pathlib import Path
from typing import Dict, Any, Optional, List, Callable
from unittest import TestCase

from src.configuration.host.host_configuration import HostConfiguration
from src.configuration.host.host_configuration_factory import HostConfigurationFactory
from test.test_utility import with_temporary_files, with_absent_files, with_temporary_directories


class TestHostConfigurationFactory(TestCase):

    def test_cannot_be_instantiated(self):
        with self.assertRaises(NotImplementedError):
            HostConfigurationFactory()

    def test_default(self):
        default: HostConfiguration = HostConfigurationFactory.default()
        self._assert_is_default_configuration(default)

    def test_extract_shared_configuration(self):
        def _run(paths: List[Path], _) -> None:
            properties: Dict[str, Any] = {
                HostConfigurationFactory.PropertyKey.SharedProperties: {
                    HostConfigurationFactory.PropertyKey.SSHUser: "user",
                    HostConfigurationFactory.PropertyKey.SSHPort: 8080,
                    HostConfigurationFactory.PropertyKey.SSHKey: str(paths[0]),
                }}

            shared_configuration: HostConfiguration = HostConfigurationFactory.extract_shared_configuration(properties)
            self._assert_properties(shared_configuration,
                                    name=None,
                                    aliases=[],
                                    ssh_address=None,
                                    ssh_user="user",
                                    ssh_port=8080,
                                    ssh_key=paths[0])

        with_temporary_files(_run)

    def test_extract_shared_configuration_ssh_key_must_exist(self):
        def _run(paths: List[Path]) -> None:
            properties: Dict[str, Any] = {
                HostConfigurationFactory.PropertyKey.SharedProperties: {
                    HostConfigurationFactory.PropertyKey.SSHKey: str(paths[0])
                }}

            with self.assertRaises(Exception):
                _: HostConfiguration = HostConfigurationFactory.extract_shared_configuration(properties)

        with_absent_files(_run)

    def test_extract_shared_configuration_ssh_key_must_be_file(self):
        def _run(paths: List[Path]) -> None:
            properties: Dict[str, Any] = {
                HostConfigurationFactory.PropertyKey.SharedProperties: {
                    HostConfigurationFactory.PropertyKey.SSHKey: str(paths[0])
                }}

            with self.assertRaises(Exception):
                _: HostConfiguration = HostConfigurationFactory.extract_shared_configuration(properties)

        with_temporary_directories(_run)

    def test_extract_shared_configuration_returns_default_configuration_on_empty_properties(self):
        properties: Dict[str, Any] = {}

        shared_configuration: HostConfiguration = HostConfigurationFactory.extract_shared_configuration(properties)
        self._assert_is_default_configuration(shared_configuration)

    def test_extract_shared_configuration_ignores_unsupported_properties(self):
        properties: Dict[str, Any] = {
            HostConfigurationFactory.PropertyKey.SharedProperties: {
                "not-supported": "not_supported",
                HostConfigurationFactory.PropertyKey.SSHPort: 8080,
            }}

        shared_configuration: HostConfiguration = HostConfigurationFactory.extract_shared_configuration(properties)
        self._assert_properties(shared_configuration,
                                name=None,
                                aliases=[],
                                ssh_user=getpass.getuser(),
                                ssh_address=None,
                                ssh_port=8080,
                                ssh_key=Path("~/.ssh/id_rsa").expanduser())

    def test_extract_shared_configuration_properties_must_be_a_dictionary(self):
        with self.assertRaises(Exception):
            _: HostConfiguration = HostConfigurationFactory.extract_shared_configuration({"common": "string"})

        with self.assertRaises(Exception):
            _: HostConfiguration = HostConfigurationFactory.extract_shared_configuration({"common": []})

        with self.assertRaises(Exception):
            _: HostConfiguration = HostConfigurationFactory.extract_shared_configuration({"common": 0})

        with self.assertRaises(Exception):
            _: HostConfiguration = HostConfigurationFactory.extract_shared_configuration({"common": 0.0})

    def test_extract_single_configuration(self):
        def _run(paths: List[Path], _) -> None:
            properties: Dict[str, Any] = {
                HostConfigurationFactory.PropertyKey.HostName: "node01",
                HostConfigurationFactory.PropertyKey.HostAliases: ["cluster01-node01"],
                HostConfigurationFactory.PropertyKey.SSHUser: "john.doe",
                HostConfigurationFactory.PropertyKey.SSHAddress: "192.168.8.12",
                HostConfigurationFactory.PropertyKey.SSHPort: 8080,
                HostConfigurationFactory.PropertyKey.SSHKey: str(paths[0]),
            }

            configuration: HostConfiguration = HostConfigurationFactory.extract_single_configuration(properties)
            self._assert_properties(configuration,
                                    name="node01",
                                    aliases=["cluster01-node01"],
                                    ssh_user="john.doe",
                                    ssh_address="192.168.8.12",
                                    ssh_port=8080,
                                    ssh_key=paths[0])

        with_temporary_files(_run)

    def test_extract_all_configurations(self):
        def _run(paths: List[Path], _) -> None:
            properties: Dict[str, Any] = {
                HostConfigurationFactory.PropertyKey.Hosts: [
                    {
                        HostConfigurationFactory.PropertyKey.HostName: "node01",
                        HostConfigurationFactory.PropertyKey.HostAliases: ["cluster01-node01"],
                        HostConfigurationFactory.PropertyKey.SSHUser: "john.doe",
                        HostConfigurationFactory.PropertyKey.SSHAddress: "node01",
                        HostConfigurationFactory.PropertyKey.SSHPort: 8080,
                        HostConfigurationFactory.PropertyKey.SSHKey: str(paths[0]),
                    },
                    {
                        HostConfigurationFactory.PropertyKey.HostName: "node02",
                        HostConfigurationFactory.PropertyKey.HostAliases: ["cluster01-node02"],
                        HostConfigurationFactory.PropertyKey.SSHUser: "jdoe",
                        HostConfigurationFactory.PropertyKey.SSHAddress: "192.168.8.99",
                        HostConfigurationFactory.PropertyKey.SSHPort: 8181,
                        HostConfigurationFactory.PropertyKey.SSHKey: str(paths[1]),
                    }
                ]
            }

            configurations: List[HostConfiguration] = HostConfigurationFactory.extract_all_configurations(properties)
            self.assertTrue(len(configurations), 2)

            configuration1: HostConfiguration = [config for config in configurations if config.name == "node01"][0]
            configuration2: HostConfiguration = [config for config in configurations if config.name == "node02"][0]

            self._assert_properties(configuration1,
                                    name="node01",
                                    aliases=["cluster01-node01"],
                                    ssh_user="john.doe",
                                    ssh_address="node01",
                                    ssh_port=8080,
                                    ssh_key=paths[0])
            self._assert_properties(configuration2,
                                    name="node02",
                                    aliases=["cluster01-node02"],
                                    ssh_user="jdoe",
                                    ssh_address="192.168.8.99",
                                    ssh_port=8181,
                                    ssh_key=paths[1])

        with_temporary_files(_run, 2)

    def _assert_is_default_configuration(self, configuration: HostConfiguration):
        self._assert_properties(configuration,
                                name=None,
                                aliases=[],
                                ssh_address=None,
                                ssh_user=getpass.getuser(),
                                ssh_port=22,
                                ssh_key=Path("~/.ssh/id_rsa").expanduser())

        self.assertIsNone(configuration._parent)

    def _assert_properties(self, configuration: HostConfiguration,
                           name: Optional[str] = None,
                           aliases: Optional[List[str]] = None,
                           ssh_user: Optional[str] = None,
                           ssh_address: Optional[str] = None,
                           ssh_port: Optional[int] = None,
                           ssh_key: Optional[Path] = None):

        self.assertIsNotNone(configuration)
        self._assert_property(configuration, HostConfiguration.name.fget, self.assertEqual, name)
        self._assert_property(configuration, HostConfiguration.aliases.fget, self.assertListEqual, aliases)
        self._assert_property(configuration, HostConfiguration.ssh_user.fget, self.assertEqual, ssh_user)
        self._assert_property(configuration, HostConfiguration.ssh_address.fget, self.assertEqual, ssh_address)
        self._assert_property(configuration, HostConfiguration.ssh_port.fget, self.assertEqual, ssh_port)
        self._assert_property(configuration, HostConfiguration.ssh_key.fget, self.assertEqual, ssh_key)

    def _assert_property(self, configuration: HostConfiguration,
                         getter: Callable[[HostConfiguration], Any],
                         assertion: Callable[[Any, Any], None],
                         expected: Optional[Any] = None):

        if expected is None:
            with self.assertRaises(Exception):
                _ = getter(configuration)

        else:
            assertion(getter(configuration), expected)
