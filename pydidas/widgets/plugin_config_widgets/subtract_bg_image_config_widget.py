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
Module with the SubtractBackgroundImageConfigWidget which is used by the
SubtractBackgroundImage plugin to modify its Parameters.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ["SubtractBackgroundImageConfigWidget"]

import os
from pathlib import Path

from qtpy import QtCore

from pydidas.core import Hdf5key
from pydidas.core.constants import (
    DEFAULT_PLUGIN_PARAM_CONFIG,
    DEFAULT_TWO_LINE_PLUGIN_PARAM_CONFIG,
    HDF5_EXTENSIONS,
)
from pydidas.core.utils import apply_qt_properties
from pydidas.widgets.factory import CreateWidgetsMixIn
from pydidas.widgets.parameter_config import ParameterEditCanvas


class SubtractBackgroundImageConfigWidget(ParameterEditCanvas, CreateWidgetsMixIn):
    """
    Subtract a background image from the data.
    """

    def __init__(self, plugin, *args, **kwargs):
        super().__init__(*args, **kwargs)
        apply_qt_properties(self.layout(), contentsMargins=(0, 0, 0, 0))
        self.plugin = plugin
        for param in self.plugin.params.values():
            _kwargs = (
                DEFAULT_TWO_LINE_PLUGIN_PARAM_CONFIG
                if param.dtype in [Hdf5key, Path]
                else DEFAULT_PLUGIN_PARAM_CONFIG
            )
            self.create_param_widget(param, **_kwargs)
        self.param_composite_widgets["bg_file"].io_edited.connect(
            self._toggle_hdf5_plugin_visibility
        )
        _start_vis = (
            os.path.splitext(self.plugin.get_param_value("bg_file", dtype=str))[1][1:]
            in HDF5_EXTENSIONS
        )
        self.toggle_param_widget_visibility("bg_hdf5_key", _start_vis)
        self.toggle_param_widget_visibility("bg_hdf5_frame", _start_vis)

    @QtCore.Slot(str)
    def _toggle_hdf5_plugin_visibility(self, new_file):
        """
        Toggle the visibility of the plugins for Hdf5 dataset and frame number.

        Parameters
        ----------
        new_file : str
            The filename of the newly selected file.
        """
        _visibility = os.path.splitext(new_file)[1][1:] in HDF5_EXTENSIONS
        self.toggle_param_widget_visibility("bg_hdf5_key", _visibility)
        self.toggle_param_widget_visibility("bg_hdf5_frame", _visibility)

    def update_edits(self):
        """
        Update the configuration fields of the plugin.
        """
        for param in self.plugin.params.values():
            self.update_widget_value(param.refkey, param.value)
