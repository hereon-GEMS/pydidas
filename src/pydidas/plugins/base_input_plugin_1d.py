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
Module with the InputPlugin base class for 1 dim-data.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["InputPlugin1d"]


from pydidas.contexts import ScanContext
from pydidas.core import get_generic_parameter
from pydidas.core.constants import INPUT_PLUGIN
from pydidas.plugins.base_input_plugin import InputPlugin
from pydidas.plugins.base_plugin import BasePlugin


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

    def pre_execute(self):
        """
        Run generic pre-execution routines.
        """
        self.update_filename_string()
        self._config["n_multi"] = self._SCAN.get_param_value("scan_multiplicity")
        self._config["start_index"] = self._SCAN.get_param_value("scan_start_index")
        self._config["delta_index"] = self._SCAN.get_param_value("scan_index_stepping")


InputPlugin1d.register_as_base_class()
