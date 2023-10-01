"""conftest.py for tests/ directory."""

from pathlib import Path

import pytest

import utils


def pytest_addoption(parser):
    parser.addoption(
        "--pygame-version", action="store",
        default=None,
        help="Pygame version to test"
    )


@pytest.fixture(scope='session')
def python_cmd():
    """Return the path to the venv Python interpreter."""
    return utils.get_python_cmd()


def pytest_sessionfinish(session, exitstatus):
    """Custom cleanup work."""
    python_cmd = utils.get_python_cmd()

    # Reset any libraries that had a different version installed
    #   during the test run.
    print("\n\n--- Resetting test venv ---\n")

    req_txt_path = Path(__file__).parents[1] / 'requirements.txt'
    req_txt_path = req_txt_path.as_posix()

    cmd = f"{python_cmd} -m pip install -r {req_txt_path}"
    # When run in the context of a test run, pip is leaving behind
    #   temp dirs on Windows that are causing errors.
    # They don't prevent the work from being done. The are just
    #   causing warnings that subprocess.run() chokes on.
    output = utils.run_command(cmd, check=False)

    changed_lines = [
        line for line in output.split('\n')
        if 'Requirement already satisfied' not in line
    ]

    if changed_lines:
        for line in changed_lines:
            print(line)
    else:
        print("  No packages were modified.")

    print("\n--- Finished resetting test venv ---\n")

    # Show which version of Python was used for tests.
    cmd = f"{python_cmd} --version"
    output = utils.run_command(cmd)

    print(f"\n***** Tests were run with: {output}")