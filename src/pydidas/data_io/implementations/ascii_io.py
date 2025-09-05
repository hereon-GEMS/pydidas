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
from pydidas.core.constants import ASCII_EXPORT_EXTENSIONS, ASCII_IMPORT_EXTENSIONS
from pydidas.core.utils import CatchFileErrors, get_extension
from pydidas.core.utils.ascii_header_decoders import (
    decode_chi_header,
    decode_specfile_header,
    decode_txt_header,
)
from pydidas.data_io.implementations.io_base import IoBase


class AsciiIo(IoBase):
    """I/O implementation for ASCII files."""

    extensions_export = ASCII_EXPORT_EXTENSIONS
    extensions_import = ASCII_IMPORT_EXTENSIONS
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
            write_header : bool, optional
                A flag which indicates whether a metadata header should be
                written. The default is True.
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
        elif _ext in ["txt", "csv"]:
            _header = cls.__create_txt_header(data, _write_x_column)
            if _ext == "csv":
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
                header=_header if kwargs.get("write_header", True) else "",
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
    def __create_txt_header(data: Dataset, write_x_column: bool):
        """
        Export data to a text file.

        Parameters
        ----------
        data : Dataset
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
        data : Dataset
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
            x_column_index : int, optional
                The column number to be used as x-column. This is only used if
                x_column is True. The default is 0.

        Returns
        -------
        data : Dataset
            The data in the form of a pydidas Dataset (with embedded metadata)
        """
        _ext = get_extension(filename)
        _x_column = kwargs.get("x_column", _ext in ["dat"])
        _col_no = kwargs.get("x_column_index", 0)
        with CatchFileErrors(filename), warnings.catch_warnings():
            warnings.simplefilter("ignore", UserWarning)
            if _ext == "chi":
                cls._data = cls.__import_chi(filename)
            elif _ext == "dat":
                cls._data = cls.__import_specfile(
                    filename, _x_column, x_column_index=_col_no
                )
            elif _ext in ["txt", "csv"]:
                _delimiter = "," if _ext == "csv" else None
                cls._data = cls.__import_txt(
                    filename,
                    delimiter=_delimiter,
                    x_column=_x_column,
                    x_column_index=_col_no,
                )
            elif _ext == "fio":
                cls._data = cls.__import_fio(
                    filename, x_column=_x_column, x_column_index=_col_no
                )
            elif _ext == "asc":
                cls._data = cls.__import_asc(filename)
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
        Dataset
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
    def __import_specfile(
        cls, filename: Path | str, read_x_column: bool, x_column_index: int = 0
    ) -> Dataset:
        """
        Import a SpecFile (.dat) file.

        Parameters
        ----------
        filename : Path | str
            The filename of the SpecFile to be imported.
        read_x_column : bool
            A flag which indicates whether the first column of the data
            should be treated as x-axis.
        x_column_index : int, optional
            The column number to be used as x-column. This is only used if
            read_x_column is True. The default is 0.

        Returns
        -------
        Dataset
            The imported data.
        """
        _labels, _units = decode_specfile_header(
            filename, read_x_column, x_column_index=x_column_index
        )
        _data_label = _labels.pop(-1)
        _data_unit = _units.pop(-1)
        _imported_data = np.loadtxt(filename, comments="#")
        if read_x_column:
            if _imported_data.ndim == 1:
                raise UserConfigError(
                    "Cannot read x-column from 1d SPEC file. Please check the file "
                    "and assure it has two columns"
                )
            _ax_ranges: list[Any] = [_imported_data[:, x_column_index]]
            _imported_data = np.delete(_imported_data, x_column_index, axis=1).squeeze()
            if _imported_data.ndim == 2:
                _ax_ranges.append(np.arange(_imported_data.shape[1]))
        else:
            _ax_ranges = [np.arange(n) for n in _imported_data.shape]
        return Dataset(
            _imported_data,
            axis_units=_units,
            axis_labels=_labels,
            axis_ranges=_ax_ranges,
            data_label=_data_label,
            data_unit=_data_unit,
        )

    @classmethod
    def __import_txt(
        cls,
        filename: Path | str,
        delimiter: str | None = None,
        x_column: bool = True,
        x_column_index: int = 0,
    ) -> Dataset:
        """
        Import a text file.

        Parameters
        ----------
        filename : Path | str
            The filename of the text file to be imported.
        delimiter : str, optional
            The delimiter used in the text file. The default is None which
            resolves to any whitespace.
        x_column : bool, optional
            A flag which indicates whether the first column of the data
            should be treated as x-axis. This flag is only used if the text
            file does not contain a metadata header. The default is True.
        x_column_index : int, optional
            The column number (0-indexed) to be used as x-column if x_column
            is True. The default is 0.

        Returns
        -------
        Dataset
            The imported data.
        """
        _data = np.loadtxt(filename, comments="#", delimiter=delimiter)
        if _data.ndim == 1 and x_column:
            raise UserConfigError(
                "Cannot read x-column from 1d text file. Please check the file "
                "and assure it has two columns"
            )
        _metadata = decode_txt_header(filename)
        if x_column or _metadata.get("use_x_column", False):
            _axes: list[Any] = [_data[:, x_column_index]]
            _data = np.delete(_data, x_column_index, axis=1).squeeze()
        else:
            _axes: list[Any] = [None]
        _labels = [_metadata.get("ax_label", "")]
        _units = [_metadata.get("ax_unit", "")]
        if _data.ndim > 1:
            _axes.append(None)
            _labels.append("")
            _units.append("")
        return Dataset(
            _data,
            axis_ranges=_axes,
            axis_labels=_labels,
            axis_units=_units,
            data_label=_metadata.get("data_label", ""),
            data_unit=_metadata.get("data_unit", ""),
        )

    @classmethod
    def __import_fio(
        cls, filename: Path | str, x_column: bool = True, x_column_index: int = 0
    ) -> Dataset:
        """
        Import a .fio file.

        Parameters
        ----------
        filename : Path | str
            The filename of the .fio file to be imported.
        x_column : bool, optional
            A flag which indicates whether the first column of the data
            should be treated as x-axis. The default is True.
        x_column_index : int, optional
            The column number (0-indexed) to be used as x-column if
            x_column is True. The default is 0.

        Returns
        -------
        Dataset
            The imported data.
        """
        with open(filename, "r") as f:
            _lines = f.readlines()
        _n_lines = len(_lines)
        # discard all lines until the data section starts:
        while _lines:
            _line = _lines.pop(0)
            if _line.strip() == "%d":
                break
        _col_keys = {}
        while _lines:
            if _lines[0].startswith(" Col "):
                _i, _key = _lines.pop(0).strip().split()[1:3]
                _col_keys[int(_i) - 1] = _key.strip()
            else:
                break
        _len_header = _n_lines - len(_lines)
        _data = np.loadtxt(filename, comments="!", skiprows=_len_header)
        if _data.size == 0:
            raise ValueError("No data found in .fio file.")
        if _data.ndim == 1 and x_column:
            raise UserConfigError(
                "Cannot read x-column from 1d .fio file. Please check the file "
                "and assure it has two columns or disable x_column reading."
            )
        if x_column:
            _axes: list[Any] = [_data[:, x_column_index]]
            _data = np.delete(_data, x_column_index, axis=1).squeeze()
            _ax_labels = [_col_keys.pop(x_column_index, "unknown")]
            if _data.ndim == 1:
                _data_label = "".join(_col_keys.values())
            else:
                _data_label = "; ".join(_k for _k in _col_keys.values())
        else:
            _axes: list[Any] = [np.arange(_data.shape[0])]
            _ax_labels = ["index"]
            _data_label = "; ".join(_k for _k in _col_keys.values())
        if _data.ndim == 2:
            _axes.append(np.arange(_data.shape[1]))
            _ax_labels.append(
                "; ".join(f"{i}: {k}" for i, k in enumerate(_col_keys.values()))
            )
        return Dataset(
            _data, axis_ranges=_axes, axis_labels=_ax_labels, data_label=_data_label
        )

    @classmethod
    def __import_asc(cls, filename: Path | str) -> Dataset:
        """
        Import an .asc file.

        Parameters
        ----------
        filename : Path | str
            The filename of the .asc file to be imported.

        Returns
        -------
        Dataset
            The imported data.
        """
        with open(filename, "r") as f:
            _lines = f.readlines()
        _metadata = {
            _key.removeprefix("*").strip(): _val.strip()
            for _key, _val in (
                _line.split("=", 1)
                for _line in _lines
                if (_line.startswith("*") and "=" in _line)
            )
        }
        _data_str = ", ".join(
            _line.strip()
            for _line in _lines
            if (len(_line.strip()) > 0 and not _line.startswith("*"))
        )
        _data = np.fromstring(_data_str, sep=",")
        if "START" in _metadata and "STOP" in _metadata and "STEP" in _metadata:
            _x_start = float(_metadata["START"])
            _x_stop = float(_metadata["STOP"])
            _x_step = float(_metadata["STEP"])
            _x_data = np.arange(_x_start, _x_stop + _x_step, _x_step)
        else:
            _x_data = np.arange(_data.size)
            _metadata["SCAN_AXIS"] = "index"
        return Dataset(
            _data,
            axis_ranges=[_x_data],
            axis_labels=[_metadata.get("SCAN_AXIS", "")],
            axis_units=[_metadata.get("XUNIT", "")],
            data_label=_metadata.get("SAMPLE", ""),
            data_unit=_metadata.get("YUNIT", ""),
        )
