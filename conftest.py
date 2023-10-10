"""Root confest.py.

Bare calls to `$ pytest` are problematic because they try to run the tests
  in chapter_11/, and also some files that have test in the name that aren't
  formal tests.

This root conftest mainly attempts to remind me of the intended usage
  if I call pytest the wrong way.
"""

from pathlib import Path
import sys
import os

import pytest


def pytest_sessionstart(session):
    """Don't run from root dir.

    This is better than setting tests/ as default dir in pytest.ini.
      With that approach, running `pytest tests/test_plotly_programs.py -k python_repos` for example
      runs all of those twice: once for the default tests/ path, and once for the path I specified.

      I use specified paths enough that using pytest.ini will almost certainly get confusing.

    This approach does cause the error message to be printed twice, and I'm not sure how to easily 
      keep that from happening.
    """
    # First, check if "tests/" is in current pytest call.
    if any('tests' in arg for arg in sys.argv):
        # This is a valid call; return to exit this check.
        return

    # Skip this check for pytest-xdist workers.
    if "PYTEST_XDIST_WORKER" in os.environ:
        return

    # tests/ is not in pytest call; make sure it's running from a non-root dir.
    if Path.cwd().name == 'demo_testing_pcc_3e':
        msg = "\n  You can't call `pytest` from root dir."
        msg += "\n  Instead, cd to tests/ or call some form of `pytest tests/...`\n\n"
        pytest.exit(msg)