# This file is part of pydidas
#
# Copyright 2021-, Helmholtz-Zentrum Hereon
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
__copyright__ = "Copyright 2021-, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ["ShowIntegrationRoiParamsWidget"]


from typing import Literal

from qtpy import QtCore

from ...core import get_generic_param_collection
from ...core.constants import POLICY_FIX_EXP, POLICY_MIN_MIN, STANDARD_FONT_SIZE
from ..widget_with_parameter_collection import WidgetWithParameterCollection


class ShowIntegrationRoiParamsWidget(WidgetWithParameterCollection):
    """
    A widget which allows to show the Parameters for the integration region.

    The Parameter widgets are created for an associated plugin which is not owned
    by this widget.
    """

    default_params = get_generic_param_collection("overlay_color")
    sig_roi_changed = QtCore.Signal()
    sig_toggle_edits = QtCore.Signal(bool)
    widget_width = 320

    def __init__(self, parent=None, **kwargs):
        self.widget_width = kwargs.get("widget_width", self.widget_width)
        WidgetWithParameterCollection.__init__(self, parent)
        self.setSizePolicy(*POLICY_MIN_MIN)
        self.set_default_params()
        self.setFixedWidth(self.widget_width)
        self._plugin = kwargs.get("plugin", None)
        self._config = self._config | {
            "forced_edit_disable": kwargs.get("forced_edit_disable", False),
            "roi_active": False,
        }
        self.create_param_widget(
            self.get_param("overlay_color"), **self._plugin_kwargs()
        )
        self.create_empty_widget(
            "plugin_container",
            fixedWidth=self.widget_width,
            stretch=(0, 0),
            sizePolicy=POLICY_MIN_MIN,
        )
        self.create_button(
            "but_reset_to_start_values",
            "Reset all changes",
            fixedWidth=self.widget_width,
            fixedHeight=25,
            visible=kwargs.get("show_reset_button", True),
        )
        if kwargs.get("add_bottom_spacer", True):
            self.create_empty_widget(
                "bottom_spacer",
                stretch=(1, 1),
                sizePolicy=POLICY_FIX_EXP,
                fixedWidth=self.widget_width,
            )

    def create_widgets_for_axis(self, plugin, axis: Literal["rad", "azi"]):
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
        _label_kwargs = dict(
            fontsize=STANDARD_FONT_SIZE,
            fixedWidth=self.widget_width,
            bold=True,
            parent_widget=self._widgets["plugin_container"],
        )
        self.create_label(
            f"label_{axis}", f"Radial {_Axis_long} integration region", **_label_kwargs
        )
        self.create_param_widget(
            plugin.get_param(f"{axis}_use_range"),
            **self._plugin_kwargs("plugin_container"),
        )
        self.create_button(
            f"but_select_{_axis_long}",
            f"Select {_axis_long} integration range in image",
            fixedWidth=self.widget_width,
            fixedHeight=25,
            parent_widget=self._widgets["plugin_container"],
        )
        for _suffix in ["unit", "range_lower", "range_upper"]:
            _pname = f"{axis}_{_suffix}"
            self.create_param_widget(
                plugin.get_param(_pname),
                **self._plugin_kwargs("plugin_container"),
            )
        self.create_line(
            None,
            parent_widget=self._widgets["plugin_container"],
            fixedWidth=self.widget_width,
        )

    def toggle_enable(self, enabled: bool):
        """
        Toggle the selection mode and enable/disable the Parameter widgets.

        Parameters
        ----------
        enabled : bool
            Editing enabled flag.
        """
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

    def _plugin_kwargs(self, container_name=None):
        """
        Get the kwargs for the plugin widget creation.

        Parameters
        ----------
        container_name : str
            The name of the container to use as parent.

        Returns
        -------
        dict
            The kwargs for the param_widget creation.
        """
        return dict(
            width_total=self.widget_width,
            width_io=120,
            width_text=180,
            width_unit=0,
            parent_widget=(
                self._widgets[container_name] if container_name is not None else self
            ),
        )
