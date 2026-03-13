# This file is part of pydidas.
#
# Copyright 2023 - 2026, Helmholtz-Zentrum Hereon
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
__copyright__ = "Copyright 2023 - 2026, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = [
    "verify_file_exists",
    "verify_file_exists_and_extension_matches",
    "verify_filenames_have_same_parent",
    "verify_files_of_range_are_same_size",
]


from pathlib import Path

from numpy import array

from pydidas.core.exceptions import FileReadError, UserConfigError


def verify_file_exists(fname: Path | str) -> bool:
    """
    Check that a file exists and raise an Exception if not.

    Parameters
    ----------
    fname : Path or str
        The filename and path.

    Raises
    ------
    UserConfigError
        If the selected filename does not exist.
    """
    fname = Path(fname)
    if not fname.is_file():
        raise UserConfigError(
            f"The selected filename `{fname}` does not point to a valid file."
        )
    return True


def verify_file_exists_and_extension_matches(
    fname: Path, extensions: str | list[str]
) -> None:
    """
    Check that a file exists and has one of the given extensions.

    Parameters
    ----------
    fname : Path
        The full filename (including the path).
    extensions : str or list[str]
        The allowed file extension(s). A string can be given for a single
        extension or multiple extensions can be separated by a `;;' in a
        single string. Alternatively, a list of strings can be provided.

    Raises
    ------
    FileReadError
        If the selected filename does not exist or has an invalid
        extension.
    """
    if isinstance(extensions, str):
        extensions = [_ext.strip() for _ext in extensions.split(";;")]
    if not fname.is_file():
        raise FileReadError(f"The selected filename `{fname}` does not exist.")
    if fname.suffix not in extensions:
        raise FileReadError(
            f"The selected file `{fname.name}` does not have a valid "
            f"extension. Allowed extensions are: {extensions}"
        )


def verify_filenames_have_same_parent(
    filename1: Path | str, filename2: Path | str
) -> None:
    """
    Verify the given files are in the same directory.

    Parameters
    ----------
    filename1 : Path or str
        The path or filename of the first file.
    filename2 : Path or str
        The path or filename of the second file.

    Raises
    ------
    UserConfigError
        If the two files are not in the same directory.
    """
    filename1 = Path(filename1)
    filename2 = Path(filename2)
    if filename2.parent not in [filename1.parent, Path()]:
        raise UserConfigError(
            "The selected files are not in the same directory:\n"
            f"{filename1}\nand\n{filename2}"
        )


def verify_files_of_range_are_same_size(files: list[Path]) -> None:
    """
    Verify a range of files are all the same size.

    Parameters
    ----------
    files : list[Path]
        The list of Path objects with the file references.

    Raises
    ------
    UserConfigError
        If the files in the filelist are not all the same size.
    """
    _fsizes = array([_f.stat().st_size for _f in files])
    if _fsizes.std() > 0.0:
        raise UserConfigError("The selected files are not all of the same size.")
