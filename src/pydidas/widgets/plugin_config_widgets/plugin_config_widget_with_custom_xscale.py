# This file is part of pydidas.
#
# Copyright 2023 - 2026, Helmholtz-Zentrum Hereon
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
Module with the PluginConfigWidgetWithCustomXscale which is a custom
configuration widget for plugins with custom xscale parameters.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2026, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["PluginConfigWidgetWithCustomXscale"]


from qtpy import QtCore

from pydidas.widgets.plugin_config_widgets.generic_plugin_config_widget import (
    GenericPluginConfigWidget,
)


CUSTOM_X_PARAMS = ["x0_offset", "x_delta", "x_label", "x_unit"]


class PluginConfigWidgetWithCustomXscale(GenericPluginConfigWidget):
    """
    A custom widget to include a custom xscale for the plugin results.

    This widget displays or hides the parameters for the custom xscale based
    on the value of the custom xscale parameter.
    """

    def connect_signals(self) -> None:
        """Connect the signals to the slots."""
        GenericPluginConfigWidget.connect_signals(self)
        self.param_widgets["use_custom_xscale"].sig_new_value.connect(
            self._toggle_custom_scale
        )

    def finalize_init(self) -> None:
        """Finalize the initialization of the widget."""
        self._toggle_custom_scale(self.plugin.get_param_value("use_custom_xscale"))

    @QtCore.Slot(str)
    def _toggle_custom_scale(self, value: str) -> None:
        """
        Toggle the visibility of the custom xscale parameters.

        Parameters
        ----------
        value : str
            The value of the custom xscale parameter.
        """
        _show = value in [True, "True"]
        for param in CUSTOM_X_PARAMS:
            self.toggle_param_widget_visibility(param, _show)

    @QtCore.Slot()
    def update_plugin_config_edits(self) -> None:
        """Update the configuration fields of the plugin."""
        super().update_plugin_config_edits()
        self._toggle_custom_scale(self.plugin.get_param_value("use_custom_xscale"))
