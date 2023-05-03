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
Module with the ShowIntegrationRegionWidget class which allows to show the integration
region of an associated Plugin in the linked plot.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ["ShowIntegrationRegionWidget"]


from functools import partial
from typing import Literal, Tuple

import numpy as np
from qtpy import QtCore

from ...core import UserConfigError, get_generic_param_collection
from ...core.constants import POLICY_FIX_EXP, POLICY_MIN_MIN, STANDARD_FONT_SIZE
from ...core.utils import apply_qt_properties, get_chi_from_x_and_y
from ..widget_with_parameter_collection import WidgetWithParameterCollection


_RANGE_KEYS = [
    "azi_range_lower",
    "azi_range_upper",
    "rad_range_lower",
    "rad_range_upper",
]


class ShowIntegrationRegionWidget(WidgetWithParameterCollection):
    """
    A widget which allows to show the integration region in a linked plot.

    This widget must be connected to a PydidasPlot2DwithIntegrationRegions widget
    to display the integration region correctly. The associated plugin can be set
    with the '.set_new_plugin' method.
    """

    container_width = 320
    default_params = get_generic_param_collection("marker_color")
    sig_roi_changed = QtCore.Signal()

    def __init__(self, plot, parent=None, **kwargs):
        WidgetWithParameterCollection.__init__(self, parent)
        apply_qt_properties(self.layout(), contentsMargins=(10, 10, 10, 10))
        self.setSizePolicy(*POLICY_MIN_MIN)
        self.set_default_params()
        self._plot = plot
        self._plugin = None
        self._config["forced_edit_disable"] = kwargs.get("forced_edit_disable", False)
        self.create_param_widget(
            self.get_param("marker_color"), **self._plugin_kwargs()
        )
        self.create_empty_widget(
            "plugin_container",
            fixedWidth=self.container_width,
            stretch=(0, 0),
            sizePolicy=POLICY_MIN_MIN,
        )
        self.create_button(
            "but_reset_to_start_values",
            "Reset all changes",
            fixedWidth=self.container_width,
            fixedHeight=25,
        )
        self.create_empty_widget(
            "bottom_spacer", stretch=(1, 1), sizePolicy=POLICY_FIX_EXP
        )
        self.param_widgets["marker_color"].io_edited.connect(
            self._plot.set_new_marker_color
        )
        self._widgets["but_reset_to_start_values"].clicked.connect(self.reset_plugin)
        if kwargs.get("plugin", None) is not None:
            self.set_new_plugin(kwargs.get("plugin"))

    def set_new_plugin(self, plugin):
        """
        Set a new connected plugin.

        Parameters
        ----------
        plugin : pydidas.plugins.BasePlugin
            The plugin to be edited
        """
        if self._plugin is not None:
            self._EXP.sig_params_changed.disconnect(self._process_exp_update)
        self._plugin = plugin
        self._original_plugin_param_values = plugin.get_param_values_as_dict()
        self._EXP = plugin._EXP
        self._EXP.sig_params_changed.connect(self._process_exp_update)
        self._clear_plugin_container()
        self._config["rad_unit"] = self._plugin.get_param_value("rad_unit")
        self._config["beamcenter"] = self._EXP.beamcenter
        self._config["det_dist"] = self._EXP.get_param_value("detector_dist")
        if "rad_use_range" in plugin.params:
            self._create_widgets_for_axis("rad")
        if "azi_use_range" in plugin.params:
            self._create_widgets_for_axis("azi")
        for _key in _RANGE_KEYS:
            _widget = self.param_widgets.get(_key, None)
            if _widget is not None:
                _widget.io_edited.connect(partial(self.show_plot_items, "roi"))
        if self._plot.getActiveImage() is None:
            _nx = self._EXP.get_param_value("detector_npixx")
            _ny = self._EXP.get_param_value("detector_npixy")
            self._plot.addImage(np.zeros((_ny, _nx)))
        self.reset_selection_mode()

    def _create_widgets_for_axis(self, axis: Literal["rad", "azi"]):
        """
        Create the widgets for the given axis.

        Parameters
        ----------
        axis : Literal["rad", "azi"]
            The axis name.
        """
        _axis_long = "radial" if axis == "rad" else "azimuthal"
        _Axis_long = "Radial" if axis == "rad" else "Azimuthal"
        _label_kwargs = dict(
            fontsize=STANDARD_FONT_SIZE,
            fixedWidth=self.container_width,
            bold=True,
            parent_widget=self._widgets["plugin_container"],
        )
        self.create_label(
            f"label_{axis}", f"Radial {_Axis_long} integration region", **_label_kwargs
        )
        self.create_param_widget(
            self._plugin.get_param(f"{axis}_use_range"),
            **self._plugin_kwargs("plugin_container"),
        )
        self.create_button(
            f"but_select_{_axis_long}",
            f"Select {_axis_long} integration region",
            fixedWidth=self.container_width,
            fixedHeight=25,
            parent_widget=self._widgets["plugin_container"],
        )
        for _suffix in ["unit", "range_lower", "range_upper"]:
            _pname = f"{axis}_{_suffix}"
            self.create_param_widget(
                self._plugin.get_param(_pname),
                **self._plugin_kwargs("plugin_container"),
            )
        self.create_line(None, parent_widget=self._widgets["plugin_container"])
        self.param_widgets[f"{axis}_use_range"].io_edited.connect(
            partial(self._updated_use_range_param, _axis_long)
        )
        self._widgets[f"but_select_{_axis_long}"].clicked.connect(
            partial(self._start_selection, _axis_long)
        )
        self.param_widgets[f"{axis}_unit"].io_edited.connect(
            getattr(self, f"_change_{axis}_unit")
        )

    @QtCore.Slot()
    def reset_plugin(self):
        """
        Reset the plugin to the start values.
        """
        for _key, _val in self._original_plugin_param_values.items():
            if _key in self.param_widgets:
                self._set_param_value_and_widget(_key, _val)
            else:
                self._plugin.set_param_value(_key, _val)
        self.reset_selection_mode()
        self.show_plot_items("roi")

    def reset_selection_mode(self):
        """
        Reset the selection mode and restore button functionality.
        """
        self._config["radial_n"] = 0
        self._config["azimuthal_n"] = 0
        self.toggle_param_edits_enabled(True)
        self.update_input_widgets()

    def toggle_param_edits_enabled(self, enabled):
        """
        Toggle the selection mode which disables the Parameter widgets.

        Parameters
        ----------
        enabled : bool
            Flag whether the editing mode is active.
        """
        if self._config["forced_edit_disable"]:
            enabled = False
        for _type in ["radial", "azimuthal"]:
            if f"but_select_{_type}" in self._widgets:
                self._widgets[f"but_select_{_type}"].setEnabled(enabled)
                self.param_widgets[f"{_type[:3]}_use_range"].setEnabled(enabled)
                self.param_widgets[f"{_type[:3]}_range_lower"].setEnabled(enabled)
                self.param_widgets[f"{_type[:3]}_range_upper"].setEnabled(enabled)
                self.param_widgets[f"{_type[:3]}_unit"].setEnabled(enabled)
        self._widgets["but_reset_to_start_values"].setEnabled(enabled)

    def show_plot_items(
        self, *kind: Tuple[Literal["azimuthal", "radial", "roi", "all"]]
    ):
        """
        Show the items for the given kind from the plot.

        Parameters
        ----------
        *kind : Tuple[Literal["azimuthal", "radial", "roi", "all"]]
            The kind or markers to be removed.
        """
        kind = ["azimuthal", "radial", "roi"] if "all" in kind else kind
        if "radial" in kind:
            _pxsize = self._EXP.get_param_value("detector_pxsizex") * 1e-6
            _range = self._plugin.get_radial_range_as_r()
            if _range is not None:
                self._plot.draw_circle(_range[0] * 1e-3 / _pxsize, "radial_lower")
                self._plot.draw_circle(_range[1] * 1e-3 / _pxsize, "radial_upper")
        if "azimuthal" in kind:
            _range = self._plugin.get_azimuthal_range_in_rad()
            if _range is not None:
                self._plot.draw_line_from_beamcenter(_range[0], "azimuthal_lower")
                self._plot.draw_line_from_beamcenter(_range[1], "azimuthal_upper")
        if "roi" in kind:
            self._show_integration_region()

    def _clear_plugin_container(self):
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
            width_total=self.container_width,
            width_io=120,
            width_text=180,
            width_unit=0,
            parent_widget=(
                self._widgets[container_name] if container_name is not None else self
            ),
        )

    @QtCore.Slot()
    def _process_exp_update(self):
        """
        Process updates of the DiffractionExperiment.
        """
        self._config["beamcenter"] = self._EXP.beamcenter
        self._config["det_dist"] = self._EXP.get_param_value("detector_dist")

    @QtCore.Slot(bool)
    def _toggle_fname_valid(self, is_valid):
        """
        Modify widgets visibility and activation based on the file selection.

        Parameters
        ----------
        is_valid : bool
            Flag to process.
        """
        self._plot.setEnabled(is_valid)

    @QtCore.Slot()
    def _start_selection(self, type_):
        """
        Start the selection of the integration region.

        Parameters
        ----------
        type_ : str
            The type of region. Must be either radial or azimuthal.
        """
        _other_type = "radial" if type_ == "azimuthal" else "azimuthal"

        self._set_param_value_and_widget(
            f"{type_[:3]}_use_range", f"Specify {type_} range"
        )
        self._config[f"{type_}_active"] = True
        self._config[f"{type_}_n"] = 0
        self._plot.remove_plot_items("all")
        self.show_plot_items(_other_type)
        self.toggle_param_edits_enabled(False)
        self._plot.sig_new_point_selected.connect(getattr(self, f"_new_{type_}_point"))

    def _set_param_value_and_widget(self, key, value):
        """
        Set the Plugin's Parameter value and the widget display value.

        Parameters
        ----------
        key : str
            The parameter reference key.
        value : object
            The new value.
        """
        self._plugin.set_param_value(key, value)
        self.update_widget_value(key, value)

    def _show_integration_region(self):
        """
        Show the integration region in the plot.
        """
        _pxsize = self._EXP.get_param_value("detector_pxsizex") * 1e-6
        _rad_range = self._plugin.get_radial_range_as_r()
        if _rad_range is not None:
            _rad_range = (
                _rad_range[0] * 1e-3 / _pxsize,
                _rad_range[1] * 1e-3 / _pxsize,
            )
        _azi_range = self._plugin.get_azimuthal_range_in_rad()
        self._plot.draw_integration_region(_rad_range, _azi_range)

    def update_input_widgets(self):
        """
        Configure the input widget visibility based on the Parameter config.
        """
        if "rad_use_range" in self.param_widgets:
            _flag = (
                self._plugin.get_param_value("rad_use_range") == "Specify radial range"
            )
            self.toggle_param_widget_visibility("rad_range_lower", _flag)
            self.toggle_param_widget_visibility("rad_range_upper", _flag)
        if "azi_use_range" in self.param_widgets:
            _flag = (
                self._plugin.get_param_value("azi_use_range")
                == "Specify azimuthal range"
            )
            self.toggle_param_widget_visibility("azi_range_lower", _flag)
            self.toggle_param_widget_visibility("azi_range_upper", _flag)

    @QtCore.Slot(float, float)
    def _new_radial_point(self, xpos, ypos):
        """
        Handle the selection of a new point in the radial selection.

        Parameters
        ----------
        xpos : float
            The x position in detector pixels.
        ypos : float
            The y position in detector pixels.
        """
        _cx, _cy = self._config["beamcenter"]
        _r_px = ((xpos - _cx) ** 2 + (ypos - _cy) ** 2) ** 0.5
        _r = _r_px * self._EXP.get_param_value("detector_pxsizex") * 1e-6
        _2theta = np.arctan(_r / self._config["det_dist"])

        if self._plugin.get_param_value("rad_unit") == "r / mm":
            _val = _r * 1e3
        elif self._plugin.get_param_value("rad_unit") == "Q / nm^-1":
            _lambda = self._EXP.get_param_value("xray_wavelength") * 1e-10
            _val = (4 * np.pi / _lambda) * np.sin(_2theta / 2) * 1e-9
        elif self._plugin.get_param_value("rad_unit") == "2theta / deg":
            _val = 180 / np.pi * _2theta
        _bounds = "lower" if self._config["radial_n"] == 0 else "upper"
        self.toggle_param_widget_visibility(f"rad_range_{_bounds}", True)
        self._set_param_value_and_widget(f"rad_range_{_bounds}", np.round(_val, 5))
        if self._config["radial_n"] == 0:
            self._plot.draw_circle(_r_px, f"radial_{_bounds}")
        self._config["radial_n"] += 1
        if self._config["radial_n"] > 1:
            self._plot.sig_new_point_selected.disconnect(self._new_radial_point)
            self.reset_selection_mode()
            self._plot.remove_plot_items("all")
            self.show_plot_items("roi")

    @QtCore.Slot(float, float)
    def _new_azimuthal_point(self, xpos, ypos):
        """
        Handle the selection of a new point in the azimuthal selection.

        Parameters
        ----------
        xpos : float
            The x position in detector pixels.
        ypos : float
            The y position in detector pixels.
        """
        _cx, _cy = self._config["beamcenter"]
        _chi = get_chi_from_x_and_y(xpos - _cx, ypos - _cy)
        _factor = (
            180 / np.pi if "deg" in self._plugin.get_param_value("azi_unit") else 1
        )
        _bounds = "lower" if self._config["azimuthal_n"] == 0 else "upper"
        self.toggle_param_widget_visibility(f"azi_range_{_bounds}", True)
        self._set_param_value_and_widget(
            f"azi_range_{_bounds}", np.round(_factor * _chi, 5)
        )
        if self._config["azimuthal_n"] == 0:
            self._plot.draw_line_from_beamcenter(_chi, f"azimuthal_{_bounds}")
        self._config["azimuthal_n"] += 1

        if self._config["azimuthal_n"] > 1:
            self._plot.sig_new_point_selected.disconnect(self._new_azimuthal_point)
            self.reset_selection_mode()
            self._plot.remove_plot_items("all")
            if not self._plugin.is_range_valid():
                self._set_param_value_and_widget("azi_use_range", "Full detector")
                self.update_input_widgets()
                self.show_plot_items("roi")
                raise UserConfigError(
                    "The pyFAI integration range must either be in the interval "
                    "[0°, 360°] or [-180°, 180°]. Please select matching limits."
                )
            self.show_plot_items("roi")
            _low, _high = self._plugin.get_azimuthal_range_native()
            self._set_param_value_and_widget("azi_range_lower", _low)
            self._set_param_value_and_widget("azi_range_upper", _high)

    @QtCore.Slot(str)
    def _change_azi_unit(self, new_unit):
        """
        Change the azimuthal unit for the integration region.

        Parameters
        ----------
        new_unit : str
            The new unit for chi.
        """
        _low = self._plugin.get_param_value("azi_range_lower")
        _high = self._plugin.get_param_value("azi_range_upper")
        _factor = 180 / np.pi if new_unit == "chi / deg" else np.pi / 180
        self._set_param_value_and_widget("azi_range_lower", np.round(_low * _factor, 6))
        self._set_param_value_and_widget(
            "azi_range_upper", np.round(_high * _factor, 6)
        )

    @QtCore.Slot(str)
    def _change_rad_unit(self, new_unit):
        """
        Change the unit for the radial integration region.

        Parameters
        ----------
        new_unit : str
            The new unit for the radial selection.
        """
        self._plugin.convert_radial_range_values(self._config["rad_unit"], new_unit)
        self._config["rad_unit"] = new_unit
        self.update_widget_value(
            "rad_range_lower", self._plugin.get_param_value("rad_range_lower")
        )
        self.update_widget_value(
            "rad_range_upper", self._plugin.get_param_value("rad_range_upper")
        )

    @QtCore.Slot(str)
    def _updated_use_range_param(self, type_, value):
        """
        Handle a new 'use radial/azimuthal range' Parameter setting.

        Parameters
        ----------
        type_ : str
            The type of range. Must be either radial or azimuthal
        value : str
            The new value of the Parameter.
        """
        _use_range = value == f"Specify {type_} range"
        self.toggle_param_widget_visibility(f"{type_[:3]}_range_lower", _use_range)
        self.toggle_param_widget_visibility(f"{type_[:3]}_range_upper", _use_range)
        self.show_plot_items("roi")
