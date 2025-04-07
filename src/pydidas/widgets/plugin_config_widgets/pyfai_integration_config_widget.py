# This file is part of pydidas
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
# along with pydidas If not, see <http://www.gnu.org/licenses/>.

"""
Module with the PyfaiIntegrationConfigWidget which is a custom configuration widget
for pyFAI integration plugins.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["PyfaiIntegrationConfigWidget"]


from functools import partial
from typing import Literal, NewType

from qtpy import QtCore

from pydidas.widgets.plugin_config_widgets.generic_plugin_config_widget import (
    GenericPluginConfigWidget,
)
from pydidas.widgets.windows import SelectIntegrationRegionWindow


BasePlugin = NewType("BasePlugin", type)


class PyfaiIntegrationConfigWidget(GenericPluginConfigWidget):
    """
    The PyfaiIntegrationConfigWidget is the custom widget to modify the Parameters for
    pyFAI integration plugins.
    """

    def create_all_widgets(self):
        """
        Create all widgets for the plugin configuration.
        """
        self._window_edit = None
        self._window_show = None
        self.create_header()
        self.create_param_config_widgets()
        self.create_button(
            "but_show_integration_region",
            "Show selected integration region",
            clicked=partial(self._select_integration_region, allow_edit=False),
        )
        self.create_button(
            "but_select_integration_region",
            "Select integration region in image",
            clicked=partial(self._select_integration_region, allow_edit=True),
        )
        if self._use_advanced_params:
            self.create_advanced_param_config_widgets()

    def connect_signals(self):
        """Connect the signals of the widgets."""
        GenericPluginConfigWidget.connect_signals(self)
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
    def _toggle_azimuthal_ranges_visibility(
        self, new_selection: Literal["Specify azimuthal range", "Full detector"]
    ):
        """
        Toggle the visibility of the plugin parameters for the azimuthal ranges.

        Parameters
        ----------
        new_selection : Literal["Specify azimuthal range", "Full detector"]
            The new selection of the azimuthal ranges Parameter.
        """
        _visibility = new_selection == "Specify azimuthal range"
        self.toggle_param_widget_visibility("azi_range_lower", _visibility)
        self.toggle_param_widget_visibility("azi_range_upper", _visibility)

    @QtCore.Slot(str)
    def _toggle_radial_ranges_visibility(
        self, new_selection: Literal["Specify radial range", "Full detector"]
    ):
        """
        Toggle the visibility of the plugin parameters for the radial ranges.

        Parameters
        ----------
        new_selection : Literal["Specify radial range", "Full detector"]
            The new selection of the azimuthal ranges Parameter.
        """
        _visibility = new_selection == "Specify radial range"
        self.toggle_param_widget_visibility("rad_range_lower", _visibility)
        self.toggle_param_widget_visibility("rad_range_upper", _visibility)

    @QtCore.Slot()
    def _select_integration_region(self, allow_edit: bool = True):
        """
        Select the plugin's integration region interactively.

        Parameters
        ----------
        allow_edit : bool
            Flag to allow or disallow editing the integration region.
        """
        _window = getattr(self, "_window_edit" if allow_edit else "_window_show")
        if _window is None:
            _window = SelectIntegrationRegionWindow(
                self.plugin, only_show_roi=not allow_edit
            )
            _window.sig_roi_changed.connect(self.update_edits)
            _window.sig_about_to_close.connect(partial(self._toggle_io_mode, True))
            setattr(self, "_window_edit" if allow_edit else "_window_show", _window)
        self._toggle_io_mode(False)
        _window.show()

    @QtCore.Slot()
    def update_edits(self):
        """
        Update the configuration fields of the plugin.
        """
        for param in self.plugin.params.values():
            self.update_widget_value(param.refkey, param.value)
        self._toggle_azimuthal_ranges_visibility(
            self.plugin.get_param_value("azi_use_range")
        )
        self._toggle_radial_ranges_visibility(
            self.plugin.get_param_value("rad_use_range")
        )
        if self._window_show is not None and self._window_show.isVisible():
            self._window_show.close()
        if self._window_edit is not None and self._window_edit.isVisible():
            self._window_edit.close()
        self._toggle_io_mode(True)

    def _toggle_io_mode(self, enabled: bool):
        """
        Block the input/output and disable all Parameter widgets.

        Parameters
        ----------
        enabled : bool
            Flag whether the I/O shall be enabled.
        """
        for _widget in self.param_widgets.values():
            _widget.setEnabled(enabled)
        self._widgets["but_show_integration_region"].setEnabled(enabled)
        self._widgets["but_select_integration_region"].setEnabled(enabled)
