"""Test all Matplotlib programs.

Chapter 15: Basic plots, random walks
Chapter 16: Weather plots

Overall approach:
- Copy code to a tmp dir.
- Modify code to call savefig() instead of plt.show().
- Compare output files against reference files.

"""

from pathlib import Path
import os
import filecmp
import shutil

import pytest

import utils


simple_plots = [
    'chapter_15/plotting_simple_line_graph/mpl_squares.py',
    'chapter_15/plotting_simple_line_graph/scatter_squares.py',
]

@pytest.mark.parametrize('test_file', simple_plots)
def test_simple_plots(tmp_path, python_cmd, test_file):
    # Copy program file to temp dir.
    src_path = Path(__file__).parents[1] / test_file

    dest_path = tmp_path / src_path.name
    shutil.copy(src_path, dest_path)

    # Replace plt.show() with savefig().
    contents = dest_path.read_text()
    save_cmd = "plt.savefig('output_file.png')"
    contents = contents.replace('plt.show()', save_cmd)
    # Uncomment this to verify that comparison fails for incorrect image:
    # contents = contents.replace('16', '32')
    dest_path.write_text(contents)


    # Run program from tmp path dir.
    os.chdir(tmp_path)
    cmd = f"{python_cmd} {dest_path.name}"
    output = utils.run_command(cmd)
    
    # Verify file was created, and that it matches reference file.
    output_path = tmp_path / 'output_file.png'
    assert output_path.exists()

    # Print output file path, so it's easy to find images.
    print("\n***** mpl_squares output:", output_path)

    reference_filename = src_path.name.replace('.py', '.png')
    reference_file_path = (Path(__file__).parent
            / 'reference_files' / reference_filename)
    assert filecmp.cmp(output_path, reference_file_path)

    # Verify text output.
    assert output == ''


def test_random_walk_program(tmp_path, python_cmd):
    # Copy rw_visual.py and random_walk.py.
    path_rwv = (Path(__file__).parents[1] /
        'chapter_15' / 'random_walks' / 'rw_visual.py')
    path_rw = path_rwv.parent / 'random_walk.py'

    dest_path_rwv = tmp_path / path_rwv.name
    dest_path_rw = tmp_path / path_rw.name

    shutil.copy(path_rwv, dest_path_rwv)
    shutil.copy(path_rw, dest_path_rw)

    # Modify rw_visual.py for testing.
    lines = dest_path_rwv.read_text().splitlines()[:26]

    # Remove while line.
    del lines[4:6]
    # Unindent remaining lines.
    lines = [line.lstrip() for line in lines]
    # Add command to write image file.
    save_cmd = "\nplt.savefig('output_file.png')"
    lines.append(save_cmd)
    # Add lines to seed random number generator.
    lines.insert(0, 'import random')
    lines.insert(4, '\nrandom.seed(23)')

    # Write modified rw_visual.py.
    contents = '\n'.join(lines)
    dest_path_rwv.write_text(contents)

    # Run the file.
    os.chdir(tmp_path)
    cmd = f"{python_cmd} {dest_path_rwv.name}"
    output = utils.run_command(cmd)

    # Verify file was created, and that it matches reference file.
    output_path = tmp_path / 'output_file.png'
    assert output_path.exists()

    # Print output file path, so it's easy to find images.
    print("\n***** rw_visual output:", output_path)

    reference_file_path = (Path(__file__).parent /
        'reference_files' / 'rw_visual.png')
    assert filecmp.cmp(output_path, reference_file_path)

    # Verify text output.
    assert output == ''