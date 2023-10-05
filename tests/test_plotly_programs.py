"""Test all Plotly programs.

Chapter 15: Rolling dice
Chapter 16: Earthquake plots
Chapter 17: Python repos?

Overall approach:
- Copy code to a tmp dir.
- Modify code to save html file instead of opening tmp file in browser.
- Compare output files against reference files.

Notes:
- Need to call write_html() and generate full file, because that's what users see.
  - Also, that lets me open the html file and visually inspect what's generated.
  - But, the full file includes hashes and version numbers.
  - Some of those can be replaced with dummy values, some are harder or not necessary.
  - Also, can call write_html(include_plotly_js=False). Can't open and view file, but it's 
    the code that represents the plot. Call this in addition to full plot, and run assertion
    against this.
  - Can also call write_image(), and just do an image comparison.
    Should probably call this in addition to write_html(), not replacing it.
  - Should definitely write over fig.show().
  - If testing against write_html() even without js becomes too fragile as versions change,
    base all plotly testing on write_image(). If that's flaky, consider stripping metadata
    for file comparisons.

"""

from pathlib import Path
import os
import shutil
import filecmp

import pytest

import utils


die_programs = [
    'chapter_15/rolling_dice/die_visual.py',
    'chapter_15/rolling_dice/dice_visual.py',
    'chapter_15/rolling_dice/dice_visual_d6d10.py',
]

@pytest.mark.parametrize('test_file', die_programs)
def test_die_program(tmp_path, python_cmd, test_file):

    # Copy program file to temp dir.
    path = Path(__file__).parents[1] / test_file
    dest_path = tmp_path / path.name
    shutil.copy(path, dest_path)

    # Copy die.py to temp dir.
    path_die = path.parent / 'die.py'
    dest_path_die = tmp_path / 'die.py'
    shutil.copy(path_die, dest_path_die)

    # Modify the program file for testing.
    # Read all lines except fig.show().
    lines = dest_path.read_text().splitlines()[:-1]

    # Set random seed.
    lines.insert(0, 'import random')
    lines.insert(5, 'random.seed(23)')

    # Add the call to fig.write_html().
    output_filename = path.name.replace('.py', '.html')
    save_cmd = f"fig.write_html('{output_filename}')"
    lines.append(save_cmd)

    contents = '\n'.join(lines)
    dest_path.write_text(contents)

    # Run the program.
    os.chdir(tmp_path)
    cmd = f"{python_cmd} {path.name}"
    output = utils.run_command(cmd)

    # Verify the output file exists.
    output_path = tmp_path / output_filename
    assert output_path.exists()

    utils.replace_plotly_hash(output_path)

    reference_file_path = (Path(__file__).parent /
        'reference_files' / output_filename)
    assert filecmp.cmp(output_path, reference_file_path)