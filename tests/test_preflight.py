import unittest

from ex_installer.preflight import check_dependencies, check_environment, check_python_version, format_errors


class PreflightTests(unittest.TestCase):
    def test_accepts_supported_python(self):
        self.assertIsNone(check_python_version((3, 10)))
        self.assertIsNone(check_python_version((3, 13)))

    def test_rejects_old_python_with_recovery_hint(self):
        error = check_python_version((3, 9))
        self.assertIn("Python 3.10 or newer", error)
        self.assertIn("recreate the virtual environment", error)

    def test_reports_missing_pyserial(self):
        errors = check_dependencies(lambda name: None)
        self.assertEqual(len(errors), 1)
        self.assertIn("pyserial", errors[0])
        self.assertIn("python -m pip install -r requirements.txt", errors[0])

    def test_combines_python_and_dependency_errors(self):
        errors = check_environment((3, 9), lambda name: None)
        self.assertEqual(len(errors), 2)
        self.assertTrue(format_errors(errors).startswith("EX-Installer cannot start:"))


if __name__ == "__main__":
    unittest.main()
