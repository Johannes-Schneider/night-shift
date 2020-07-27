from typing import Dict, Any
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
