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
Module with the FioMcaLineScanSeriesLoader Plugin which can be used to load
MCA spectral data
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["FioMcaLineScanSeriesLoader"]


import os
from pathlib import Path

from pydidas.contexts import ScanContext
from pydidas.core import (
    Dataset,
    FileReadError,
    UserConfigError,
    get_generic_param_collection,
)
from pydidas.core.utils import copy_docstring
from pydidas.core.utils import fio_utils as fio
from pydidas.plugins import InputPlugin, InputPlugin1d
from pydidas.widgets.plugin_config_widgets.plugin_config_widget_with_custom_xscale import (
    PluginConfigWidgetWithCustomXscale,
)


SCAN = ScanContext()


class FioMcaLineScanSeriesLoader(InputPlugin1d):
    """
    Load 1d data from a series of Fio files with MCA data.

    This plugin is designed to allow loading .fio files written by Sardana which
    include a single row of data with the MCA spectrum.

    Data is expected in a series of directories with an identical number of
    files in each. The names of the directories and file prefixes in the
    directories are defined by the filename_pattern in the Scan settings whereas
    the suffix is defined by the fio_suffix parameter.

    For example, for loading a series of files with the following names
    /data/path/scan_0001/scan_0001_mca_s1.fio,
    /data/path/scan_0001/scan_0001_mca_s2.fio,
    ...
    /data/path/scan_0001/scan_0010_mca_s20.fio,

    to
    /data/path/scan_0010/scan_0010_mca_s1.fio,
    /data/path/scan_0010/scan_0010_mca_s2.fio,
    ...
    /data/path/scan_0010/scan_0010_mca_s20.fio,

    use the following settings:
    - Scan base directory: /data/path
    - Scan name pattern: scan_####
    - Fio file suffix: _mca_s#.fio (set by default)

    Please note that each instrument might have different data defined in the
    fio file format and not all data might be readable.

    Parameters
    ----------
    directory_path : Union[str, pathlib.Path]
        The base path to the directory with all the scan subdirectories.
    filename_pattern : str
        The name and pattern of the subdirectories and the prefixes in the
        filename.
    live_processing : bool, optional
        Flag to toggle file system checks. In live_processing mode, checks
        for the size and existence of files are disabled. The default is False.
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
    default_params = get_generic_param_collection(
        "live_processing",
        "files_per_directory",
        "_counted_files_per_directory",
        "fio_suffix",
        "use_custom_xscale",
        "x0_offset",
        "x_delta",
        "x_label",
        "x_unit",
    )

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
        fio.update_config_from_fio_file(self.get_filename(0), self._config, self.params)
        self._config["roi"] = self._get_own_roi()

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
            _i_start = self._SCAN.get_param_value("scan_start_index")
            _path = Path(self.filename_string.format(index0=_i_start, index1=1)).parent
            if not _path.is_dir():
                raise FileReadError(
                    "The given directory for the first batch of fio files does not "
                    "exist. Please check the scan base directory and naming "
                    f"pattern. \n\nDirectory name not found:\n{str(_path)}"
                )
            _n_files = sum(1 for _name in _path.iterdir() if _name.is_file())
            self.set_param_value("_counted_files_per_directory", _n_files)
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
        _dataset = fio.load_fio_spectrum(self.get_filename(index), self._config)
        return _dataset, kwargs

    @copy_docstring(InputPlugin)
    def get_filename(self, index: int) -> str:
        """
        Get the filename for the given index.

        For the full docstring, please refer to the
        :py:class:`pydidas.plugins.base_input_plugin.InputPlugin
        <InputPlugin>` class.
        """
        _n_per_dir = self.get_param_value("_counted_files_per_directory")
        _path_index = index // _n_per_dir + self._SCAN.get_param_value(
            "scan_start_index"
        )
        _file_index = index % _n_per_dir + 1
        return self.filename_string.format(index0=_path_index, index1=_file_index)

    def get_parameter_config_widget(self):
        """Get the parameter config widget for the plugin."""
        return PluginConfigWidgetWithCustomXscale
