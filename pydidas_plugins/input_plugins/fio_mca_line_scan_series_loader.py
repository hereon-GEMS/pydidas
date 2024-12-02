# This file is part of pydidas.
#
# Copyright 2023 - 2024, Helmholtz-Zentrum Hereon
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
Module with the FioMcaLineScanSeriesLoader Plugin which can be used to load
MCA spectral data
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2024, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["FioMcaLineScanSeriesLoader"]

import os
from pathlib import Path

import numpy as np

from pydidas.contexts import ScanContext
from pydidas.core import (
    Dataset,
    FileReadError,
    Parameter,
    ParameterCollection,
    UserConfigError,
    get_generic_parameter,
)
from pydidas.core.utils import CatchFileErrors, copy_docstring
from pydidas.plugins import InputPlugin, InputPlugin1d


FIO_MCA_READER_DEFAULT_PARAMS = ParameterCollection(
    get_generic_parameter("live_processing"),
    Parameter(
        "files_per_directory",
        int,
        -1,
        name="Files per directory",
        tooltip=(
            "The number of files in each directory. A value of "
            "'-1' will take the number of present files in the "
            "first directory."
        ),
    ),
    Parameter(
        "_counted_files_per_directory",
        int,
        -1,
        name="Files per directory",
        tooltip="The counted number of files in each directory.",
    ),
    Parameter(
        "fio_suffix",
        str,
        "_mca_s#.fio",
        name="FIO-file suffix",
        tooltip=("The file suffix for the individual MCA files."),
    ),
    Parameter(
        "use_absolute_energy",
        int,
        0,
        choices=[True, False],
        name="Use absolute energy scale",
        tooltip=("Use an absolute energy scale for the results."),
    ),
    Parameter(
        "energy_offset",
        float,
        0,
        name="Energy offset",
        unit="eV",
        tooltip=("The absolute offset in energy for the zeroth channel."),
    ),
    Parameter(
        "energy_delta",
        float,
        1,
        name="Channel energy Delta",
        unit="eV",
        tooltip=("The width of each energy channels in eV."),
    ),
)


SCAN = ScanContext()


