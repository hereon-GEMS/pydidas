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
Module with the IoBase class which exporters/importers using the pydidas
metaclass-based registry should inherit from.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2026, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["IoBase"]


from numbers import Integral
from pathlib import Path
from typing import Any, ClassVar

from numpy import amax, amin, ndarray

from pydidas.core import Dataset, FileReadError
from pydidas.core.utils import rebin
from pydidas.data_io.io_manager import IoManager
from pydidas.data_io.utils import RoiSliceManager


class IoBase(metaclass=IoManager):
    """
    Base class for Metaclass-based importer/exporters.
    """

    extensions_export: ClassVar[list[str]] = []
    extensions_import: ClassVar[list[str]] = []
    format_name: ClassVar[str] = ""
    dimensions: ClassVar[list[int]] = []
    allows_metadata_import: ClassVar[bool] = False

    _roi_controller: ClassVar[RoiSliceManager] = RoiSliceManager()
    _data = None

    @staticmethod
    def export_to_file(filename: Path | str, data: ndarray, **kwargs: Any) -> None:
        """
        Write the content to a file.

        This method needs to be implemented by the concrete subclass.

        Parameters
        ----------
        filename : Path or str
            The filename of the file to be written.
        data : ndarray
            The data to be written to the file. Pydidas Dataset objects will
            also export their metadata if the file format allows it.
        **kwargs : Any
            Any keyword arguments. Supported keywords must be specified by
            the specific implementation.
        """
        raise NotImplementedError

    @staticmethod
    def import_from_file(filename: Path | str, **kwargs: Any) -> Dataset:
        """
        Restore the content from a file

        This method needs to be implemented by the concrete subclass.

        Parameters
        ----------
        filename : Path or str
            The filename of the data file to be imported.
        **kwargs : Any
            Any keyword arguments. Supported keywords must be specified by
            the specific implementation.
        """
        raise NotImplementedError

    @staticmethod
    def return_data(data: Dataset, **kwargs: Any) -> Dataset:
        """
        Return the stored data.

        Parameters
        ----------
        data : Dataset
            The data to be returned.
        **kwargs : Any
            A dictionary of keyword arguments. Supported keyword arguments
            are:

            astype : type or 'auto', optional
                The datatype to which the data should be converted. If
                "auto", the data will be returned in its native datatype.
                The default is "auto".
            binning : int, optional
                The rebinning factor to be applied to the data. The default
                is 1.
            roi : tuple or None, optional
                A region of interest for cropping. Acceptable are both 4-tuples
                of integers in the format (y_low, y_high, x_low, x_high)
                and 2-tuples of integers or slice objects. If None, the full
                image will be returned. The default is None.

        Raises
        ------
        ValueError
            If no data has been read.

        Returns
        -------
        data : Dataset
            The data in the form of a pydidas Dataset.
        """
        _return_type = kwargs.get("astype", "auto")
        _local_roi = kwargs.get("roi", None)
        _binning = kwargs.get("binning", 1)
        if data is None:
            raise ValueError("No image has been read.")
        if _local_roi is not None:
            IoBase._roi_controller.ndim = kwargs.get("ndim", 2)
            IoBase._roi_controller.roi = _local_roi
            data = data[IoBase._roi_controller.roi]
        if _binning != 1:
            data = rebin(data, int(_binning))
        if _return_type not in ("auto", data.dtype):
            data = data.astype(_return_type)
        return data

    @staticmethod
    def get_data_range(data: ndarray, **kwargs: Any) -> list:
        """
        Get the data range from the keyword arguments or the data values.

        Parameters
        ----------
        data : np.ndarray
            The data to be inspected.
        **kwargs : Any
            The keyword arguments. This method will only use the
            `data_range` keyword.

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

    @staticmethod
    def raise_filereaderror_from_exception(ex: Exception, filename: str) -> None:
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
