# This file is part of pydidas.
#
# Copyright 2024 - 2025, Helmholtz-Zentrum Hereon
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
__copyright__ = "Copyright 2024 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"


import math
import multiprocessing as mp
import os
import re
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Literal, Optional

import git


HELP_TEXT = """
Formatting checks for pydidas
=============================

Supported python modules are:
1. ruff `format` for automatic code re-formatting (use ruff-format).
2. ruff `check` for style guide checks (use ruff-check).
3. reuse for copyright information checking.
4. black for automatic code re-formatting.
5. isort for automatic import sorting.
6. flake8 for style guide checks.

In addition, functionality to check the correct copyright years and the version
numbers are available by using the `--copyright` and `--version` arguments,
respectively. These two are also included in the `--all` argument.

Usage
-----
Individual modules can be selected by the '--<modulename>' argument.
The copyright update can be selected with the '--copyright' argument.
All modules can be run with the '--all' argument.

If only a check but no update is desired, use the '--check' argument. Omitting
the '--check' argument will update files to comply with the formatting
(for black, isort and copyright).
A --silent argument can be used to supress various verbose messages.

Examples
--------
1. Check all formatting modules (without updating any files):
    python formatting_checks.py --all --check
2. Run black and update all files:
    python formatting_checks.py --black
"""
MODULE_TASK = {
    "ruff-format": "re-formatting",
    "ruff-check": "style guide checks",
    "reuse": "licensing check",
    "flake8": "style guide checks",
    "black": "re-formatting",
}
MODULE_ARGS = {
    "black": ["."],
    "isort": ["."],
    "flake8": [],
    "ruff-check": [],
    "ruff-format": [],
    "reuse": ["--root", ".", "lint"],
}
_DIRS_TO_SKIP = [
    ".git",
    "__pycache__",
    ".ruff_cache",
    ".idea",
    "pydidas.egg-info",
    "dist",
    "sphinx",
    ".pytest_cache",
]
_FILES_TO_SKIP = [".coverage"]


def _timed_print(input_str: str, new_lines: int = 0, verbose: bool = True):
    """
    Print the input with a prepended time string.

    Parameters
    ----------
    input_str : str
        The input to be printed.
    new_lines : int
        The number of new (empty) lines in front of the output. The default is 0.
    verbose : bool, optional
        Flag to enable printed output. The default is True.
    """
    if not verbose:
        return
    _epoch = time.time()
    _time = time.localtime(_epoch)
    _sec = _time[5] + _epoch - math.floor(_epoch)
    _time_str = (
        f"{_time[0]:04d}/{_time[1]:02d}/{_time[2]:02d} "
        f"{_time[3]:02d}:{_time[4]:02d}:{_sec:06.3f}"
    )
    print("\n" * new_lines + f"{_time_str}: {input_str}")


def run_module(module_name: Literal["black", "flake8", "isort", "reuse"]):
    """
    Run the given module in subprocess.

    Parameters
    ----------
    module_name : Literal["black", "flake8", "isort", "reuse"]
        The name of the module to be run.
    """
    if module_name not in [
        "black",
        "flake8",
        "isort",
        "reuse",
        "ruff-check",
        "ruff-format",
    ]:
        raise ValueError(f"Module '{module_name}' not supported.")
    _check = "--check" in sys.argv and module_name in ["ruff-format", "black", "isort"]
    _check_arg = (
        ["--check"]
        if _check
        else (
            ["--fix"]
            if ("--check" not in sys.argv and module_name == "ruff-check")
            else []
        )
    )
    _job_label = (
        f"{MODULE_TASK[module_name]} "
        + ("check " if _check else "")
        + f"with {module_name}"
    )
    _cmd_module = (
        module_name.split("-") if module_name.startswith("ruff") else [module_name]
    )
    _cmd = ["python", "-m"] + _cmd_module + MODULE_ARGS[module_name] + _check_arg
    try:
        _timed_print(f"Starting {_job_label}...", new_lines=1)
        subprocess.run(_cmd, check=True)
        _timed_print(f"Finished {_job_label}!")
    except subprocess.CalledProcessError:
        _timed_print(_job_label.capitalize() + " failed.", new_lines=1)


