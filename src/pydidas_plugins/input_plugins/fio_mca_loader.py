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
Module with the FioMcaLineScanSeriesLoader Plugin which can be used to load
MCA spectral data
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["FioMcaLoader"]


import os

from pydidas.contexts import ScanContext
from pydidas.core import (
    Dataset,
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


class FioMcaLoader(InputPlugin1d):
    """
    Load 1d data from a series of .fio files with MCA data (in a single directory).

    This plugin is designed to allow loading .fio files written by Sardana which
    include a single row of data with the MCA spectrum.

    Please give the full path to the folder in the Scan settings and use
    a single hash key (#) in the filename pattern to indicate the index of the
    scan point (which do not have leading zeros).

    Please note that each instrument might have different data defined in the
    fio file format and not all data might be readable.

    Parameters
    ----------
    directory_path : Union[str, pathlib.Path]
        The base path to the directory with all the scan subdirectories.
    filename_pattern : str
        The name pattern of the filenames.
    live_processing : bool, optional
        Flag to toggle file system checks. In live_processing mode, checks
        for the size and existence of files are disabled. The default is False.
    file_stepping : int, optional
        The stepping width through all files in the file list, determined
        by fist and last file. The default is 1.
    filename_suffix : str, optional
        The end of the filename. The default is ".fio"
    use_custom_xscale : bool, optional
        Keyword to toggle an absolute energy scale for the channels. If False,
        pydidas will simply use the channel number. The default is False.
    x0_offset : float, optional
        The offset for channel zero, if the absolute energy scale is used.
        This value must be given in eV. The default is 0.
    x_delta : float, optional
        The width of each energy channel. This value is given in units and only
        used when the absolute x-scale is enabled. The default is 1.
    """

    plugin_name = "Fio MCA loader"
    default_params = get_generic_param_collection(
        "live_processing",
        "use_custom_xscale",
        "x0_offset",
        "x_delta",
        "x_label",
        "x_unit",
    )
    has_unique_parameter_config_widget = True

    def __init__(self, *args: tuple, **kwargs: dict):
        super().__init__(*args, **kwargs)
        self._config.update({"header_lines": 0})

    def pre_execute(self):
        """
        Prepare loading spectra from a file series.
        """
        InputPlugin1d.pre_execute(self)
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
        _pattern = _pattern.replace("#" * _len_pattern, "{index0:d}")
        self.filename_string = os.path.join(_basepath, _pattern)

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
        _index = self._SCAN.get_param_value("scan_start_index") + index
        return self.filename_string.format(index0=_index)

    def get_parameter_config_widget(self):
        """Get the parameter config widget for the plugin."""
        return PluginConfigWidgetWithCustomXscale
