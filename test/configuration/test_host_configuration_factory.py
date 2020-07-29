import getpass
import os
from pathlib import Path
from typing import Dict, Any, Optional, List, Callable
from unittest import TestCase

from src.configuration.host_configuration import HostConfiguration
from src.configuration.host_configuration_factory import HostConfigurationFactory


class TestHostConfigurationFactory(TestCase):

    def test_cannot_be_instantiated(self):
        with self.assertRaises(NotImplementedError):
            HostConfigurationFactory()

    def test_default(self):
        default: HostConfiguration = HostConfigurationFactory.default()
        self._assert_is_default_configuration(default)

    def test_extract_shared_configuration(self):
        ssh_key: Path = Path(".__temp_key__")
        try:
            with ssh_key.open("w+") as f:
                self.assertTrue(ssh_key.exists())
                self.assertTrue(ssh_key.is_file())

                properties: Dict[str, Any] = {
                    "common": {
                        "ssh_user": "user",
                        "ssh_port": 8080,
                        "ssh_key": str(ssh_key.expanduser().absolute()),
                    }}

                shared_configuration: HostConfiguration = HostConfigurationFactory.extract_shared_configuration(properties)
                self._assert_properties(shared_configuration,
                                        name=None,
                                        aliases=[],
                                        ssh_address=None,
                                        ssh_user="user",
                                        ssh_port=8080,
                                        ssh_key=ssh_key.expanduser().absolute())

        finally:
            os.remove(str(ssh_key.expanduser().absolute()))

    def test_extract_shared_configuration_ssh_key_must_exist(self):
        ssh_key: Path = Path(".__temp_key__")
        if ssh_key.exists():
            os.remove(str(ssh_key.expanduser().absolute()))

        self.assertFalse(ssh_key.exists())

        properties: Dict[str, Any] = {
            "common": {
                "ssh_key": str(ssh_key.expanduser().absolute())
            }}

        with self.assertRaises(Exception):
            _: HostConfiguration = HostConfigurationFactory.extract_shared_configuration(properties)

    def test_extract_shared_configuration_ssh_key_must_be_file(self):
        ssh_key: Path = Path(".__temp_dir__/")
        try:
            ssh_key.mkdir(parents=True, exist_ok=True)

            self.assertTrue(ssh_key.exists())
            self.assertTrue(ssh_key.is_dir())

            properties: Dict[str, Any] = {
                "common": {
                    "ssh_key": str(ssh_key.expanduser().absolute())
                }}

            with self.assertRaises(Exception):
                _: HostConfiguration = HostConfigurationFactory.extract_shared_configuration(properties)

        finally:
            os.removedirs(str(ssh_key.expanduser().absolute()))

    def test_extract_shared_configuration_returns_default_configuration_on_empty_properties(self):
        properties: Dict[str, Any] = {}

        shared_configuration: HostConfiguration = HostConfigurationFactory.extract_shared_configuration(properties)
        self._assert_is_default_configuration(shared_configuration)

    def test_extract_shared_configuration_ignores_unsupported_properties(self):
        properties: Dict[str, Any] = {
            "common": {
                "not_supported": "not_supported",
                "ssh_port": 8080,
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
        ssh_key: Path = Path(".__temp_key__").expanduser().absolute()
        try:
            with ssh_key.open("w+") as f:
                self.assertTrue(ssh_key.exists())
                self.assertTrue(ssh_key.is_file())

                properties: Dict[str, Any] = {
                    "name": "node01",
                    "aliases": ["cluster01-node01"],
                    "ssh_user": "john.doe",
                    "ssh_address": "192.168.8.12",
                    "ssh_port": 8080,
                    "ssh_key": str(ssh_key),
                }

                configuration: HostConfiguration = HostConfigurationFactory.extract_single_configuration(properties)
                self._assert_properties(configuration,
                                        name="node01",
                                        aliases=["cluster01-node01"],
                                        ssh_user="john.doe",
                                        ssh_address="192.168.8.12",
                                        ssh_port=8080,
                                        ssh_key=ssh_key)

        finally:
            os.remove(str(ssh_key))

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
            assertion(expected, getter(configuration))