class FioMcaLineScanSeriesLoader(InputPlugin1d):
    """
    Load data frames from a series of Fio files with MCA data.

    This plugin is designed to allow loading .fio files written by DESY's
    SPOCK for a number of line scans.

    Please note that each instrument might have different data defined in the
    fio file format and not all data might be readable.

    Parameters
    ----------
    directory_path : Union[str, pathlib.Path]
        The base path to the directory with all the scan subdirectories.
    filename_pattern : str
        The name and pattern of the sub-directories and the prefixes in the
        filename.
    live_processing : bool, optional
        Flag to toggle file system checks. In live_processing mode, checks
        for the size and existance of files are disabled. The default is False.
    file_stepping : int, optional
        The stepping width through all files in the file list, determined
        by fist and last file. The default is 1.
    filename_suffix : str, optional
        The end of the filename. The default is ".fio"
    files_per_directory : int, optional
        The number of files in each directory. This number determines when
        pydidas will start looking in the next directory. A number of -1 will
        automatically determine the number of files. The default is -1.
    use_absolute_energy : bool, optional
        Keyword to toggle an absolute energy scale for the channels. If False,
        pydidas will simply use the channel number. The default is False.
    energy_offset : float, optional
        The offset for channel zero, if the absolute energy scale is used.
        This value must be given in eV. The default is 0.
    energy_delta : float, optional
        The width of each energy channel. This value is given in eV and only
        used when the absolute energy scale is enabled. The default is 1.
    """

    plugin_name = "Fio MCA line scan series loader"
    default_params = FIO_MCA_READER_DEFAULT_PARAMS.copy()

    def __init__(self, *args: tuple, **kwargs: dict):
        super().__init__(*args, **kwargs)
        self.set_param_value("live_processing", False)
        self._config.update({"header_lines": 0})

    def pre_execute(self):
        """
        Prepare loading spectra from a file series.
        """
        InputPlugin1d.pre_execute(self)
        self._check_files_per_directory()
        self._determine_header_size()
        self._config["roi"] = self._get_own_roi()
        self._config["energy_scale"] = None

    def update_filename_string(self):
        """
        Set up the generator that can create the full file names to load images.
        """
        _basepath = self._SCAN.get_param_value("scan_base_directory", dtype=str)
        _pattern = self._SCAN.get_param_value("scan_name_pattern", dtype=str)
        _len_pattern = _pattern.count("#")
        if _len_pattern < 1:
            raise UserConfigError("No filename pattern detected in the Input plugin!")
        _pattern = _pattern.replace(
            "#" * _len_pattern, "{index0:0" + str(_len_pattern) + "d}"
        )
        _fio_suffix = self.get_param_value("fio_suffix").replace("#", "{index1:d}")
        self.filename_string = os.path.join(_basepath, _pattern, _pattern + _fio_suffix)

    def _check_files_per_directory(self):
        """
        Check the number of files in each directory to compose the filename
        correctly.
        """
        if self.get_param_value("files_per_directory") == -1:
            _nstart = self._SCAN.get_param_value("scan_start_index")
            _path = Path(self.filename_string.format(index0=_nstart, index1=1)).parent
            if not _path.is_dir():
                raise FileReadError(
                    "The given directory for the first batch of fio files does not "
                    "exist. Please check the scan base directory and naming "
                    f"pattern. \n\nDirectory name not found:\n{str(_path)}"
                )
            _nfiles = sum(1 for _name in _path.iterdir() if _name.is_file())
            self.set_param_value("_counted_files_per_directory", _nfiles)
            if self.get_param_value("_counted_files_per_directory") == 0:
                raise UserConfigError(
                    "There are no files in the given first directory. Please check the "
                    f"path. \nGiven path:\n{_path}"
                )
        else:
            self.set_param_value(
                "_counted_files_per_directory",
                self.get_param_value("files_per_directory"),
            )

    def _determine_header_size(self):
        """
        Determine the size of the header in lines.
        """
        _fname = self.get_filename(0)
        with CatchFileErrors(_fname):
            with open(_fname, "r") as _f:
                _lines = _f.readlines()
        _lines_total = len(_lines)
        _n_header = _lines.index("! Data \n") + 2
        _lines = _lines[_n_header:]
        while _lines[0].strip().startswith("Col"):
            _lines.pop(0)
            _n_header += 1
        self._config["header_lines"] = _n_header
        self._config["data_lines"] = _lines_total - _n_header

    def get_frame(self, index: int, **kwargs: dict) -> tuple[Dataset, dict]:
        """
        Get the frame for the given index.

        Parameters
        ----------
        index : int
            The index of the scan point.
        **kwargs : dict
            Keyword arguments for loading frames.

        Returns
        -------
        _dataset : pydidas.core.Dataset
            The loaded dataset.
        kwargs : dict
            The updated kwargs.
        """
        _fname = self.get_filename(index)
        with CatchFileErrors(_fname):
            _data = np.loadtxt(_fname, skiprows=self._config["header_lines"])
        if self._config["energy_scale"] is None:
            self._create_energy_scale()
        _dataset = Dataset(
            _data,
            axis_labels=["energy"],
            axis_units=[self._config["energy_unit"]],
            axis_ranges=[self._config["energy_scale"]],
        )
        if self._config["roi"] is not None:
            _dataset = _dataset[self._config["roi"]]
        return _dataset, kwargs

    def _create_energy_scale(self):
        """
        Create the energy scale to be applied to the return Dataset.

        Parameters
        ----------
        num_bins : int
            The number of bins of the detector.
        """
        if not self.get_param_value("use_absolute_energy"):
            self._config["energy_unit"] = "channels"
            self._config["energy_scale"] = np.arange(self._config["data_lines"])
            return
        self._config["energy_unit"] = "eV"
        self._config["energy_scale"] = np.arange(
            self._config["data_lines"]
        ) * self.get_param_value("energy_delta") + self.get_param_value("energy_offset")

    @copy_docstring(InputPlugin)
    def get_filename(self, index: int) -> str:
        """
        Get the filename for the given index.

        For the full docstring, please refer to the
        :py:class:`pydidas.plugins.base_input_plugin.InputPlugin
        <InputPlugin>` class.
        """
        _n_per_dir = self.get_param_value("_counted_files_per_directory")
        _pathindex = index // _n_per_dir + self._SCAN.get_param_value(
            "scan_start_index"
        )
        _fileindex = index % _n_per_dir + 1
        return self.filename_string.format(index0=_pathindex, index1=_fileindex)

    def get_raw_input_size(self) -> int:
        """
        Get the raw input size.

        Returns
        -------
        int
            The number of bins in the input data.
        """
        self.update_filename_string()
        if self.get_param_value("_counted_files_per_directory") < 1:
            self._check_files_per_directory()
        if self._config.get("data_lines", None) is None:
            self._determine_header_size()
        return self._config["data_lines"]
