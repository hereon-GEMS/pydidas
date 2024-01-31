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
import os
import re
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

from pydidas.core.utils import timed_print


THIS_YEAR = datetime.fromtimestamp(time.time()).year
SUFFIX_WHITELIST = [".py", ".rst", "", ".cff", ".md", ".in", ".toml"]


def run_black():
    """Run the black module for the current directory."""
    timed_print("Starting re-formatting with black...", new_lines=1)
    try:
        subprocess.run(["python", "-m", "black", "."], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Formatting with black failed. Error: {e}")


def run_isort():
    """Run the isort module in the current directory."""
    timed_print("Starting import re-organization with isort...", new_lines=1)
    try:
        subprocess.run(["python", "-m", "isort", "."], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Formatting with isort failed. Error: {e}")


def run_flake8():
    """Run the flake8 module in the current directory."""
    timed_print("Running code style checks with flake8...", new_lines=1)
    try:
        subprocess.run(["python", "-m", "flake8"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Checking with flake8 failed. Error: {e}")


def run_reuse():
    """Run the reuse module in the current directory."""
    timed_print("Checking pydidas licensing with reuse...", new_lines=1)
    try:
        subprocess.run(["python", "-m", "reuse", "--root", ".", "lint"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Checking with reuse failed. Error: {e}")


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


def run_update_copyright():
    """Update the copyright year based on the files modification date"""
    timed_print("Checking pydidas copyright information...", new_lines=1)

    _check_copyright = "--check-copyright" in sys.argv
    _display_copyright = "--display-copyright" in sys.argv
    _update_copyright = "--update-copyright" in sys.argv or "--all" in sys.argv

    _regex_full = re.compile("Copyright 20[0-9][0-9][ ]?-[ ]?20[0-9][0-9],")
    _regex_short = re.compile("Copyright 20\d\d,")
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
        if _fname.suffix not in SUFFIX_WHITELIST or "LICENSES" in str(_fname):
            continue
        if _fname.is_file() and _fname not in _filelist:
            _filelist.append(_fname)
    _filelist.remove(Path(__file__))
    for _fname in _filelist:
        if datetime.fromtimestamp(os.path.getmtime(_fname)).year < THIS_YEAR:
            continue
        with open(_fname, "r") as f:
            _contents = f.read()
        _original = _contents[:]
        if _regex_full.search(_contents) is not None:
            _contents = re.sub(_regex_full, _update_long_copyright, _contents)
        if _regex_short.search(_contents) is not None:
            _contents = re.sub(_regex_short, _update_short_copyright, _contents)
        if _contents == _original:
            continue
        if _check_copyright:
            sys.exit(os.EX_SOFTWARE)
        if _display_copyright:
            print("Outdated copyright on file:", _fname)
        if _update_copyright:
            with open(_fname, "w") as f:
                f.write(_contents)
            print("Updated copyright on file:", _fname)


if __name__ == "__main__":
    if "--black" in sys.argv or "--all" in sys.argv:
        run_black()
    if "--isort" in sys.argv or "--all" in sys.argv:
        run_isort()
    if "--flake8" in sys.argv or "--all" in sys.argv:
        run_flake8()
    if "--reuse" in sys.argv or "--all" in sys.argv:
        run_reuse()
    if (
        "--check-copyright" in sys.argv
        or "--update-copyright" in sys.argv
        or "--display-copyright" in sys.argv
        or "--all" in sys.argv
    ):
        run_update_copyright()
