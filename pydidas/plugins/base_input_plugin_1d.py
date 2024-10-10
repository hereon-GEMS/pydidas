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
Module with the InputPlugin base class for 1 dim-data.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2024, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["InputPlugin1d"]


from ..contexts import ScanContext
from ..core import get_generic_parameter
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
    input_data_dim = None
    output_data_dim = 1
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

    def update_required_kwargs(self, kwargs: dict):
        """
        Update the kwargs dict in place.
        """
        if "roi" not in kwargs and self.get_param_value("use_roi"):
            kwargs["ndim"] = 1
            kwargs["roi"] = [
                slice(
                    self.get_param_value("roi_xlow"), self.get_param_value("roi_xhigh")
                )
            ]


InputPlugin1d.register_as_base_class()
