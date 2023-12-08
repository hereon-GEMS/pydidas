# This file is part of pydidas.
#
# Copyright 2023, Helmholtz-Zentrum Hereon
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
__copyright__ = "Copyright 2023, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"


import subprocess

from pydidas.core.utils import timed_print


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
        print(f"Checking with flake8 failed. Error: {e}")


if __name__ == "__main__":
    run_black()
    run_isort()
    run_flake8()
    run_reuse()
