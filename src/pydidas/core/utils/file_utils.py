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
Module with file utility functions pertaining to filenames.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = [
    "trim_filename",
    "get_extension",
    "find_valid_python_files",
    "get_file_naming_scheme",
    "CatchFileErrors",
]


import os
import re
from numbers import Integral
from pathlib import Path
from typing import List, Tuple, Union

from pydidas.core.constants import FILENAME_DELIMITERS
from pydidas.core.exceptions import FileReadError, UserConfigError
from pydidas.core.utils.iterable_utils import flatten


_FILE_NAME_SCHEME_ERROR_STR = (
    "Could not interprete the filenames. The filenames do not differ in exactly one "
    "item, as determined by the delimiters. Delimiters considered are: "
    f"{FILENAME_DELIMITERS.split('|')}"
).replace("\\\\.", ".")


def trim_filename(path: Path) -> Path:
    """
    Trim a filename from a path if present.

    Parameters
    ----------
    path : pathlib.Path
        The file system path, including eventual filenames.

    Returns
    -------
    path : pathlib.Path
        The path without the filename.
    """
    return path.parent if path.is_file() else path


def get_extension(path: Union[Path, str], lowercase=False) -> str:
    """
    Get the extension to a file in the given path.

    Parameters
    ----------
    path : Union[pathlib.Path, str]
        The full filename and path
    lowercase : bool, optional
        Flag to get the extension as lower case string.

    Returns
    -------
    str
        The extracted file extension.
    """
    if path is None:
        return ""
    if isinstance(path, str):
        path = Path(path)
    _ext = path.suffix
    if _ext.startswith("."):
        _ext = _ext[1:]
    if lowercase:
        _ext.lower()
    return _ext


def find_valid_python_files(path: Path) -> List[Path]:
    """
    Search for all python files in path and subdirectories.

    This method will search the specified path recursicely for all
    python files, defined as files with a .py extension.
    It will ignore protected files /directories (starting with "__")
    and hidden files / directories (starting with ".").

    Parameters
    ----------
    path : Union[str, Path]
        The file system path to search.

    Returns
    -------
    list
        A list with the full filesystem path of python files in the
        directory and its subdirectories.
    """
    if isinstance(path, str):
        path = Path(path)
    if path is None or not path.exists():
        return []
    if path.is_file():
        if (
            not (path.stem.startswith("__") or path.stem.startswith("."))
            and path.suffix == ".py"
        ):
            return [path]
        return []
    path = trim_filename(path)
    _entries = [
        path.joinpath(_item)
        for _item in path.iterdir()
        if not (_item.name.startswith("__") or _item.name.startswith("."))
    ]
    _dirs = [_item for _item in _entries if _item.is_dir()]
    _files = [_item for _item in _entries if _item.is_file()]
    _results = flatten(
        [find_valid_python_files(path.joinpath(_entry)) for _entry in _dirs]
    )
    _results += [f for f in _files if f.suffix == ".py"]
    return _results


def get_file_naming_scheme(
    filename1: Union[Path, str],
    filename2: Union[Path, str],
    ignore_leading_zeros: bool = False,
) -> Tuple[str, range]:
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


class CatchFileErrors:
    """
    A context manager which allows to catch generic file reading errors.

    The CatchFileErrors context manager allows to raise file reading errors
    as pydidas' FileReadError exception. Additional

    Parameters
    ----------
    filename : Union[Path, str]
        The filename of the file to be handled.
    *additional_exceptions : tuple
        Additional exception types to be handled.
    raise_file_read_error : bool, optional
        Flag to raise the FileReadError exception. The default is True.
    error_suffix : str, optional
        A suffix to be added to the error message. The default is an empty string.
    """

    def __init__(
        self,
        filename: Union[Path, str],
        *additional_exceptions: tuple,
        raise_file_read_error=True,
        error_suffix: str = "",
    ):
        self._exceptions = additional_exceptions + (
            ValueError,
            FileNotFoundError,
            OSError,
        )
        self._filename = str(filename)
        self._raised_exception = False
        self._raise_file_read_error = raise_file_read_error
        self._exception_msg_suffix = error_suffix

    def __enter__(self):
        """
        Enter the context.

        The CatchFileErrors has an empty __enter__ method.
        """
        return self

    def __exit__(self, ex_type, ex_value, traceback):
        """
        Check the exception type and raise it as FileReadError.
        """
        self._raised_exception = ex_type is not None
        if ex_type is None:
            self._exception_msg = ""
            return
        if issubclass(ex_type, self._exceptions):
            _index = 1 if isinstance(ex_value.args[0], Integral) else 0
            if len(self._filename) > 60:
                self._filename = "[...]" + self._filename[-50:]
            _ex_repr = ex_value.args[_index].replace('"', "`").replace("'", "`")
            self._exception_msg = (
                f"{ex_type.__name__}: "
                + f"{_ex_repr} {self._exception_msg_suffix}"
                + f"\n\nFilename: {self._filename}"
            )
            if self._raise_file_read_error:
                raise FileReadError(self._exception_msg)
            return True

    def __call__(self):
        """
        Get the raised exception status.

        Returns
        -------
        bool
            The status of the raised exception.
        """
        return self._raised_exception

    @property
    def raised_exception(self) -> bool:
        """
        Get the raised exception status.

        Returns
        -------
        bool
            The status of the raised exception.
        """
        return self()

    @property
    def exception_message(self) -> str:
        """
        Get the exception message.

        Returns
        -------
        str
            The exception message.
        """
        return self._exception_msg
