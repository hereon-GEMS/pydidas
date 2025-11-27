# This file is part of pydidas
#
# Copyright 2025, Helmholtz-Zentrum Hereon
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
# along with pydidas If not, see <http://www.gnu.org/licenses/>.

"""
Module with the AssociatedFileMixin which allows to associate a file to a class.

The AssociatedFileMixin class handles convenience functions like type checking.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["AssociatedFileMixin"]


from pathlib import Path
from typing import Any

from pydidas.core.constants import (
    ASCII_IMPORT_EXTENSIONS,
    BINARY_EXTENSIONS,
    HDF5_EXTENSIONS,
)
from pydidas.core.exceptions import UserConfigError
from pydidas.core.generic_parameters import get_generic_parameter
from pydidas.core.utils.file_utils import get_extension


class AssociatedFileMixin:
    """
    A mixin-class to associate a file to a class.

    Parameters
    ----------
    **kwargs : Any
        Additional keyword arguments. Supported kwargs are

        filename : Path or str
            An initial filename to associate with the class. If not given,
            the filename parameter will be initialized with an empty Path.
        filename_param : Parameter
            A Parameter instance to use as the filename parameter. If not given,
            a generic filename Parameter will be created.
    """

    def __init__(self, **kwargs: Any) -> None:
        self._filename_param = kwargs.get(
            "filename_param", get_generic_parameter("filename")
        )
        _fname = kwargs.get("filename", None)
        if _fname is not None:
            self._filename_param.value = _fname

    @property
    def _filetype(self) -> str:
        """The file type of the associated file."""
        _ext = get_extension(self._filename_param.value, lowercase=True)
        if _ext in HDF5_EXTENSIONS:
            return "hdf5"
        if _ext in BINARY_EXTENSIONS:
            return "binary"
        if _ext in ASCII_IMPORT_EXTENSIONS:
            return "ascii"
        return "generic"

    @property
    def hdf5_file(self) -> bool:
        """Flag whether the selected file is an HDF5 file."""
        return self._filetype == "hdf5"

    @property
    def binary_file(self) -> bool:
        """Flag whether the selected file is a raw binary file."""
        return self._filetype == "binary"

    @property
    def generic_file(self) -> bool:
        """Flag whether the selected file is a generic file."""
        return self._filetype == "generic"

    @property
    def ascii_file(self) -> bool:
        """Flag whether the selected file is an ASCII file."""
        return self._filetype == "ascii"

    @property
    def current_filename(self) -> str:
        """Get the current filename."""
        return str(self._filename_param.value)

    @property
    def current_filepath(self) -> Path:
        """Get the current filename as a Path instance."""
        return self._filename_param.value

    @current_filename.setter
    def current_filename(self, name: Path | str) -> None:
        """
        Set a new filename.

        Parameters
        ----------
        name : Path | str
            The full file system path to the new file.
        """
        if not isinstance(name, (str, Path)):
            raise UserConfigError(
                "The filename must be a string or Path instance. The given value "
                f"was: {name} (type: {type(name)})."
            )
        self._filename_param.value = name

    @current_filepath.setter
    def current_filepath(self, path: Path | str) -> None:
        """
        Set a new filepath.

        This setter is an alias for the current_filename setter.

        Parameters
        ----------
        path : Path | str
            The full file system path to the new file.
        """
        self.current_filename = path

    @property
    def current_filename_is_valid(self) -> bool:
        """Flag whether the current filename points to a valid file."""
        return self._filename_param.value.is_file()
