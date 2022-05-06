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
Module with the ouptut Plugin base class.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ["OutputPlugin"]

import os

from ..core.constants import OUTPUT_PLUGIN
from ..core import get_generic_parameter
from .base_plugin import BasePlugin


class OutputPlugin(BasePlugin):
    """
    The base class for output (file saving / plotting) plugins.
    """

    plugin_type = OUTPUT_PLUGIN
    plugin_name = "Base output plugin"
    generic_params = BasePlugin.generic_params.get_copy()
    generic_params.add_param(get_generic_parameter("directory_path"))
    default_params = BasePlugin.default_params.get_copy()

    def pre_execute(self):
        """
        Prepare loading images from a file series.
        """
        self._path = self.get_param_value("directory_path")
        if not os.path.exists(self._path):
            os.makedirs(self._path)

    def _get_base_output_filename(self):
        """
        Get the output filename from the global frame index and the Plugin
        label.

        Returns
        -------
        str
            The full filename and path.
        """
        if self._config["global_index"] is None:
            raise KeyError(
                'The "global_index" keyword has not been set. '
                "The plugin does not know how to get the filename."
            )
        _label = self.get_param_value("label")
        if _label is None or _label == "":
            _name = f"node_{self.node_id:02d}_" + "{:06d}"
        else:
            _name = f"{_label}_" + "{:06d}"
        return os.path.join(self._path, _name.format(self._config["global_index"]))
