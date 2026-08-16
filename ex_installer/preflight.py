"""Checks that can run before importing the GUI and its third-party modules."""

import importlib.util
import sys


MIN_PYTHON = (3, 10)
REQUIRED_MODULES = {
    "serial": "pyserial (install with: python -m pip install -r requirements.txt)",
}


def check_python_version(version=None):
    """Return an actionable error for unsupported Python versions, or ``None``."""
    version = version or sys.version_info
    if version[:2] < MIN_PYTHON:
        return (
            f"EX-Installer requires Python {MIN_PYTHON[0]}.{MIN_PYTHON[1]} or newer; "
            f"Python {version[0]}.{version[1]} is installed. "
            "Install a supported Python version and recreate the virtual environment."
        )
    return None


def check_dependencies(module_finder=importlib.util.find_spec):
    """Return actionable errors for dependencies needed during device upload."""
    errors = []
    for module, install_hint in REQUIRED_MODULES.items():
        try:
            available = module_finder(module) is not None
        except (ImportError, ModuleNotFoundError, ValueError):
            available = False
        if not available:
            errors.append(f"Missing dependency '{module}': {install_hint}")
    return errors


def check_environment(version=None, module_finder=importlib.util.find_spec):
    """Return all preflight errors without importing the GUI."""
    errors = []
    python_error = check_python_version(version)
    if python_error:
        errors.append(python_error)
    errors.extend(check_dependencies(module_finder))
    return errors


def format_errors(errors):
    """Format preflight failures for a terminal or launcher error dialog."""
    return "EX-Installer cannot start:\n\n" + "\n".join(f"- {error}" for error in errors)