def check_version_tags(directory: Optional[Path] = None):
    """
    Check that all version tags are consistent.

    This function checks that the CHANGELOG.rst and CITATION.CFF are consistent
    with the version given in the pydidas.version.

    Parameters
    ----------
    directory : Path, optional
        The pydidas source directory. If not specified, will be located relative to
        this script file. The default is None.
    """
    _directory = Path(__file__).parent if directory is None else Path(directory)
    with open(_directory.joinpath("src", "pydidas", "version.py"), "r") as f:
        _line = [_line for _line in f.readlines() if _line.startswith("__version__")]
    _version = _line[0].split("=")[1].strip().strip('"')
    _timed_print("Starting version tag check.", new_lines=1)
    # check the CHANGELOG:
    with open(_directory.joinpath("CHANGELOG.rst"), "r") as f:
        _changelog_lines = f.readlines()
    _changelog_okay = f"v{_version}" in [_line.strip() for _line in _changelog_lines]
    if not _changelog_okay:
        _timed_print("The CHANGELOG does not include a current version tag.")
    # check the CITATION.cff:
    with open(_directory.joinpath("CITATION.cff"), "r") as f:
        _lines = [_line.strip() for _line in f.readlines()]
    _citation_okay = f"version: {_version}" in _lines
    if not _citation_okay:
        _timed_print("The CITATION.cff does not include the latest version tag.")
    # check the pydidas/version.py file which is required for consistency with old
    # updaters:
    with open(_directory.joinpath("pydidas", "version.py"), "r") as f:
        _line = [_line for _line in f.readlines() if _line.startswith("__version__")]
    _updater_version = _line[0].split("=")[1].strip().strip('"')
    _updater_version_okay = _updater_version == _version
    if not _updater_version_okay:
        _timed_print("The pydidas/version.py differs from the src version.")
    if not (_citation_okay and _changelog_okay and _updater_version_okay):
        sys.exit(1)
    _timed_print("Version tag check sucessfully concluded.")


