# This file is part of pydidas.
#
# pydidas is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Pydidas is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Pydidas. If not, see <http://www.gnu.org/licenses/>.

"""
Module with file utility functions pertaining to filenames.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = [
    "trim_filename",
    "get_extension",
    "find_valid_python_files",
    "get_file_naming_scheme",
]

import os
import re

from .iterable_utils import flatten
from ..exceptions import UserConfigError
from ..constants import FILENAME_DELIMITERS

_FILE_NAME_SCHEME_ERROR_STR = (
    "Could not interprete the filenames. The filenames do not differ in exactly one "
    "item, as determined by the delimiters. Delimiters considered are: "
    f"{FILENAME_DELIMITERS.split('|')}"
).replace("\\\\.", ".")


def trim_filename(path):
    """
    Trim a filename from a path if present.

    Parameters
    ----------
    path : str
        The file system path, including eventual filenames.

    Returns
    -------
    path : str
        The path without the filename.
    """
    path = os.path.dirname(path) if os.path.isfile(path) else path
    if os.sep == "/":
        path.replace("\\", os.sep)
    else:
        path.replace("/", os.sep)
    return path


def get_extension(path):
    """
    Get the extension to a file in the given path.

    Parameters
    ----------
    path : Union[pathlib.Path, str]
        The full filename and path

    Returns
    -------
    str
        The extracted file extension.
    """
    _ext = os.path.splitext(path)[1]
    if _ext != "":
        _ext = _ext[1:]
    return _ext


def find_valid_python_files(path):
    """
    Search for all python files in path and subdirectories.

    This method will search the specified path recursicely for all
    python files, defined as files with a .py extension.
    It will ignore protected files /directories (starting with "__")
    and hidden files / directories (starting with ".").

    Parameters
    ----------
    path : str
        The file system path to search.

    Returns
    -------
    list
        A list with the full filesystem path of python files in the
        directory and its subdirectories.
    """
    if path is None or not os.path.exists(path):
        return []
    path = trim_filename(path)
    _entries = [
        os.path.join(path, item)
        for item in os.listdir(path)
        if not (item.startswith("__") or item.startswith("."))
    ]
    _dirs = [item for item in _entries if os.path.isdir(item)]
    _files = [item for item in _entries if os.path.isfile(item)]
    _results = flatten(
        [find_valid_python_files(os.path.join(path, entry)) for entry in _dirs]
    )
    _results += [f for f in _files if f.endswith(".py")]
    return _results


def get_file_naming_scheme(filename1, filename2, ignore_leading_zeros=False):
    """
    Get the naming scheme (formattable string with 'index' variable) from two filenames.

    This method tries to find the single difference in the filenames and
    builds a formattable string from it.

    Parameters
    ----------
    filename1 : Union[pathlib.Path, str]
        The first filename (including the path).
    filename2 : Union[pathlib.Path, str]
        The second filename (including the path).
    ignore_leading_zeros : bool, optional
        Keyword to ignore leading zeros, i.e. to allow entries like '_12' and '_1255'
        to be compared. If False, the function will not accept the example above. The
        default is False.

    Returns
    -------
    fnames : str
        The formattable string (keyword "index") to get the file name.
    range : range
        The range iterable which points to all file names.
    """

    _path1, _fname1 = os.path.split(filename1)
    _fname2 = os.path.split(filename2)[1]
    _name_parts_1 = re.split(FILENAME_DELIMITERS, os.path.splitext(_fname1)[0])
    _name_parts_2 = re.split(FILENAME_DELIMITERS, os.path.splitext(_fname2)[0])
    _ext_1 = get_extension(_fname1)
    _ext_2 = get_extension(_fname2)
    if len(_name_parts_1) != len(_name_parts_2) or _ext_1 != _ext_2:
        raise UserConfigError(_FILE_NAME_SCHEME_ERROR_STR)
    _different_parts = []
    for _index, (_item, _item2) in enumerate(zip(_name_parts_1, _name_parts_2)):
        if _item != _item2 and (ignore_leading_zeros or len(_item) == len(_item2)):
            _different_parts.append(_index)
    if len(_different_parts) != 1:
        raise UserConfigError(_FILE_NAME_SCHEME_ERROR_STR)
    _change_index = _different_parts[0]
    _n = len(_name_parts_1[_change_index])
    _strindex = len("".join(_name_parts_1[:_change_index])) + _change_index
    _fnames = (
        _path1
        + os.sep
        + _fname1[:_strindex]
        + "{index:"
        + (f"0{_n}" if not ignore_leading_zeros else "")
        + "d}"
        + _fname1[_strindex + _n :]
    )
    _index1 = int(_name_parts_1[_change_index])
    _index2 = int(_name_parts_2[_change_index])
    return _fnames, range(_index1, _index2 + 1)
