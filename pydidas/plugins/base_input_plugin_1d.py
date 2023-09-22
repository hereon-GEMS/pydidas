# This file is part of pydidas.
#
# Copyright 2023, Helmholtz-Zentrum Hereon
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
Module with the InputPlugin base class for 1 dim-data.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["InputPlugin1d"]

import numpy as np

from ..contexts import ScanContext
from ..core import Dataset, UserConfigError, get_generic_parameter
from ..core.constants import INPUT_PLUGIN
from .base_input_plugin import InputPlugin
from .base_plugin import BasePlugin


SCAN = ScanContext()


class InputPlugin1d(InputPlugin):
    """
    The base plugin class for input plugins.
    """

    plugin_type = INPUT_PLUGIN
    plugin_name = "Base input plugin 1d"
    input_data_dim = 1
    generic_params = BasePlugin.generic_params.copy()
    generic_params.add_params(
        get_generic_parameter("use_roi"),
        get_generic_parameter("roi_xlow"),
        get_generic_parameter("roi_xhigh"),
        get_generic_parameter("binning"),
    )
    default_params = InputPlugin.default_params.copy()
    advanced_parameters = ["use_roi", "roi_xlow", "roi_xhigh", "binning"]

    def __init__(self, *args: tuple, **kwargs: dict):
        """
        Create BasicPlugin instance.
        """
        BasePlugin.__init__(self, *args, **kwargs)
        self._SCAN = kwargs.get("scan", SCAN)
        self.filename_string = ""
        self._original_input_shape = None

    def calculate_result_shape(self):
        """
        Calculate the shape of the Plugin's results.
        """
        _n = self.get_raw_input_size()
        self._config["result_shape"] = (_n,)
        self._original_input_shape = (_n,)

    def pre_execute(self):
        """
        Run generic pre-execution routines.
        """
        self.update_filename_string()
        if self._original_input_shape is None:
            self.calculate_result_shape()
        self._config["n_multi"] = self._SCAN.get_param_value("scan_multiplicity")
        self._config["start_index"] = self._SCAN.get_param_value("scan_start_index")
        self._config["delta_index"] = self._SCAN.get_param_value("scan_index_stepping")

    def execute(self, index: int, **kwargs: dict):
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
        """
        if "n_multi" not in self._config:
            raise UserConfigError(
                "Calling plugin execution without prior pre-execution is not allowed."
            )
        _data = None
        kwargs
        if "roi" not in kwargs and self.get_param_value("use_roi"):
            kwargs["roi"] = [
                slice(
                    self.get_param_value("roi_xlow"), self.get_param_value("roi_xhigh")
                )
            ]
            kwargs["ndim"] = 1
        if self._config["n_multi"] == 1:
            _data, kwargs = self.get_frame(index, **kwargs)
            _data.data_label = self.output_data_label
            _data.data_unit = self.output_data_unit
            return _data, kwargs
        return self._handle_multi_image(index, **kwargs)

    def _handle_multi_image(self, index: int, **kwargs: dict) -> tuple[Dataset, dict]:
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
        _data = Dataset(np.zeros(self._original_input_shape, dtype=np.float32))
        for _frame_index in _frames:
            _tmp_data, kwargs = self.get_frame(_frame_index, **kwargs)
            if _handling == "Maximum":
                np.maximum(_data, _tmp_data, out=_data)
            else:
                _data += _tmp_data / _factor
        if _frames.size > 1:
            kwargs["frames"] = _frames
        _data.data_label = self.output_data_label
        _data.data_unit = self.output_data_unit
        return _data, kwargs

    def get_raw_input_size(self):
        """
        Get the number of data points in the raw input.

        Raises
        ------
        NotImplementedError
            This method needs to be implemented by the concrete subclass.

        Returns
        -------
        int
            The raw input size in data points.
        """
        raise NotImplementedError
