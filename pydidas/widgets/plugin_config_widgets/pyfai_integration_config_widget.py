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
__all__ = ["PyfaiIntegrationConfigWidget"]

from qtpy import QtCore

from pydidas.core.constants import DEFAULT_PLUGIN_PARAM_CONFIG
from pydidas.core.utils import apply_qt_properties
from pydidas.widgets.factory import CreateWidgetsMixIn
from pydidas.widgets.parameter_config import ParameterEditCanvas


class PyfaiIntegrationConfigWidget(ParameterEditCanvas, CreateWidgetsMixIn):
    """
    Subtract a background image from the data.
    """

    def __init__(self, plugin, *args, **kwargs):
        super().__init__(*args, **kwargs)
        apply_qt_properties(self.layout(), contentsMargins=(0, 0, 0, 0))
        self.plugin = plugin
        for param in self.plugin.params.values():
            self.create_param_widget(param, **DEFAULT_PLUGIN_PARAM_CONFIG)
        if "azi_use_range" in self.param_composite_widgets:
            self.param_composite_widgets["azi_use_range"].io_edited.connect(
                self._toggle_azimuthal_ranges_visibility
            )
            self._toggle_azimuthal_ranges_visibility(
                self.plugin.get_param_value("azi_use_range")
            )
        if "rad_use_range" in self.param_composite_widgets:
            self.param_composite_widgets["rad_use_range"].io_edited.connect(
                self._toggle_radial_ranges_visibility
            )
        self._toggle_radial_ranges_visibility(
            self.plugin.get_param_value("rad_use_range")
        )

    @QtCore.Slot(str)
    def _toggle_azimuthal_ranges_visibility(self, new_selection):
        """
        Toggle the visibility of the plugin parameters for the azimuthal ranges.

        Parameters
        ----------
        new_selection : str
            The new selection of the azimuthal ranges Parameter.
        """
        _visibility = new_selection == "Specify azimuthal range"
        self.toggle_param_widget_visibility("azi_range_lower", _visibility)
        self.toggle_param_widget_visibility("azi_range_upper", _visibility)

    @QtCore.Slot(str)
    def _toggle_radial_ranges_visibility(self, new_selection):
        """
        Toggle the visibility of the plugin parameters for the radial ranges.

        Parameters
        ----------
        new_selection : str
            The new selection of the azimuthal ranges Parameter.
        """
        _visibility = new_selection == "Specify radial range"
        self.toggle_param_widget_visibility("rad_range_lower", _visibility)
        self.toggle_param_widget_visibility("rad_range_upper", _visibility)

    def update_edits(self):
        """
        Update the configuration fields of the plugin.
        """
        for param in self.plugin.params.values():
            self.update_widget_value(param.refkey, param.value)
