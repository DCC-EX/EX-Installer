import unittest

from ex_installer.manage_arduino_cli import (
    _installed_version,
    _is_dependency_installed,
    _items_from_cli_response,
)


class ArduinoCliInventoryTests(unittest.TestCase):
    def test_accepts_bare_and_wrapped_platform_inventories(self):
        platform = {"id": "arduino:avr", "installed_version": "1.8.6"}
        self.assertEqual(_items_from_cli_response([platform], "platforms"), [platform])
        self.assertEqual(_items_from_cli_response({"platforms": [platform]}, "platforms"), [platform])

    def test_missing_or_malformed_inventory_is_not_an_install_success(self):
        self.assertEqual(_items_from_cli_response({"platforms": None}, "platforms"), None)
        self.assertEqual(_items_from_cli_response({"unexpected": []}, "platforms"), [])
        self.assertFalse(_is_dependency_installed([], "arduino:avr", "1.8.6", "platform"))

    def test_platform_requires_exact_id_and_version(self):
        items = [{"id": "arduino:avr", "installed": "1.8.6"}]
        self.assertTrue(_is_dependency_installed(items, "arduino:avr", "1.8.6", "platform"))
        self.assertFalse(_is_dependency_installed(items, "arduino:avr", "1.8.5", "platform"))
        self.assertEqual(_installed_version(items[0], "platform"), ("arduino:avr", "1.8.6"))

    def test_library_requires_nested_name_and_exact_version(self):
        items = [{"library": {"name": "Ethernet", "version": "2.0.2"}}]
        self.assertTrue(_is_dependency_installed(items, "Ethernet", "2.0.2", "library"))
        self.assertFalse(_is_dependency_installed(items, "Ethernet", "2.0.1", "library"))
        self.assertFalse(_is_dependency_installed([{}], "Ethernet", "2.0.2", "library"))


if __name__ == "__main__":
    unittest.main()
