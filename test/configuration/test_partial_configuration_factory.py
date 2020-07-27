import os
from pathlib import Path
from typing import Dict, Any, List
from unittest import TestCase

from src.configuration.partial_configuration_factory import PartialConfigurationFactory


class TestPartialConfigurationFactory(TestCase):

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
        file: Path = Path(".__temp__").expanduser().absolute()
        try:
            with file.open("w+") as f:
                self.assertTrue(file.exists())
                self.assertTrue(file.is_file())

                returned_file: Path = PartialConfigurationFactory.assert_is_existing_file(TestCase, "property_name", str(file))
                self.assertEqual(str(file), str(returned_file.expanduser().absolute()))

        finally:
            os.remove(str(file.expanduser().absolute()))

    def test_assert_is_existing_file_does_not_accept_none(self):
        with self.assertRaises(Exception):
            PartialConfigurationFactory.assert_is_existing_file(TestCase, "property_name", None)

    def test_assert_is_existing_file_does_not_accept_directory(self):
        directory: Path = Path(".__temp__/")
        try:
            directory.mkdir(parents=True, exist_ok=True)
            self.assertTrue(directory.exists())
            self.assertFalse(directory.is_file())

            with self.assertRaises(Exception):
                PartialConfigurationFactory.assert_is_existing_file(TestCase, "property_name", str(directory.expanduser().absolute()))

        finally:
            os.removedirs(str(directory.expanduser().absolute()))

    def test_assert_is_existing_file_does_not_accept_absent_file(self):
        file: Path = Path(".__temp__.bin").expanduser().absolute()
        if file.exists():
            os.remove(str(file))

        self.assertFalse(file.exists())
        with self.assertRaises(Exception):
            PartialConfigurationFactory.assert_is_existing_file(TestCase, "property_name", str(file))

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
