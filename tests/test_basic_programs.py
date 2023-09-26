"""Test all basic programs in Chapters 1-10.

- These are programs that don't involve input, or any difficult setup work.
- These tests are parametrized, so we just find each file, run it, and check 
    its output.

"""

import subprocess, sys
from pathlib import Path
from shlex import split
import sys

import pytest


basic_programs = [
    # Chapter 1
    ('chapter_01/hello_world.py', 'Hello Python world!'),

    # Chapter 2
    ('chapter_02/apostrophe.py', "One of Python's strengths is its diverse community."),
    ('chapter_02/comment.py', "Hello Python people!"),
]

@pytest.mark.parametrize('file_path, expected_output', basic_programs)
def test_basic_program(file_path, expected_output):
    """Test a program that only prints output."""
    root_dir = Path(__file__).parents[1]
    path = root_dir / file_path

    # Use the venv python.
    python_cmd = sys.prefix + "/bin/python"
    cmd = f"{python_cmd} {path}"

    # Run the command, and make assertions.
    cmd_parts = split(cmd)
    result = subprocess.run(cmd_parts,
        capture_output=True, text=True, check=True)
    output = result.stdout.strip()

    assert output == expected_output