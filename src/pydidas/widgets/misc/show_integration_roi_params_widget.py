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
Module with the ShowIntegrationRoiParamsWidget class which allows to show the
integration region of an associated Plugin in the linked plot.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["ShowIntegrationRoiParamsWidget"]


from typing import Literal

from qtpy import QtCore

from pydidas.core import get_generic_param_collection
from pydidas.core.constants import (
    FONT_METRIC_PARAM_EDIT_WIDTH,
    POLICY_FIX_EXP,
    POLICY_MIN_MIN,
)
from pydidas.plugins import BasePlugin
from pydidas.widgets.widget_with_parameter_collection import (
    WidgetWithParameterCollection,
)


class ShowIntegrationRoiParamsWidget(WidgetWithParameterCollection):
    """
    A widget which allows to show the Parameters for the integration region.

    The Parameter widgets are created for an associated plugin which is not owned
    by this widget.
    """

    default_params = get_generic_param_collection("overlay_color")
    sig_roi_changed = QtCore.Signal()
    sig_toggle_edits = QtCore.Signal(bool)

    def __init__(self, **kwargs: dict):
        WidgetWithParameterCollection.__init__(self, **kwargs)
        self.setSizePolicy(*POLICY_MIN_MIN)
        self.set_default_params()
        self._plugin = kwargs.get("plugin", None)
        self._config = self._config | {
            "forced_edit_disable": kwargs.get("forced_edit_disable", False),
            "roi_active": False,
        }
        self.create_param_widget(self.get_param("overlay_color"))
        self.create_empty_widget(
            "plugin_container",
            sizePolicy=POLICY_MIN_MIN,
            stretch=(0, 0),
        )
        self.create_button(
            "but_reset_to_start_values",
            "Reset all changes",
            visible=kwargs.get("show_reset_button", True),
        )
        if kwargs.get("add_bottom_spacer", True):
            self.create_empty_widget(
                "bottom_spacer",
                sizePolicy=POLICY_FIX_EXP,
                stretch=(1, 1),
            )

    def create_widgets_for_axis(self, plugin: BasePlugin, axis: Literal["rad", "azi"]):
        """
        Create the widgets for the given axis.

        Parameters
        ----------
        plugin : pydidas.plugins.BasePlugin
            The plugin for which widgets shall be created.
        axis : Literal["rad", "azi"]
            The axis name.
        """
        _axis_long = "radial" if axis == "rad" else "azimuthal"
        _Axis_long = "Radial" if axis == "rad" else "Azimuthal"
        self.create_label(
            f"label_{axis}",
            f"{_Axis_long} integration region",
            bold=True,
            parent_widget=self._widgets["plugin_container"],
        )
        if axis == "azi":
            self.create_label(
                "label_azi_note",
                "Note: For an upward-oriented axis (i.e. the origin at the bottom of "
                "the image), the positive angular is counter-clockwise. For a downward-"
                "oriented-axis (i.e. the origin at the top of the image), the positive "
                "angular direction is clockwise. \nThe zero position is at the positive"
                " x-axis, i.e. right of the beamcenter.",
                font_metric_height_factor=7,
                font_metric_width_factor=FONT_METRIC_PARAM_EDIT_WIDTH,
                parent_widget=self._widgets["plugin_container"],
                sizePolicy=POLICY_FIX_EXP,
                wordWrap=True,
            )
        self.create_param_widget(
            plugin.get_param(f"{axis}_use_range"),
            parent_widget=self._widgets["plugin_container"],
            width_io=0.7,
            width_text=0.3,
        )
        self.create_button(
            f"but_select_{_axis_long}",
            f"Select {_axis_long} integration range in image",
            parent_widget=self._widgets["plugin_container"],
        )

        for _suffix in ["unit", "range_lower", "range_upper"]:
            _pname = f"{axis}_{_suffix}"
            self.create_param_widget(
                plugin.get_param(_pname),
                parent_widget=self._widgets["plugin_container"],
            )
        self.create_line(None, parent_widget=self._widgets["plugin_container"])

    def toggle_enable(self, enabled: bool):
        """
        Toggle the selection mode and enable/disable the Parameter widgets.

        Parameters
        ----------
        enabled : bool
            Editing enabled flag.
        """
        if self._config["forced_edit_disable"]:
            enabled = False
        for _type in ["rad", "azi"]:
            _type_long = "radial" if _type == "rad" else "azimuthal"
            if f"but_select_{_type_long}" in self._widgets:
                self._widgets[f"but_select_{_type_long}"].setEnabled(enabled)
                self.param_widgets[f"{_type}_use_range"].setEnabled(enabled)
                self.param_widgets[f"{_type}_range_lower"].setEnabled(enabled)
                self.param_widgets[f"{_type}_range_upper"].setEnabled(enabled)
                self.param_widgets[f"{_type}_unit"].setEnabled(enabled)
        self._widgets["but_reset_to_start_values"].setEnabled(enabled)

    def clear_plugin_widgets(self):
        """
        Clear the plugin_container widget to create new widgets.
        """
        _layout = self._widgets["plugin_container"].layout()
        for i in reversed(range(_layout.count())):
            _item = _layout.itemAt(i)
            _widget_to_remove = _item.widget()
            _layout.removeWidget(_widget_to_remove)
            _widget_to_remove.setParent(None)
            _widget_to_remove.deleteLater()
        for _name in ["but_select_azimuthal", "but_select_radial"]:
            if _name in self._widgets:
                self._widgets.pop(_name)
        for _suffix in ["use_range", "unit", "range_lower", "range_upper"]:
            for _prefix in ["rad", "azi"]:
                _name = f"{_prefix}_{_suffix}"
                if _name in self.param_widgets:
                    self.param_widgets.pop(_name)
