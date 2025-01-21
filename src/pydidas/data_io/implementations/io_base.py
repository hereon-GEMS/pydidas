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
Module with the IoBase class which exporters/importers using the pydidas
metaclass-based registry should inherit from.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["IoBase"]


import os
from numbers import Integral
from pathlib import Path
from typing import Union

from numpy import amax, amin, ndarray

from pydidas.core import Dataset, FileReadError
from pydidas.core.utils import rebin
from pydidas.data_io.io_manager import IoManager
from pydidas.data_io.utils import RoiSliceManager


class IoBase(metaclass=IoManager):
    """
    Base class for Metaclass-based importer/exporters.
    """

    extensions_export = []
    extensions_import = []
    format_name = ""
    dimensions = []

    _roi_controller = RoiSliceManager()
    _data = None

    @classmethod
    def export_to_file(cls, filename: Union[Path, str], data: ndarray, **kwargs: dict):
        """
        Write the content to a file.

        This method needs to be implemented by the concrete subclass.

        Parameters
        ----------
        filename : str
            The filename of the file to be written.
        **kwargs : dict
            Any keyword arguments. Supported keywords must be specified by
            the specific implementation.
        """
        raise NotImplementedError

    @classmethod
    def import_from_file(cls, filename: Union[Path, str], **kwargs: dict) -> Dataset:
        """
        Restore the content from a file

        This method needs to be implemented by the concrete subclass.

        Parameters
        ----------
        filename: Union[Path, str]
            The filename of the data file to be imported.
        """
        raise NotImplementedError

    @classmethod
    def check_for_existing_file(cls, filename: Union[Path, str], **kwargs: dict):
        """
        Check if the file exists and if the overwrite flag has been set.

        Parameters
        ----------
        filename: Union[Path, str]
            The full filename and path.
        **kwargs : dict
            Any keyword arguments. Supported is 'overwrite' [bool], a flag to allow
            overwriting of existing files.

        Raises
        ------
        FileExistsError
            If a file with filename exists and the overwrite flag is not True.
        """
        _overwrite = kwargs.get("overwrite", False)
        if os.path.exists(filename) and not _overwrite:
            raise FileExistsError(
                f"The file `{filename}` exists and overwriting has not been confirmed."
            )

    @classmethod
    def get_data_range(cls, data: Dataset, **kwargs: dict):
        """
        Get the data range from the keyword arguments or the data values.

        Parameters
        ----------
        data : pydidas.core.Dataset
            The data to be exported.
        **kwargs : dict
            The keyword arguments. This method will only use the "data_range"
            keyword.

        Returns
        -------
        range : list
            The range with two entries for the lower and upper boundaries as
            numerical values.
        """
        _range = list(kwargs.get("data_range", (None, None)))
        if _range[0] is None:
            _range[0] = amin(data)
        if _range[1] is None:
            _range[1] = amax(data)
        return _range

    @classmethod
    def return_data(cls, **kwargs: dict) -> Dataset:
        """
        Return the stored data.

        Parameters
        ----------
        **kwargs : dict
            A dictionary of keyword arguments. Supported keyword arguments
            are: "datatype", "binning", "roi".
            "datatype" can be either "auto" for the native datatype or the
            specified type. "Binning" can be any integer number and "roi" can
            be either None or a 4-tuple of float.

        Raises
        ------
        ValueError
            If no data has been read.

        Returns
        -------
        _data : pydidas.core.Dataset
            The data in form of a pydidas Dataset (a subclassed numpy.ndarray).
        """
        _return_type = kwargs.get("datatype", "auto")
        _local_roi = kwargs.get("roi", None)
        _binning = kwargs.get("binning", 1)
        if cls._data is None:
            raise ValueError("No image has been read.")
        _data = cls._data
        if _local_roi is not None:
            cls._roi_controller.ndim = kwargs.get("ndim", 2)
            cls._roi_controller.roi = _local_roi
            _data = _data[cls._roi_controller.roi]
        if _binning != 1:
            _data = rebin(_data, int(_binning))
        if _return_type not in ("auto", _data.dtype):
            _data = _data.astype(_return_type)
        return _data

    @staticmethod
    def raise_filereaderror_from_exception(ex: Exception, filename: str):
        """
        Raise a FileReadError from the given Exception.

        Parameters
        ----------
        ex : Exception
            The original exception.
        filename : str
            The filename of the file causing the Exception.

        Raises
        ------
        FileReadError
            The new FileReadError.
        """
        _index = 1 if isinstance(ex.args[0], Integral) else 0
        if len(filename) > 60:
            filename = "[...]" + filename[-55:]
        _msg = (
            ex.__class__.__name__ + ": " + ex.args[_index] + f"\n\nFilename: {filename}"
        )
        raise FileReadError(_msg)
