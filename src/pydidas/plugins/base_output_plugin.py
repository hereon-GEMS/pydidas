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
Module with the OutputPlugin base class.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["OutputPlugin"]


import os

from pydidas.core import UserConfigError, get_generic_param_collection
from pydidas.core.constants import OUTPUT_PLUGIN
from pydidas.plugins.base_plugin import BasePlugin


class OutputPlugin(BasePlugin):
    """
    The base class for output (file saving / plotting) plugins.
    """

    plugin_type = OUTPUT_PLUGIN
    plugin_name = "Base output plugin"
    output_data_dim = None
    generic_params = BasePlugin.generic_params.copy()
    generic_params.add_params(
        get_generic_param_collection(
            "directory_path",
            "enable_overwrite",
            "output_fname_digits",
            "output_index_offset",
        )
    )
    default_params = BasePlugin.default_params.copy()
    advanced_parameters = ["output_fname_digits", "output_index_offset"]

    def pre_execute(self):
        """
        Prepare loading images from a file series.
        """
        self._path = self.get_param_value("directory_path")
        _overwrite = self.get_param_value("enable_overwrite")
        if self._path.is_dir() and len(os.listdir(self._path)) > 0 and (not _overwrite):
            raise UserConfigError(
                f"Configuration in `{self.plugin_name}` (node ID {self.node_id}) "
                "is invalid:\n"
                f"The given output path `{self._path}` (which resolves to "
                f"`{str(self._path.absolute())}` is not empty and overwriting "
                "was not enabled. Please check the path or enable overwriting of "
                "existing files."
            )
        if not os.path.exists(self._path) and not self.test_mode:
            os.makedirs(self._path)
        _label = self.get_param_value("label")
        _ndigits = self.get_param_value("output_fname_digits")
        if _ndigits < 1:
            raise UserConfigError(
                f"Configuration in `{self.plugin_name}` (node ID {self.node_id}) "
                "is invalid:\n"
                "The number of digits for the output filenames must be at least 1."
            )
        if self.node_id is None:
            raise UserConfigError(
                f"Configuration in `{self.plugin_name}` (node ID {self.node_id}) "
                "is invalid:\n"
                "The node ID is None. Please check the plugin configuration."
            )
        if _label == "":
            self._base_name = f"node_{self.node_id:02d}_" + "{:0" + str(_ndigits) + "d}"
        else:
            self._base_name = f"{_label}_" + "{:0" + str(_ndigits) + "d}"

    def get_output_filename(self, extension: str = "txt") -> str:
        """
        Get the output filename from the global frame index and the Plugin
        label.

        Parameters
        ----------
        extension : str, optional
            The file extension. The default is txt.

        Returns
        -------
        str
            The full filename and path.
        """
        _index = self._config["global_index"]
        if _index is None:
            raise UserConfigError(
                "The `global_index` keyword has not been set. "
                "The plugin does not know how to assemble the filename."
            )
        _index = _index + self.get_param_value("output_index_offset")
        return str(self._path / (self._base_name.format(_index) + f".{extension}"))


OutputPlugin.register_as_base_class()
