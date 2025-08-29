# This file is part of pydidas.
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
# along with Pydidas. If not, see <http://www.gnu.org/licenses/>.

"""
Module with the TiffIo class for importing and exporting tiff data.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = []

import datetime
import time
import warnings
from pathlib import Path
from typing import Any

import numpy as np

from pydidas.core import Dataset, UserConfigError
from pydidas.core.utils import CatchFileErrors, get_extension
from pydidas.core.utils.ascii_header_decoders import (
    decode_chi_header,
    decode_specfile_header,
    decode_txt_header,
)
from pydidas.data_io.implementations.io_base import IoBase


class AsciiIo(IoBase):
    """I/O implementation for ASCII files."""

    extensions_export = ["txt", "csv", "chi", "dat"]
    extensions_import = ["txt", "csv", "chi", "dat", "asc", "fio"]
    format_name = "ASCII"
    dimensions = [1, 2]

    @classmethod
    def export_to_file(cls, filename: str | Path, data: np.ndarray, **kwargs: Any):
        """
        Export data to file in ASCII format.

        Note that for Datasets, the x-axis will always be written as a first
        column, unless specifically disabled via the "x_column=False" kwarg.
        For ndarrays, the default is to write only the array, without an
        x-column.
        The first axis of the Dataset will be used as x-axis, if the second
        axis should be used, the Dataset should be transposed for export.

        Parameters
        ----------
        filename : str | Path
            The filename
        data : np.ndarray
            The data to be written to file.
        **kwargs : Any
            Supported arguments are:

            overwrite : bool, optional
                Flag to allow overwriting of existing files. The default is False.
            x_column : bool, optional
                A flag which indicates whether the x-axis should be written as
                a first column. If False, only the data array will be written. The
                default is True.
        """
        cls.check_for_existing_file(filename, **kwargs)
        if data.ndim > 2:
            raise UserConfigError("Only 1-d and 2-d data can be saved as ASCII")
        if not isinstance(filename, Path):
            filename = Path(filename)
        _write_x_column = kwargs.get("x_column", isinstance(data, Dataset))
        data = data if isinstance(data, Dataset) else Dataset(data)
        _ext = get_extension(filename)
        _format = kwargs.get("format", "%.18e")
        _comment_prefix = "#"
        _delimiter = kwargs.get("delimiter", "\t")
        if _ext == "chi":
            if not _write_x_column:
                raise UserConfigError("CHI files always need an x-column.")
            _header = cls.__create_chi_header(filename, data)
            _comment_prefix = ""
        elif _ext == "txt":
            _header = cls.__create_txt_header(filename, data, _write_x_column)
        elif _ext == "csv":
            _header = ""
            _delimiter = ","
        elif _ext == "dat":
            _header = cls.__create_specfile_header(filename, data, _write_x_column)
        else:
            raise UserConfigError(f"File extension '{_ext}' not supported for export.")
        if _write_x_column:
            _data = np.column_stack((data.axis_ranges[0], data.array))
        else:
            _data = data.array
        with CatchFileErrors(filename):
            np.savetxt(
                filename,
                _data,
                delimiter=_delimiter,
                header=_header,
                fmt=_format,
                comments=_comment_prefix,
            )

    @classmethod
    def __create_chi_header(cls, filename: Path, data: Dataset):
        """
        Export data to a chi file.

        Parameters
        ----------
        filename : Path
            The filename of the chi file to be written.
        data : Dataset
            The data to be written to the chi file.
        """
        if data.ndim > 1:
            raise UserConfigError("Only 1-d data can be saved as CHI")
        _header = f"{filename.name}\n"
        _header += data.get_axis_description(0, sep="(") + "\n"
        _header += data.get_data_description(sep="(") + "\n"
        _header += f"    {data.size}\n"
        return _header

    @staticmethod
    def __create_txt_header(filename: Path, data: Dataset, write_x_column: bool):
        """
        Export data to a text file.

        Parameters
        ----------
        filename : Path
            The filename of the text file to be written.
        data : pydidas.core.Dataset
            The data to be written to the text file.
        write_x_column : bool
            A flag which indicates whether the output will be a single column,
            in which case no axis metadata will be written.
        """
        _header = " Metadata:\n"
        for key, val in data.metadata.items():
            _header += f"     {key}: {val}\n"
        if write_x_column:
            _header += f"\n Axis label: {data.axis_labels[0]}\n"
            _header += f" Axis unit: {data.axis_units[0]}\n"
        _header += f" Data label: {data.data_label}\n"
        _header += f" Data unit: {data.data_unit}\n"
        _header += f" First column is x-axis: {write_x_column}\n"
        _header += " --- end of metadata ---\n"
        _header += " axis\tvalue\n"
        return _header

    @staticmethod
    def __create_specfile_header(filename: Path, data: Dataset, write_x_column: bool):
        """
        Export data to a SpecFile (.dat) file.

        Parameters
        ----------
        filename : Path
            The filename of the SpecFile to be written.
        data : pydidas.core.Dataset
            The data to be written to the SpecFile.
        write_x_column : bool
            A flag which indicates whether a column with the x-axis will be written
            (as first column).
        """
        _header = ""
        _time = datetime.datetime.now().strftime("%a %b %d %H:%M:%S %Y")
        _ncols = (data.shape[1] if data.ndim > 1 else 1) + write_x_column
        _header = (
            f"F {Path(filename).name}\nE {time.time()}\nD {_time}\n\n"
            f"S 1 pydidas results\nD {_time}\nN {_ncols}\n"
        )
        if data.ndim == 1:
            _header += (
                f"L {data.get_axis_description(0, sep='(')} "
                f"{data.get_data_description('(')}\n"
            )
        else:
            _header += f"L {data.get_data_description('(')}\n"
        return _header

    @classmethod
    def import_from_file(cls, filename: Path | str, **kwargs: Any) -> Dataset:
        """
        Read data from an Ascii file.

        The decoder is based on the extensions.

        Parameters
        ----------
        filename : str | Path
            The filename of the file with the data to be imported.
        **kwargs : Any
            Supported arguments are:

            roi : Union[tuple, None], optional
                A region of interest for cropping. Acceptable are both 4-tuples
                of integers in the format (y_low, y_high, x_low, x_high) and
                2-tuples of integers or slice objects. If None, the full image
                will be returned. The default is None.
            returnType : Union[datatype, 'auto'], optional
                If 'auto', the image will be returned in its native data type.
                If a specific datatype has been selected, the image is converted
                to this type. The default is 'auto'.
            binning : int, optional
                The rebinning factor to be applied to the image. The default
                is 1.
            x_column : bool, optional
                A flag which indicates whether the first column of the data
                should be treated as x-axis. This flag is only used for
                importing .dat and .csv files or .txt files without a metadata
                header. The default is True for .dat and False for .csv and .txt
                files.

        Returns
        -------
        data : pydidas.core.Dataset
            The data in the form of a pydidas Dataset (with embedded metadata)
        """
        _ext = get_extension(filename)
        _read_x_column = kwargs.get("x_column", _ext in ["dat"])
        with CatchFileErrors(filename), warnings.catch_warnings():
            warnings.simplefilter("ignore", UserWarning)
            if _ext == "chi":
                cls._data = cls.__import_chi(filename)
            elif _ext == "dat":
                cls._data = cls.__import_specfile(filename, _read_x_column)
            elif _ext in ["txt", "csv"]:
                cls._data = cls.__import_txt(filename, _read_x_column)
            else:
                raise UserConfigError(
                    f"File extension '{_ext}' not supported for import."
                )
        return cls.return_data(**kwargs)

    @staticmethod
    def __import_chi(filename: Path | str) -> Dataset:
        """
        Import a chi file.

        Parameters
        ----------
        filename : Path |  str
            The filename of the chi file to be imported.

        Returns
        -------
        pydidas.core.Dataset
            The imported data.
        """
        _data_label, _data_unit, _ax_label, _ax_unit = decode_chi_header(filename)
        _data = np.loadtxt(filename, skiprows=4)
        return Dataset(
            _data[:, 1],
            axis_units=[_ax_unit],
            axis_labels=[_ax_label],
            axis_ranges=[_data[:, 0]],
            data_label=_data_label,
            data_unit=_data_unit,
        )

    @classmethod
    def __import_specfile(cls, filename: Path | str, read_x_column: bool) -> Dataset:
        """
        Import a SpecFile (.dat) file.

        Parameters
        ----------
        filename : Path | str
            The filename of the SpecFile to be imported.
        read_x_column : bool
            A flag which indicates whether the first column of the data
            should be treated as x-axis.

        Returns
        -------
        pydidas.core.Dataset
            The imported data.
        """
        _labels, _units = decode_specfile_header(filename)
        print("labels:", _labels)
        print("units:", _units)
        _data_label = _labels.pop(-1)
        _data_unit = _units.pop(-1)
        _imported_data = np.loadtxt(filename, comments="#")
        if read_x_column:
            if _imported_data.ndim == 1:
                raise UserConfigError(
                    "Cannot read x-column from 1d SPEC file. Please check the file "
                    "and assure it has two columns"
                )
            _ax_ranges = [_imported_data[:, 0]]
            _imported_data = _imported_data[:, 1:].squeeze()
        else:
            _ax_ranges = [np.arange(n) for n in _imported_data.shape]
            # _data = _imported_data[:, 1:].squeeze()
            # _ax_ranges = [_imported_data[:, 0]]
            # if _data.ndim > 1:
            #     _ax_ranges.append(np.arange(_data.shape[1]))
        print("axranges:", _ax_ranges)
        return Dataset(
            _imported_data,
            axis_units=_units,
            axis_labels=_labels,
            axis_ranges=_ax_ranges,
            data_label=_data_label,
            data_unit=_data_unit,
        )

    def __import_txt(cls, filename: Path | str) -> Dataset:
        """
        Import a text file.

        Parameters
        ----------
        filename : Path | str
            The filename of the text file to be imported.

        Returns
        -------
        pydidas.core.Dataset
            The imported data.
        """
        _data = np.loadtxt(
            filename, comments="#"
        )  # TODO: check if necessary: delimiter=None)
        if _data.shape[1] == 2:
            _metadata = decode_txt_header(filename)
            return Dataset(
                _data[:, 1],
                axis_ranges=[_data[:, 0]],
                axis_labels=[_metadata.get("ax_label", "axis_0")],
                axis_units=[_metadata.get("ax_unit", "")],
                data_label=_metadata.get("data_label", "data"),
                data_unit=_metadata.get("data_unit", ""),
            )
        return Dataset(_data)
