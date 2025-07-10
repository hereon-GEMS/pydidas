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
import time
from typing import Any

import numpy as np

from pydidas.contexts import ScanContext
from pydidas.core import Dataset, FileReadError, UserConfigError, get_generic_parameter
from pydidas.core.constants import INPUT_PLUGIN
from pydidas.plugins.base_plugin import BasePlugin


class InputPlugin(BasePlugin):
    """
    The base plugin class for input plugins.
    """

    plugin_type = INPUT_PLUGIN
    plugin_name = "Base input plugin"
    output_data_label = "Image intensity"
    output_data_unit = "counts"
    input_data_dim = None
    base_output_data_dim = 2
    generic_params = BasePlugin.generic_params.copy()
    generic_params.add_params(
        get_generic_parameter("binning"),
        get_generic_parameter("use_roi"),
        get_generic_parameter("roi_xlow"),
        get_generic_parameter("roi_xhigh"),
        get_generic_parameter("_counted_images_per_file"),
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

    def __init__(self, *args: tuple, **kwargs: Any):
        """
        Create a BasicPlugin instance.
        """
        BasePlugin.__init__(self, *args, **kwargs)
        self._SCAN = kwargs.get("scan", ScanContext())
        self.filename_string = ""
        self._config["pre_executed"] = False
        if self.base_output_data_dim == 2:
            self.add_params(
                get_generic_parameter("roi_ylow"),
                get_generic_parameter("roi_yhigh"),
            )

    @property
    def output_data_dim(self) -> int:
        """
        The output data dimension of the plugin.

        Returns
        -------
        int
            The output data dimension.
        """
        return self.base_output_data_dim + (
            1
            if self._SCAN.get_param_value("scan_frames_per_scan_point") > 1
            and self._SCAN.get_param_value("scan_multi_frame_handling") == "Stack"
            else 0
        )

    def pre_execute(self):
        """
        Run generic pre-execution routines.
        """
        self.update_filename_string()
        self._config["pre_executed"] = True

    def update_filename_string(self):
        """
        Set up the generator that can create the full file names to load images.

        The generic implementation only joins the base directory and filename pattern,
        as defined in the ScanContext class.
        """
        _basepath = self._SCAN.get_param_value("scan_base_directory", dtype=str)
        _pattern = self._SCAN.get_param_value("scan_name_pattern", dtype=str)
        _hash_indices = [i for i, char in enumerate(_pattern) if char == "#"]
        if _hash_indices and max(np.diff(_hash_indices)) > 1:
            raise UserConfigError(
                "The scan name pattern must only contain one consecutive group of "
                "hash characters (#)."
            )
        _len_pattern = _pattern.count("#")
        _base_str = os.path.join(_basepath, _pattern)
        if _len_pattern < 1:
            self.filename_string = _base_str
        else:
            self.filename_string = _base_str.replace(
                "#" * _len_pattern, "{index:0" + str(_len_pattern) + "d}"
            )

    def input_available(self, ordinal: int) -> bool:
        """
        Check whether a new input file is available.

        Note: This function returns False by default. It is intended to be
        used only for checks during live processing.

        Parameters
        ----------
        ordinal : int
            The frame index.

        Returns
        -------
        bool
            flag whether the file for the frame #<index> is ready for reading.
        """
        _frame_indices = self._SCAN.get_frame_indices_from_ordinal(ordinal)
        _last_index = _frame_indices[-1]
        _fname = self.get_filename(_last_index)
        if os.path.exists(_fname):
            try:
                _ = self.get_frame(_last_index)
            except FileReadError:
                time.sleep(0.05)
                return False
            return True
        return False

    def get_filename(self, frame_index: int) -> str:
        """
        Get the filename of the file associated with the frame index.

        Parameters
        ----------
        frame_index : int
            The index of the frame.

        Returns
        -------
        str
            The filename.
        """
        _file_counter = frame_index // self.get_param_value("_counted_images_per_file")
        _file_index = _file_counter * self._SCAN.get_param_value(
            "file_number_delta"
        ) + self._SCAN.get_param_value("file_number_offset")
        return self.filename_string.format(index=_file_index)

    def get_frame(self, frame_index: int, **kwargs: Any) -> Dataset:
        """
        Get the specified image frame (which does not necessarily correspond to the
        scan point index).

        Parameters
        ----------
        frame_index : int
            The index of the specific frame to be loaded.
        **kwargs : Any
            Keyword arguments passed for loading the frame.

        Returns
        -------
        pydidas.core.Dataset
            The image data frame.
        """
        raise NotImplementedError

    def execute(self, ordinal: int, **kwargs: Any) -> tuple[Dataset, dict]:
        """
        Import the data and pass it on after (optionally) handling image multiplicity.

        Parameters
        ----------
        ordinal : int
            The ordinal index of the scan point.
        **kwargs : Any
            Keyword arguments passed to the execute method.

        Returns
        -------
        Dataset
            The image data frame.
        kwargs : Any
            The updated kwargs.
        """
        if not self._config["pre_executed"]:
            raise UserConfigError(
                "The pre_execute method must be called before the execute method."
            )
        _frames = self._SCAN.get_frame_indices_from_ordinal(ordinal)
        if len(_frames) == 1:
            _data, kwargs = self.get_frame(_frames[0], **kwargs)
        else:
            _data, kwargs = self.read_multi_image(_frames, **kwargs)
        _data.data_label = self.output_data_label
        _data.data_unit = self.output_data_unit
        return _data, kwargs

    def read_multi_image(
        self, frame_indices: list[int, ...], **kwargs: Any
    ) -> tuple[Dataset, dict]:
        """
        Read multiple image frames and handle them according to the settings.

        Parameters
        ----------
        frame_indices : list[int, ...]
            The indices of the frames to be handled.
        **kwargs : Any
            Keyword arguments for the get_frame method.

        Returns
        -------
        Dataset
            The image data frame.
        kwargs : Any
            The updated kwargs.
        """
        _handling = self._SCAN.get_param_value("scan_multi_frame_handling")
        _factor = len(frame_indices) if _handling == "Average" else 1
        _data = None
        for _i, _frame_index in enumerate(frame_indices):
            _tmp_data, kwargs = self.get_frame(_frame_index, **kwargs)
            if _data is None:
                _shape = _tmp_data.shape
                if _handling == "Stack":
                    _shape = (len(frame_indices),) + _shape
                _data = Dataset(np.zeros(_shape, dtype=np.float32))
            if _handling == "Stack":
                _data[_i] = _tmp_data
            elif _handling == "Maximum":
                np.maximum(_data, _tmp_data, out=_data)
            else:  # Average or Sum
                _data += _tmp_data / _factor
        kwargs["frames"] = frame_indices
        return _data, kwargs


InputPlugin.register_as_base_class()
