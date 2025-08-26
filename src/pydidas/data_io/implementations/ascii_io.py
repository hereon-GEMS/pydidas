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

import time
import warnings
from datetime import datetime
from io import TextIOWrapper
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

        Returns
        -------
        data : pydidas.core.Dataset
            The data in the form of a pydidas Dataset (with embedded metadata)
        """
        _ext = get_extension(filename)
        with CatchFileErrors(filename), warnings.catch_warnings():
            warnings.simplefilter("ignore", UserWarning)
            if _ext == "chi":
                cls._data = cls.__import_chi(filename)
            elif _ext == "dat":
                cls._data = cls.__import_specfile(filename)
            elif _ext in ["txt", "csv"]:
                cls._data = cls.__import_txt(filename)
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
        _data_label, _ax_label, _ax_unit = decode_chi_header(filename)
        _data = np.loadtxt(filename, skiprows=4)
        return Dataset(
            _data[:, 1],
            axis_units=[_ax_unit],
            axis_labels=[_ax_label],
            axis_ranges=[_data[:, 0]],
            data_label=_data_label,
        )

    @classmethod
    def __import_specfile(cls, filename: Path | str) -> Dataset:
        """
        Import a SpecFile (.dat) file.

        Parameters
        ----------
        filename : Path | str
            The filename of the SpecFile to be imported.

        Returns
        -------
        pydidas.core.Dataset
            The imported data.
        """
        _labels, _units = decode_specfile_header(filename)
        _data_label = _labels.pop(-1)
        _data_unit = _units.pop(-1)
        _imported_data = np.loadtxt(filename, comments="#")
        _data = _imported_data[:, 1:].squeeze()
        _ax_ranges = [_imported_data[:, 0], np.arange(_imported_data.shape[1] - 1)][
            : _data.ndim
        ]
        return Dataset(
            _data,
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
        _data = np.loadtxt(filename, comments="#", delimiter=None)
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

    @classmethod
    def export_to_file(cls, filename: str | Path, data: np.ndarray, **kwargs: Any):
        """
        Export data to file in ASCII format.

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

        """
        cls.check_for_existing_file(filename, **kwargs)
        if not isinstance(filename, Path):
            filename = Path(filename)
        if not isinstance(data, Dataset):
            data = Dataset(data)
        _ext = get_extension(filename)
        _format = kwargs.get("format", "%.18e")
        _delimiter = kwargs.get("delimiter", "\t")
        if _ext == "chi":
            _header = cls.__create_chi_header(filename, data)
        elif _ext == "txt":
            _header = cls.__create_txt_header(filename, data)
        elif _ext == "csv":
            _header = ""
            _delimiter = ","
        elif _ext == "dat":
            _header = cls.__create_specfile_header(filename, data)
        else:
            raise UserConfigError(f"File extension '{_ext}' not supported for export.")
        if data.ndim == 1:
            _data = np.column_stack((data.axis_ranges[0], data.array))
        else:
            _data = data.array
        with CatchFileErrors(filename):
            np.savetxt(
                filename, _data, delimiter=_delimiter, header=_header, fmt=_format
            )

    @classmethod
    def __create_chi_header(cls, filename: Path, data: Dataset, format: str = "%.8e"):
        """
        Export data to a chi file.

        Parameters
        ----------
        filename : Path
            The filename of the chi file to be written.
        data : pydidas.core.Dataset
            The data to be written to the chi file.
        format : str
            The numerical format for each number to be written.
        """
        if data.ndim > 1:
            raise UserConfigError("Only 1-d data can be saved as CHI")
        _header = f"{filename.name}\n"
        _header += data.get_axis_description(0, sep="(") + "\n"
        _header += data.get_data_description(sep="(") + "\n"
        _header += f"    {data.size}\n"
        return _header

    @staticmethod
    def __create_txt_header(filename: Path, data: Dataset, header=True, delimiter="\t"):
        """
        Export data to a text file.

        Parameters
        ----------
        filename : Path
            The filename of the text file to be written.
        data : pydidas.core.Dataset
            The data to be written to the text file.
        header : bool, optional
            A flag whether to write a metadata header. The default is True.
        delimiter : str, optional
            The delimiter to be used. The default is a tab.
        """
        _header = "# Metadata:\n"
        for key, val in data.metadata.items():
            _header += f"# {key}: {val}\n"
        if data.ndim == 1:
            _header += f"#\n# Axis label: {data.axis_labels[0]}\n"
            _header += f"# Axis unit: {data.axis_units[0]}\n"
        _header += f"# Data label: {data.data_label}\n"
        _header += f"# Data unit: {data.data_unit}\n"
        _header += "# --- end of metadata ---\n"
        _header += "# axis\tvalue\n"
        return _header

    @staticmethod
    def __create_specfile_header(filename: Path, data: Dataset):
        """
        Export data to a SpecFile (.dat) file.

        Parameters
        ----------
        filename : Path
            The filename of the SpecFile to be written.
        data : pydidas.core.Dataset
            The data to be written to the SpecFile.
        """
        if data.ndim > 2:
            raise UserConfigError("Only 1-d and 2-d data can be saved as SpecFile")
        _header = ""
        _time = datetime.datetime.now().strftime("%a %b %d %H:%M:%S %Y")
        _header = (
            f"#F {Path(filename).name}\n"
            f"#E {time.time()}\n"
            f"#D {_time}\n\n"
            "#S 1 pydidas results\n"
            f"#D {_time}\n"
            "#N 2\n"
        )
        if data.ndim == 1:
            _header += (
                f"#L {data.get_axis_description(0, sep='(')} "
                "{data.get_data_description('(')}\n"
            )
        else:
            _header += f"#L {data.get_data_description('(')}\n"
        return _header

    @staticmethod
    def __write_1d_data_as_ascii(file: TextIOWrapper, data: Dataset, delimiter="\t"):
        """Write 1d data to an ASCII file."""
        for x, y in zip(data.axis_ranges[0], data.array):
            file.write(f"{x:.6e}{delimiter}{y:.6e}\n")
