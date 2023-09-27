"""conftest.py for tests/ directory."""

import sys

import pytest


@pytest.fixture(scope='session')
def python_cmd():
    """Return the path to the venv Python interpreter."""
    return sys.prefix + "/bin/python"