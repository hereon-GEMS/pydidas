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
Module with the InputPlugin base class.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["InputPlugin"]


import os

import numpy as np

from pydidas.contexts import ScanContext
from pydidas.core import Dataset, UserConfigError, get_generic_parameter
from pydidas.core.constants import INPUT_PLUGIN
from pydidas.plugins.base_plugin import BasePlugin


SCAN = ScanContext()


class InputPlugin(BasePlugin):
    """
    The base plugin class for input plugins.
    """

    plugin_type = INPUT_PLUGIN
    plugin_name = "Base input plugin"
    output_data_label = "Image intensity"
    output_data_unit = "counts"
    input_data_dim = None
    output_data_dim = 2
    generic_params = BasePlugin.generic_params.copy()
    generic_params.add_params(
        get_generic_parameter("use_roi"),
        get_generic_parameter("roi_xlow"),
        get_generic_parameter("roi_xhigh"),
        get_generic_parameter("roi_ylow"),
        get_generic_parameter("roi_yhigh"),
        get_generic_parameter("binning"),
        get_generic_parameter("live_processing"),
    )
    default_params = BasePlugin.default_params.copy()
    advanced_parameters = [
        "use_roi",
        "roi_xlow",
        "roi_xhigh",
        "roi_ylow",
        "roi_yhigh",
        "binning",
    ]

    def __init__(self, *args: tuple, **kwargs: dict):
        """
        Create BasicPlugin instance.
        """
        BasePlugin.__init__(self, *args, **kwargs)
        self._SCAN = kwargs.get("scan", SCAN)
        self.filename_string = ""

    def prepare_carryon_check(self):
        """
        Prepare the checks of the multiprocessing carryon.

        By default, this gets and stores the file target size for live
        processing.
        """
        self._config["file_size"] = self.get_first_file_size()

    def get_first_file_size(self) -> int:
        """
        Get the size of the first file to be processed.

        Returns
        -------
        int
            The file size in bytes.
        """
        _fname = self.get_filename(0)
        self._config["file_size"] = os.stat(_fname).st_size
        return self._config["file_size"]

    def input_available(self, index: int) -> bool:
        """
        Check whether a new input file is available.

        Note: This function returns False by default. It is intended to be
        used only for checks during live processing.

        Parameters
        ----------
        index : int
            The frame index.

        Returns
        -------
        bool
            flag whether the file for the frame #<index> is ready for reading.
        """
        _fname = self.get_filename(index)
        if os.path.exists(_fname):
            return self._config["file_size"] == os.stat(_fname).st_size
        return False

    def pre_execute(self):
        """
        Run generic pre-execution routines.
        """
        self.update_filename_string()
        self._config["n_multi"] = self._SCAN.get_param_value("scan_multiplicity")
        self._config["start_index"] = self._SCAN.get_param_value("scan_start_index")
        self._config["delta_index"] = self._SCAN.get_param_value("scan_index_stepping")

    def get_filename(self, frame_index: int) -> str:
        """
        Get the filename of the file associated with the frame index.

        Parameters
        ----------
        frame index : int
            The index of the frame to be processed.

        Returns
        -------
        str
            The filename.
        """
        _index = frame_index * self._SCAN.get_param_value(
            "scan_index_stepping"
        ) + self._SCAN.get_param_value("scan_start_index")
        return self.filename_string.format(index=_index)

    def update_filename_string(self):
        """
        Set up the generator that can create the full file names to load images.

        The generic implementation only joins the base directory and filename pattern,
        as defined in the ScanContext class.
        """
        _basepath = self._SCAN.get_param_value("scan_base_directory", dtype=str)
        _pattern = self._SCAN.get_param_value("scan_name_pattern", dtype=str)
        _len_pattern = _pattern.count("#")
        if _len_pattern < 1:
            # raise UserConfigError("No filename pattern detected in the Input plugin!")
            self.filename_string = os.path.join(_basepath, _pattern)
            return
        self.filename_string = os.path.join(_basepath, _pattern).replace(
            "#" * _len_pattern, "{index:0" + str(_len_pattern) + "d}"
        )

    def execute(self, index: int, **kwargs: dict) -> tuple[Dataset, dict]:
        """
        Import the data and pass it on after (optionally) handling image multiplicity.

        Parameters
        ----------
        index : int
            The index of the scan point.
        **kwargs : dict
            Keyword arguments passed to the execute method.

        Returns
        -------
        pydidas.core.Dataset
            The image data frame.
        kwargs : dict
            The updated kwargs.
        """
        if "n_multi" not in self._config:
            raise UserConfigError(
                "Calling plugin execution without prior pre-execution is not allowed."
            )
        if self._config["n_multi"] == 1:
            _data, kwargs = self.get_frame(index, **kwargs)
            _data.data_label = self.output_data_label
            _data.data_unit = self.output_data_unit
            return _data, kwargs
        return self.handle_multi_image(index, **kwargs)

    def handle_multi_image(self, index: int, **kwargs: dict) -> tuple[Dataset, dict]:
        """
        Handle frames with an image multiplicity.

        Parameters
        ----------
        index : int
            The scan index.
        **kwargs : dict
            Keyword arguments for the get_frame method.

        Returns
        -------
        pydidas.core.Dataset
            The image data frame.
        kwargs : dict
            The updated kwargs.
        """
        _frames = self._config["n_multi"] * index + np.arange(self._config["n_multi"])
        _handling = self._SCAN.get_param_value("scan_multi_image_handling")
        _factor = self._config["n_multi"] if _handling == "Average" else 1
        _data = None
        for _frame_index in _frames:
            _tmp_data, kwargs = self.get_frame(_frame_index, **kwargs)
            if _data is None:
                _data = Dataset(np.zeros(_tmp_data.shape, dtype=np.float32))
            if _handling == "Maximum":
                np.maximum(_data, _tmp_data, out=_data)
            else:
                _data += _tmp_data / _factor
        if _frames.size > 1:
            kwargs["frames"] = _frames
        _data.data_label = self.output_data_label
        _data.data_unit = self.output_data_unit
        return _data, kwargs

    def get_frame(self, frame_index: int, **kwargs: dict) -> Dataset:
        """
        Get the specified image frame (which does not necessarily correspond to the
        scan point index).

        Parameters
        ----------
        frame_index : int
            The index of the specific frame to be loaded.
        **kwargs : dict
            Keyword arguments passed for loading the frame.

        Returns
        -------
        pydidas.core.Dataset
            The image data frame.
        """
        raise NotImplementedError


InputPlugin.register_as_base_class()
