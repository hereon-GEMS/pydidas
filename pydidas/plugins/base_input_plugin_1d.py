# This file is part of pydidas.
#
# pydidas is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
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
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ["InputPlugin1d"]

import numpy as np

from ..core import get_generic_parameter, UserConfigError
from ..core.constants import INPUT_PLUGIN
from ..experiment import SetupScan
from .base_plugin import BasePlugin
from .base_input_plugin import InputPlugin


SCAN = SetupScan()


class InputPlugin1d(InputPlugin):
    """
    The base plugin class for input plugins.
    """

    plugin_type = INPUT_PLUGIN
    plugin_name = "Base input plugin 1d"
    input_data_dim = 1
    generic_params = BasePlugin.generic_params.get_copy()
    generic_params.add_params(
        get_generic_parameter("use_roi"),
        get_generic_parameter("roi_xlow"),
        get_generic_parameter("roi_xhigh"),
        get_generic_parameter("binning"),
    )
    default_params = InputPlugin.default_params.get_copy()

    def __init__(self, *args, **kwargs):
        """
        Create BasicPlugin instance.
        """
        BasePlugin.__init__(self, *args, **kwargs)
        self.filename_string = ""

    def calculate_result_shape(self):
        """
        Calculate the shape of the Plugin's results.
        """
        _n = self.get_raw_input_size()
        self._config["result_shape"] = (_n,)
        self._original_input_shape = (_n,)

    def execute(self, index, **kwargs):
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
        if "roi" not in kwargs and self.get_param_value("use_roi"):
            kwargs["roi"] = slice(
                self.get_param_value("roi_xlow"), self.get_param_value("roi_xhigh")
            )
        _frames = self._config["n_multi"] * self._config[
            "delta_index"
        ] * index + self._config["delta_index"] * np.arange(self._config["n_multi"])
        for _frame_index in _frames:
            if _data is None:
                _data, kwargs = self.get_frame(_frame_index, **kwargs)
            else:
                _data += self.get_frame(_frame_index, **kwargs)[0]
        if SCAN.get_param_value("scan_multi_image_handling") == "Average":
            _data = _data / self._config["n_multi"]
        if _frames.size > 1:
            kwargs["frames"] = _frames
        return _data, kwargs

    def get_raw_input_size(self):
        """
        Get the raw input size.

        Raises
        ------
        NotImplementedError
            This method needs to be implemented by the concrete subclass.

        Returns
        -------
        int
            The raw input size in bins.
        """
        raise NotImplementedError
