# This file is part of pydidas.
#
# Copyright 2023 - 2025, Helmholtz-Zentrum Hereon
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

"""
The file_checks module includes functions to interact with files and perform some
basic checks for existence, size and same directory.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = [
    "check_hdf5_key_exists_in_file",
    "check_file_exists",
    "verify_files_in_same_directory",
    "verify_files_of_range_are_same_size",
    "file_is_writable",
]


import os
from pathlib import Path
from typing import List, Union

from numpy import array

from pydidas.core.exceptions import UserConfigError
from pydidas.core.utils.hdf5_dataset_utils import get_hdf5_populated_dataset_keys


def check_hdf5_key_exists_in_file(fname: Union[Path, str], key: str):
    """
    Verify that the selected file has a dataset with key.

    Parameters
    ----------
    fname : Union[Path, str]
        The filename and path.
    key : str
        The dataset key.

    Raises
    ------
    UserConfigError
        If the dataset key is not found in the hdf5 file.
    """
    key = key if key.startswith("/") else f"/{key}"
    dsets = get_hdf5_populated_dataset_keys(fname, 0, 0)
    if key not in dsets:
        raise UserConfigError(
            f"hdf5_key `{key}` is not a valid key for the file `{fname}`."
        )


def check_file_exists(fname: Union[Path, str]):
    """
    Check that a file exists and raise an Exception if not.

    Parameters
    ----------
    fname : Union[Path, str]
        The filename and path.

    Raises
    ------
    UserConfigError
        If the selected filename does not exist.
    """
    if isinstance(fname, str):
        fname = Path(fname)
    if not fname.is_file():
        raise UserConfigError(
            f"The selected filename `{fname}` does not point to a valid file."
        )


def verify_files_in_same_directory(
    filename1: Union[Path, str], filename2: Union[Path, str]
):
    """
    Verify the given files are in the same directory.

    Parameters
    ----------
    filename1 : Union[Path, str]
        The path or filename of the first file.
    filename2 : Union[Path, str]
        The path or filename of the second file.

    Raises
    ------
    OSError
        If the two files are not in the same directory.
    """

    filename1 = Path(filename1) if isinstance(filename1, str) else filename1
    filename2 = Path(filename2) if isinstance(filename2, str) else filename2
    if filename2.parent not in [filename1.parent, Path()]:
        raise UserConfigError(
            "The selected files are not in the same directory:\n"
            f"{filename1}\nand\n{filename2}"
        )


def verify_files_of_range_are_same_size(files: List[Path]):
    """
    Verify a range of files are all the same size.

    Parameters
    ----------
    files : List[Path]
        The list of Path objects with the file references.

    Raises
    ------
    UserConfigError
        If the files in the filelist are not all the same size.
    """
    _fsizes = array([_f.stat().st_size for _f in files])
    if _fsizes.std() > 0.0:
        raise UserConfigError("The selected files are not all of the same size.")


def file_is_writable(filename: Union[Path, str], overwrite=False) -> bool:
    """
    Check whether a file exists and the file is writable.

    If the filename does not exist, the function checks whether write
    permissions are granted for the directory in which the file would
    be created.

    Parameters
    ----------
    filename : Union[Path, str]
        The path or filename of the file to be checked.
    overwrite: bool
        Keyword to allow overwriting of existing files. Default: False

    Returns
    -------
    bool
        True if file exists and is writeable and overwrite or
        directory is writable. False in other cases.
    """
    filename = Path(filename) if isinstance(filename, str) else filename
    # check for existing files:
    if filename.is_file():
        return os.access(filename, os.W_OK) and overwrite
    # check if directory is writable:
    if not filename.is_dir():
        filename = filename.parent
    # if directory, check if writable:
    return filename.is_dir() and os.access(filename, os.W_OK)
