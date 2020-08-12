from pathlib import Path
from typing import Dict, Any, List
from unittest import TestCase

from src.configuration.partial_configuration_factory import PartialConfigurationFactory
from test.test_utility import with_temporary_files, with_temporary_directories, with_absent_files


class TestPartialConfigurationFactory(TestCase):

    def test_cannot_be_instantiated(self):
        with self.assertRaises(NotImplementedError):
            PartialConfigurationFactory()

    def test_to_lower(self):
        my_dict: Dict[str, Any] = {
            "UPPER": 0,
            "lower": 1,
            "Mixed": 2,
        }

        lower_dict: Dict[str, Any] = PartialConfigurationFactory.to_lower(my_dict)

        self.assertEqual(lower_dict["upper"], 0)
        self.assertEqual(lower_dict["lower"], 1)
        self.assertEqual(lower_dict["mixed"], 2)

    def test_assert_is_str(self):
        self.assertEqual("", PartialConfigurationFactory.assert_is_str(TestCase, "property_name", ""))
        self.assertEqual("property_value", PartialConfigurationFactory.assert_is_str(TestCase, "property_name", "property_value"))

    def test_assert_is_str_does_not_accept_none(self):
        with self.assertRaises(Exception):
            PartialConfigurationFactory.assert_is_str(TestCase, "property_name", None)

    def test_assert_is_str_does_only_accept_strings(self):
        with self.assertRaises(TypeError):
            PartialConfigurationFactory.assert_is_str(TestCase, "property_name", 0)

        with self.assertRaises(TypeError):
            PartialConfigurationFactory.assert_is_str(TestCase, "property_name", 0.0)

        with self.assertRaises(TypeError):
            PartialConfigurationFactory.assert_is_str(TestCase, "property_name", ["property_value"])

        with self.assertRaises(TypeError):
            PartialConfigurationFactory.assert_is_str(TestCase, "property_name", {"key": "value"})

    def test_assert_is_int(self):
        self.assertEqual(1, PartialConfigurationFactory.assert_is_int(TestCase, "property_name", 1))

    def test_assert_is_int_does_not_accept_none(self):
        with self.assertRaises(Exception):
            PartialConfigurationFactory.assert_is_int(TestCase, "property_name", None)

    def test_assert_is_int_does_only_accept_ints(self):
        with self.assertRaises(TypeError):
            PartialConfigurationFactory.assert_is_int(TestCase, "property_name", "0")

        with self.assertRaises(TypeError):
            PartialConfigurationFactory.assert_is_int(TestCase, "property_name", 0.0)

        with self.assertRaises(TypeError):
            PartialConfigurationFactory.assert_is_int(TestCase, "property_name", ["property_value"])

        with self.assertRaises(TypeError):
            PartialConfigurationFactory.assert_is_int(TestCase, "property_name", {"key": "value"})

    def test_assert_is_float(self):
        self.assertEqual(1.0, PartialConfigurationFactory.assert_is_float(TestCase, "property_name", 1.0))

    def test_assert_is_float_does_not_accept_none(self):
        with self.assertRaises(Exception):
            PartialConfigurationFactory.assert_is_float(TestCase, "property_name", None)

    def test_assert_is_float_does_only_accept_floats(self):
        with self.assertRaises(TypeError):
            PartialConfigurationFactory.assert_is_float(TestCase, "property_name", "0")

        with self.assertRaises(TypeError):
            PartialConfigurationFactory.assert_is_float(TestCase, "property_name", 0)

        with self.assertRaises(TypeError):
            PartialConfigurationFactory.assert_is_float(TestCase, "property_name", ["property_value"])

        with self.assertRaises(TypeError):
            PartialConfigurationFactory.assert_is_float(TestCase, "property_name", {"key": "value"})

    def test_assert_is_existing_file(self):
        def _run(paths: List[Path], _) -> None:
            returned_file: Path = PartialConfigurationFactory.assert_is_existing_file(TestCase, "property_name", str(paths[0]))
            self.assertEqual(str(paths[0]), str(returned_file.expanduser().absolute()))

        with_temporary_files(_run)

    def test_assert_is_existing_file_does_not_accept_none(self):
        with self.assertRaises(Exception):
            PartialConfigurationFactory.assert_is_existing_file(TestCase, "property_name", None)

    def test_assert_is_existing_file_does_not_accept_directory(self):
        def _run(paths: List[Path]) -> None:
            with self.assertRaises(Exception):
                PartialConfigurationFactory.assert_is_existing_file(TestCase, "property_name", str(paths[0]))

        with_temporary_directories(_run)

    def test_assert_is_existing_file_does_not_accept_absent_file(self):
        def _run(paths: List[Path]) -> None:
            with self.assertRaises(Exception):
                PartialConfigurationFactory.assert_is_existing_file(TestCase, "property_name", str(paths[0]))

        with_absent_files(_run)

    def test_assert_is_existing_file_does_only_accept_strings(self):
        with self.assertRaises(TypeError):
            PartialConfigurationFactory.assert_is_existing_file(TestCase, "property_name", 0)

        with self.assertRaises(TypeError):
            PartialConfigurationFactory.assert_is_existing_file(TestCase, "property_name", 0.0)

        with self.assertRaises(TypeError):
            PartialConfigurationFactory.assert_is_existing_file(TestCase, "property_name", ["property_value"])

        with self.assertRaises(TypeError):
            PartialConfigurationFactory.assert_is_existing_file(TestCase, "property_name", {"key": "value"})

    def test_assert_is_list_of_str(self):
        lst: List[str] = ["1", "2", "test", "value"]
        self.assertEqual(lst, PartialConfigurationFactory.assert_is_list_of_str(TestCase, "property_name", lst))

    def test_assert_is_list_of_str_does_not_accept_none(self):
        with self.assertRaises(Exception):
            PartialConfigurationFactory.assert_is_list_of_str(TestCase, "property_name", None)

    def test_assert_is_list_of_str_does_not_accept_mixed_lists(self):
        with self.assertRaises(TypeError):
            PartialConfigurationFactory.assert_is_list_of_str(TestCase, "property_name", ["1", 1, 1.0])

    def test_assert_is_list_of_str_does_only_accept_lists_of_strings(self):
        with self.assertRaises(TypeError):
            PartialConfigurationFactory.assert_is_list_of_str(TestCase, "property_name", "0")

        with self.assertRaises(TypeError):
            PartialConfigurationFactory.assert_is_list_of_str(TestCase, "property_name", 0)

        with self.assertRaises(TypeError):
            PartialConfigurationFactory.assert_is_list_of_str(TestCase, "property_name", 0.0)

        with self.assertRaises(TypeError):
            PartialConfigurationFactory.assert_is_list_of_str(TestCase, "property_name", {"key": "value"})