class CopyrightYearUpdater:
    """
    Class to check the copyright year is up-to-date with the commit date.

    This class checks that the copyright written in the file matches the
    commit year for files in git version control. For other whitelisted files,
    it checks the modification year.

            Parameters
    ----------
    directory : Path, optional
        The directory to be checked. If None, this will take the parent directory
        of the class's file. The default is None,
    **kwargs : dict, optional
        Additional supported keywords are:

        check : bool, optional
            Flag to check the copyright only without updating it.
            The default is False:
        verbose : bool, optional
            Flag to write status messages. The default is True.
        git_only : bool, optional
            Flag to check for files in git version control only.
            The default is False.
        autorun : bool, optional
            Flag to automatically start the check on class instantiation.
            The default is True.
    """

    THIS_YEAR = datetime.fromtimestamp(time.time()).year
    SUFFIX_WHITELIST = [".py", ".rst", "", ".cff", ".md", ".in", ".toml"]
    _regex_full = re.compile("Copyright 20[0-9][0-9] ?- ?20[0-9][0-9],")
    _regex_short = re.compile("Copyright 20[0-9][0-9],")

    def _check_git_commit_year(self, fname: str) -> tuple[str, int]:
        """
        Check the commit year of a file in git.

        If there is not `git diff` to the current file, this method returns the commit
        year. If there is a difference, this method returns the current year.

        Parameters
        ----------
        fname : str
            The filename including the path.

        Returns
        -------
        str
            The input filename.
        int
            The timestamp (in years) of the last change
            (either commit or file difference).
        """
        if not Path(fname).is_file():
            return fname, -1
        try:
            _commit_epoch = self.__repo.git.log("-1", "--format=%at", fname)
            _commit_year = datetime.fromtimestamp(int(_commit_epoch)).year
            _diff = self.__repo.git.diff(fname)
            if _diff == "":
                return fname, _commit_year
            return fname, self.THIS_YEAR
        except (subprocess.CalledProcessError, ValueError):
            return fname, -1

    def __init__(self, directory: Optional[Path] = None, **kwargs):
        self._flags = {
            "check": kwargs.get("check", "--check" in sys.argv),
            "git-only": kwargs.get("git_only", "--git-only" in sys.argv),
            "autorun": kwargs.get("autorun", True),
        }
        self._flags["update"] = not self._flags["check"]
        self._flags["verbose"] = kwargs.get(
            "verbose", "--silent" not in sys.argv or self._flags["check"]
        )
        self._directory = (
            Path(__file__).parent if directory is None else Path(directory)
        )
        self.__repo = git.Repo(self._directory)
        self._timestamps = {}
        os.chdir(self._directory)
        if self._flags["autorun"]:
            self.run_copyright_check()

    def _print(self, string):
        """
        Print the given string if verbose.

        Parameters
        ----------
        string : str
            The input string to be printed.
        """
        if self._flags["verbose"]:
            print(string)

    def run_copyright_check(self):
        """
        Run the copyright check.
        """
        _timed_print(
            "Checking copyright information...",
            new_lines=1,
            verbose=self._flags["verbose"],
        )
        self._timestamps = self._get_all_file_timestamps()
        _outdated_files = self._check_and_update_file_copyrights()
        _timed_print("Copyright check finished.", verbose=self._flags["verbose"])
        if self._flags["check"] and len(_outdated_files) > 0:
            sys.exit(1)

    def _get_all_file_timestamps(self) -> dict:
        """
        Get all the files to be checked.

        Returns
        -------
        dict
            The filenames and timestamps for all files.
        """
        _timestamps = self._get_gitfile_timestamps()
        if not self._flags["git-only"]:
            _timestamps = _timestamps | self._get_unversioned_timestamps(_timestamps)
        return _timestamps

    def _get_gitfile_timestamps(self) -> dict:
        """
        Get the timestamps for git files.

        Returns
        -------
        dict
            The filenames and commit times of all files tracked by git.
        """
        _git_files = [
            self._directory.joinpath(_fname)
            for _fname in subprocess.check_output("git ls-files", shell=True)
            .decode()
            .strip()
            .split("\n")
            if self._directory.joinpath(_fname).suffix in self.SUFFIX_WHITELIST
        ]
        with mp.Pool() as _pool:
            _timestamps = {
                _item[0]: _item[1]
                for _item in _pool.imap_unordered(
                    self._check_git_commit_year, _git_files
                )
            }
        return _timestamps

    def _get_unversioned_timestamps(self, git_files: Optional[dict] = None) -> dict:
        """
        Get the timestamps of unversioned files.

        If a list of files in git version control is given, these files will be
        ignored.

        Parameters
        ----------
        git_files : list[Path], optional
            The list of files in git version control. Use None to check all
            files. The default is None.

        Returns
        -------
        dict
            The dictionary with all filenames and modification timestamps.
        """
        git_files = git_files if git_files is not None else dict()
        _unversioned_files = []
        for _base, _dirs, _files in os.walk(self._directory):
            for _dirname in _DIRS_TO_SKIP:
                if _dirname in _dirs:
                    _dirs.remove(_dirname)
            for _item in _files:
                _fname = Path(_base).joinpath(_item)
                if (
                    _fname.is_file()
                    and _fname.suffix.lower() in self.SUFFIX_WHITELIST
                    and _fname.name not in _FILES_TO_SKIP
                    and _fname not in git_files
                ):
                    _unversioned_files.append(_fname)
        return {
            _fname: datetime.fromtimestamp(os.path.getmtime(_fname)).year
            for _fname in _unversioned_files
        }

    def _check_and_update_file_copyrights(self) -> list[Path]:
        """
        Check the copyright year of all flagged files.

        Returns
        -------
        list[Path]
            A list of files which are outdated.
        """
        _outdated = []
        _hint = "Updated" if self._flags["update"] else "Outdated"
        for _fname, _timestamp in self._timestamps.items():
            if _timestamp < self.THIS_YEAR:
                continue
            with open(_fname, "r", encoding="utf-8") as f:
                try:
                    _contents = f.read()
                except UnicodeDecodeError:
                    _timed_print(
                        f"Error reading file: {_fname}", verbose=self._flags["verbose"]
                    )
            _original = _contents[:]
            _contents = re.sub(self._regex_full, self._update_long_regex, _contents)
            _contents = re.sub(self._regex_short, self._update_short_regex, _contents)
            if _contents == _original:
                continue
            _outdated.append(_fname)
            if self._flags["update"]:
                with open(_fname, "w", encoding="utf-8") as f:
                    f.write(_contents)
            self._print(f"{_hint} copyright on file {_fname}")
        return _outdated

    def _update_short_regex(self, match: re.Match) -> str:
        """
        Update the matched short copyright regex with the current year.

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
        if _input[-5:] == f"{self.THIS_YEAR},":
            return _input
        return match.group()[:-1] + f" - {self.THIS_YEAR},"

    def _update_long_regex(self, match: re.Match) -> str:
        """
        Update the matched long copyright regex with the current year.

        Parameters
        ----------
        match : re.Match
            The regular expression match.

        Returns
        -------
        str
            The updated string.
        """
        return match.group()[:-5] + f"{self.THIS_YEAR},"


if __name__ == "__main__":
    if "--check" in sys.argv and len(sys.argv) < 3:
        sys.argv.append("--all")
    if "--help" in sys.argv or len(sys.argv) < 2:
        print(HELP_TEXT)
        sys.exit()
    for _module in ["black", "isort", "flake8"]:
        if f"--{_module}" in sys.argv:
            run_module(_module)
    for _module in ["ruff-check", "ruff-format"]:
        if f"--{_module}" in sys.argv or "--all" in sys.argv or "--ruff" in sys.argv:
            run_module(_module)
    if "--reuse" in sys.argv or "--all" in sys.argv:
        run_module("reuse")
    if "--copyright" in sys.argv or "--all" in sys.argv:
        CopyrightYearUpdater()
    if "--version" in sys.argv or "--all" in sys.argv:
        check_version_tags()
