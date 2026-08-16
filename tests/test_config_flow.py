import unittest

from ex_installer.config_flow import (
    ap_config_lines,
    csb1_track_defaults,
    post_flash_verification,
    should_upload,
    validate_static_ip,
)


class ConfigFlowTests(unittest.TestCase):
    def test_compile_only_skips_upload(self):
        self.assertFalse(should_upload(True))
        self.assertTrue(should_upload(False))

    def test_csb1_defaults_tracks_c_and_d_to_main(self):
        self.assertEqual(csb1_track_defaults("EXCSB1_DUAL")["C"], "MAIN")
        self.assertEqual(csb1_track_defaults("EXCSB1_DUAL")["D"], "MAIN")
        self.assertIsNone(csb1_track_defaults("STANDARD_MOTOR_SHIELD"))

    def test_custom_ap_emits_force_ap(self):
        lines = ap_config_lines("layout", "password123")
        self.assertIn('#define FORCE_AP true\n', lines)
        self.assertIn('#define WIFI_SSID "layout"\n', lines)

    def test_default_ap_keeps_firmware_defaults(self):
        lines = ap_config_lines("", "")
        self.assertNotIn('#define FORCE_AP true\n', lines)

    def test_static_ip_validation(self):
        self.assertEqual(validate_static_ip([192, 168, 1, 50]), "192.168.1.50")
        with self.assertRaises(ValueError):
            validate_static_ip([999, 168, 1, 50])

    def test_post_flash_verification(self):
        self.assertTrue(post_flash_verification("DCC-EX CommandStation ready"))
        self.assertFalse(post_flash_verification("upload failed: error"))


if __name__ == "__main__":
    unittest.main()
