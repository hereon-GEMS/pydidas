# This file is part of pydidas.
#
# Copyright 2024 - 2025, Helmholtz-Zentrum Hereon
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
Module with the Hdf5singleFileLoader Plugin which can be used to load
images from single Hdf5 files.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2024 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["Hdf51dProfileLoader"]

import numpy as np

from pydidas.core import Dataset, UserConfigError, get_generic_param_collection
from pydidas.core.utils import copy_docstring, get_hdf5_metadata
from pydidas.data_io import import_data
from pydidas.plugins import InputPlugin1d
from pydidas.widgets.plugin_config_widgets.plugin_config_widget_with_custom_xscale import (
    PluginConfigWidgetWithCustomXscale,
)


class Hdf51dProfileLoader(InputPlugin1d):
    """
    Load 1d profiles from Hdf5 data files.

    This class is designed to load image data from a series of hdf5 file. The file
    series is defined through the SCAN's base directory, filename pattern and
    start index.

    The final filename is
    <SCAN base directory>/<SCAN name pattern with index substituted for hashes>.

    The dataset in the Hdf5 file is defined by the hdf5_key Parameter.

    A region of interest and binning can be supplied to apply directly to the raw
    profile.

    Parameters
    ----------
    hdf5_key : str, optional
        The key to access the hdf5 dataset in the file. The default is entry/data/data.
    profiles_per_file : int, optional
        The number of images per file. If -1, pydidas will auto-discover the number
        of images per file based on the first file. The default is -1.
    file_stepping : int, optional
        The stepping width through all files in the file list, determined
        by fist and last file. The default is 1.
    """

    plugin_name = "HDF5 1d profile loader"
    default_params = get_generic_param_collection(
        "hdf5_key",
        "use_custom_xscale",
        "x0_offset",
        "x_delta",
        "x_label",
        "x_unit",
        "hdf5_slicing_axis",
        "profiles_per_file",
        "file_stepping",
        "_counted_images_per_file",
    )
    advanced_parameters = InputPlugin1d.advanced_parameters.copy() + [
        "hdf5_slicing_axis",
        "profiles_per_file",
        "file_stepping",
    ]
    has_unique_parameter_config_widget = True

    def pre_execute(self):
        """
        Prepare loading images from a file series.
        """
        InputPlugin1d.pre_execute(self)
        self._prepare_hdf5_reading()
        self._standard_kwargs = {
            "dataset": self.get_param_value("hdf5_key"),
            "binning": self.get_param_value("binning"),
            "forced_dimension": 1,
            "import_pydidas_metadata": False,
        }
        self._config["xrange"] = None

    def _prepare_hdf5_reading(self):
        """Prepare reading the hdf5 files ."""
        _i_per_file = self.get_param_value("profiles_per_file")
        _slice_ax = self.get_param_value("hdf5_slicing_axis")
        if _i_per_file == -1:
            _i_per_file = (
                1
                if _slice_ax is None
                else get_hdf5_metadata(
                    self.get_filename(0), "shape", dset=self.get_param_value("hdf5_key")
                )[_slice_ax]
            )
        self.set_param_value("_counted_images_per_file", _i_per_file)
        self._index_func = lambda i: (
            None if _slice_ax is None else ((None,) * _slice_ax + (i,))
        )

    def get_frame(self, frame_index: int, **kwargs: dict) -> tuple[Dataset, dict]:
        """
        Load a frame and pass it on.

        Parameters
        ----------
        frame_index : int
            The frame index.
        **kwargs : dict
            Any calling keyword arguments. Can be used to apply a ROI or
            binning to the raw image.

        Returns
        -------
        _data : pydidas.core.Dataset
            The image data.
        kwargs : dict
            The updated kwargs for importing the frame.
        """
        _fname = self.get_filename(frame_index)
        _hdf_index = frame_index % self.get_param_value("_counted_images_per_file")
        kwargs = kwargs | self._standard_kwargs
        kwargs["indices"] = self._index_func(_hdf_index)

        _data = import_data(
            _fname,
            roi=self._get_own_roi(),
            **kwargs,
        )
        if self._config["xrange"] is None:
            self.calculate_xrange(_data.size)
        _data.axis_units = self._config["axis_units"]
        _data.axis_labels = self._config["axis_labels"]
        _data.axis_ranges = self._config["xrange"]
        return _data, kwargs

    def calculate_xrange(self, n_points: int):
        """
        Calculate the x-range for the data.
        """
        if self.params.get_value("use_custom_xscale"):
            self._config["axis_units"] = [self.params.get_value("x_unit")]
            self._config["axis_labels"] = [self.params.get_value("x_label")]
            self._config["xrange"] = [
                np.arange(n_points) * self.params.get_value("x_delta")
                + self.params.get_value("x0_offset")
            ]
        else:
            self._config["axis_units"] = ["channel"]
            self._config["axis_labels"] = ["detector x"]
            self._config["xrange"] = [np.arange(n_points)]

    @copy_docstring(InputPlugin1d)
    def get_filename(self, frame_index: int) -> str:
        """
        Get the input filename.

        For the full docstring, please refer to the
        :py:class:`pydidas.plugins.base_input_plugin.InputPlugin
        <InputPlugin>` class.
        """
        if self.filename_string == "":
            raise UserConfigError(
                "`pre_execute` has not been called for the Hdf5FileSeriesLoader plugin "
                "and no filename generator has been created."
            )
        _i_file = (
            frame_index // self.get_param_value("_counted_images_per_file")
        ) * self.get_param_value("file_stepping") + self._SCAN.get_param_value(
            "scan_start_index"
        )
        return self.filename_string.format(index=_i_file)

    def get_parameter_config_widget(self):
        """Get the parameter config widget for the plugin."""
        return PluginConfigWidgetWithCustomXscale
