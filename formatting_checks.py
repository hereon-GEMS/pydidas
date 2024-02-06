# This file is part of pydidas.
#
# Copyright 2024, Helmholtz-Zentrum Hereon
# SPDX-License-Identifier: GPL-3.0-only
#
# pydidas is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 3 as
# published by the Free Software Foundation.
#
# Pydidas is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Pydidas. If not, see <http://www.gnu.org/licenses/>.

"""Formatting script to avoid manually calling formatting modules."""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2024, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"


import fnmatch
import math
import os
import re
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path


THIS_YEAR = datetime.fromtimestamp(time.time()).year
SUFFIX_WHITELIST = [".py", ".rst", "", ".cff", ".md", ".in", ".toml"]
HELP_TEXT = """
Formatting checks for pydidas
=============================

Supported python modules are:
1. black for automatic code re-formatting.
2. isort for import re-organisation.
3. flake8 for style guide checks.
4. reuse for copyright information checking.

In addition, a function to update the copyright in changed files to be consistent
with the year of the change is included.

Usage
-----
Individual modules can be selected by the '--<modulename>' argument.
The copyright update can be selected with the '--copyright' argument.
All modules can be run with the '--all' argument.

If only a check but no update is desired, use the '--check' argument. Omitting
the '--check' argument will update files to comply with the formatting
(for black, isort and copyright).

Examples
--------
1. Check all formatting modules (without updating any files):
    python formatting_checks.py --all --check
2. Run black and update all files:
    python formatting_checks.py --black
"""


def _timed_print(input: str, new_lines: int = 0):
    """
    Print the input with a prepended time string.

    Parameters
    ----------
    input : str
        The input to be printed.
    new_lines : int
        The number of new (empty) lines in front of the output. The default is 0.
    """
    _epoch = time.time()
    _time = time.localtime(_epoch)
    _sec = _time[5] + _epoch - math.floor(_epoch)
    _time_str = (
        f"{_time[0]:04d}/{_time[1]:02d}/{_time[2]:02d} "
        f"{_time[3]:02d}:{_time[4]:02d}:{_sec:06.3f}"
    )
    print("\n" * new_lines + f"{_time_str}: {input}")


def run_black():
    """Run the black module for the current directory."""
    _check = "--check" in sys.argv
    _timed_print(
        "Starting re-formatting " + ("check " if _check else "") + "with black...",
        new_lines=1,
    )
    _cmd = ["python", "-m", "black", "."] + (["--check"] if _check else [])
    try:
        subprocess.run(_cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Formatting with black failed. Error: {e}")


def run_isort():
    """Run the isort module in the current directory."""
    _check = "--check" in sys.argv
    _timed_print(
        "Starting import re-organization "
        + ("check " if _check else "")
        + "with isort...",
        new_lines=1,
    )
    _cmd = ["python", "-m", "isort", "."] + (["--check"] if _check else [])
    try:
        subprocess.run(_cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Formatting with isort failed. Error: {e}")


def run_flake8():
    """Run the flake8 module in the current directory."""
    _timed_print("Running code style checks with flake8...", new_lines=1)
    try:
        subprocess.run(["python", "-m", "flake8"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Checking with flake8 failed. Error: {e}")


def run_reuse():
    """Run the reuse module in the current directory."""
    _timed_print("Checking pydidas licensing with reuse...", new_lines=1)
    try:
        subprocess.run(["python", "-m", "reuse", "--root", ".", "lint"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Checking with reuse failed. Error: {e}")


def _update_short_copyright(match: re.Match) -> str:
    """
    Update the matched short string with the current year.

    Parameters
    ----------
    match : re.Match
        The regular expression match.

    Returns
    -------
    str
        The updated string.
    """
    _input = match.group()
    if _input[-5:] == f"{THIS_YEAR},":
        return _input
    return match.group()[:-1] + f" - {THIS_YEAR},"


def _update_long_copyright(match: re.Match) -> str:
    """
    Update the matched string with the current year.

    Parameters
    ----------
    match : re.Match
        The regular expression match.

    Returns
    -------
    str
        The updated string.
    """
    return match.group()[:-5] + f"{THIS_YEAR},"


def run_copyright_check():
    """
    Update the copyright year based on the files modification date

    Usage:

    """

    _timed_print("Checking pydidas copyright information...", new_lines=1)

    _check_copyright = "--check" in sys.argv
    _display_copyright = "--display" in sys.argv or _check_copyright
    _update_copyright = not _check_copyright

    _copyright_outdated = False
    _regex_full = re.compile("Copyright 20[0-9][0-9][ ]?-[ ]?20[0-9][0-9],")
    _regex_short = re.compile("Copyright 20[0-9][0-9],")
    _this_dir = Path(__file__).parent
    os.chdir(_this_dir)
    _git_files = (
        subprocess.check_output("git ls-files", shell=True).decode().strip().split("\n")
    )
    _filelist = []
    for _base, _dirs, _files in os.walk(_this_dir):
        if ".git" in _dirs:
            _dirs.remove(".git")
        _matches = fnmatch.filter(_files, "*.py") + fnmatch.filter(_files, "*.rst")
        _filelist.extend(Path(_base).joinpath(_fname) for _fname in _matches)

    for _name in _git_files:
        _fname = _this_dir.joinpath(_name)
        if (
            _fname.is_file()
            and _fname not in _filelist
            and (_fname.suffix in SUFFIX_WHITELIST or "LICENSES" in str(_fname))
        ):
            _filelist.append(_fname)
    _filelist.remove(Path(__file__))
    for _fname in _filelist:
        if datetime.fromtimestamp(os.path.getmtime(_fname)).year < THIS_YEAR:
            continue
        with open(_fname, "r") as f:
            _contents = f.read()
        _original = _contents[:]
        _contents = re.sub(_regex_full, _update_long_copyright, _contents)
        _contents = re.sub(_regex_short, _update_short_copyright, _contents)
        if _contents == _original:
            continue
        _copyright_outdated = True
        if _display_copyright:
            print("Outdated copyright on file:", _fname)
        if _update_copyright:
            with open(_fname, "w") as f:
                f.write(_contents)
            print("Updated copyright on file:", _fname)
    if _check_copyright and _copyright_outdated:
        sys.exit(1)


if __name__ == "__main__":
    if "--check" in sys.argv and len(sys.argv) < 3:
        sys.argv.append("--all")
    if "--help" in sys.argv or len(sys.argv) < 2:
        print(HELP_TEXT)
        sys.exit()
    if "--black" in sys.argv or "--all" in sys.argv:
        run_black()
    if "--isort" in sys.argv or "--all" in sys.argv:
        run_isort()
    if "--flake8" in sys.argv or "--all" in sys.argv:
        run_flake8()
    if "--reuse" in sys.argv or "--all" in sys.argv:
        run_reuse()
    if "--copyright" in sys.argv or "--all" in sys.argv:
        run_copyright_check()
