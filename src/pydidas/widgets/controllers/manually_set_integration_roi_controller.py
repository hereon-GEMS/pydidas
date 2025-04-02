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
Module with the ManuallySetIntegrationRoiController class which manages manually setting
the integration region for a plugin by selecting theROI graphically in a plot.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["ManuallySetIntegrationRoiController"]


from functools import partial
from typing import Literal

import numpy as np
from qtpy import QtCore
from qtpy.QtWidgets import QWidget

from pydidas.core import UserConfigError, get_generic_param_collection
from pydidas.core.constants import PYDIDAS_COLORS
from pydidas.core.utils import get_chi_from_x_and_y
from pydidas.core.utils.scattering_geometry import convert_radial_value
from pydidas.plugins import BasePlugin


class ManuallySetIntegrationRoiController(QtCore.QObject):
    """
    A controller to handle manually setting the integration region.

    This controller connects a plot widget (PydidasPlot2d instance) with the editor
    which holds the references to the Parameters for the integration ROI bounds.
    It allows to draw the boundaries of the integration ROI in the plot (assuming
    that the DiffractionExperimentContext has been set).
    If enabled, it picks up clicks in the plot widget and updates the respective
    Parameters and draws the new bounds in the plot.

    Parameters
    ----------
    editor : pydidas.widgets.misc.ShowIntegrationRoiParamsWidget
        The ShowIntegrationRoiParamsWidget instance to display parameter values.
    plot : pydidas.widgets.silx_plot.PydidasPlot2DwithIntegrationRegions
        The plot to display the ROI.
    **kwargs : dict
        Supported keyword arguments are:

        plugin : pydidas.plugins.BasePlugin
            The plugin to be edited.
        forced_edit_disable : bool
            Flag to force
    """

    default_params = get_generic_param_collection("overlay_color")
    sig_roi_changed = QtCore.Signal()
    sig_toggle_enable = QtCore.Signal(bool)
    sig_toggle_selection_mode = QtCore.Signal(bool)
    widget_width = 320

    def __init__(self, editor: QWidget, plot: QWidget, **kwargs: dict):
        QtCore.QObject.__init__(self)
        self._plot = plot
        self._plugin = kwargs.get("plugin", None)
        self._editor = editor
        self._config = {
            "roi_plotted": False,
            "forced_edit_disable": kwargs.get("forced_edit_disable", False),
            "enabled": True,
            "exp": None,
        }
        self._editor.param_widgets["overlay_color"].io_edited.connect(
            self.set_new_marker_color
        )
        self._editor._widgets["but_reset_to_start_values"].clicked.connect(
            self.reset_plugin
        )
        if self._plugin is not None:
            self.set_new_plugin(self._plugin)

    @property
    def enabled(self) -> bool:
        """
        Get the enabled status flag.

        Returns
        -------
        bool
            The enabled status.
        """
        return self._config["enabled"]

    def set_new_plugin(self, plugin: BasePlugin):
        """
        Set a new connected plugin.

        Parameters
        ----------
        plugin : pydidas.plugins.BasePlugin
            The plugin to be edited
        """
        if self._config["exp"] is not None:
            self._config["exp"].sig_params_changed.disconnect(self._process_exp_update)

        self._plugin = plugin
        self._original_plugin_param_values = plugin.get_param_values_as_dict()
        self._config["exp"] = plugin._EXP
        self._config["exp"].sig_params_changed.connect(self._process_exp_update)
        self._process_exp_update()

        self._editor.clear_plugin_widgets()
        if "rad_use_range" in plugin.params:
            self._editor.create_widgets_for_axis(plugin, "rad")
            self._connect_axis_widgets("rad")
            self._config["rad_unit"] = plugin.get_param_value("rad_unit")
        if "azi_use_range" in plugin.params:
            self._editor.create_widgets_for_axis(plugin, "azi")
            self._connect_axis_widgets("azi")
        if self._plot.getActiveImage() is None:
            _nx = self._config["exp"].get_param_value("detector_npixx")
            _ny = self._config["exp"].get_param_value("detector_npixy")
            self._plot.addImage(np.zeros((_ny, _nx)))
        self.reset_selection_mode()

    def _connect_axis_widgets(self, axis: Literal["rad", "azi"]):
        """
        Connect the new widgets for the given axis.

        Parameters
        ----------
        axis : Literal["rad", "azi"]
            The axis name.
        """
        _axis_long = "radial" if axis == "rad" else "azimuthal"
        self._editor.param_widgets[f"{axis}_use_range"].io_edited.connect(
            partial(self._updated_use_range_param, _axis_long)
        )
        self._editor._widgets[f"but_select_{_axis_long}"].clicked.connect(
            partial(self._start_selection, _axis_long)
        )
        self._editor.param_widgets[f"{axis}_unit"].io_edited.connect(
            getattr(self, f"_change_{axis}_unit")
        )
        for _key in [f"{axis}_range_lower", f"{axis}_range_upper"]:
            _widget = self._editor.param_widgets.get(_key, None)
            if _widget is not None:
                _widget.io_edited.connect(partial(self.show_plot_items, "roi"))

    @QtCore.Slot(str)
    def set_new_marker_color(self, color: str):
        """
        Set the new color for the markers.

        Parameters
        ----------
        color : str
            The name of the new color.
        """
        self._config["color"] = PYDIDAS_COLORS[color]
        self._plot.set_marker_color(color)
        for _key in [
            "roi",
            "azimuthal_lower",
            "azimuthal_upper",
            "radial_lower",
            "radial_upper",
        ]:
            _item = self._plot._getItem("item", legend=_key)
            if _item is not None:
                _item.setColor(self._config["color"])

    @QtCore.Slot()
    def reset_plugin(self):
        """
        Reset the plugin to the start values.
        """
        for _key, _val in self._original_plugin_param_values.items():
            if _key in self._editor.param_widgets:
                self.set_param_value_and_widget(_key, _val)
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
        self.toggle_enable(True)
        self.update_input_widgets()
        self.sig_toggle_selection_mode.emit(False)

    def toggle_enable(self, enabled: bool):
        """
        Toggle the selection mode which disables the Parameter widgets.

        Parameters
        ----------
        enabled : bool
            Flag whether the editing mode is active.
        """
        enabled = enabled if not self._config["forced_edit_disable"] else False
        self._config["enabled"] = enabled
        self._editor.toggle_enable(enabled)
        self.sig_toggle_enable.emit(enabled)

    def toggle_marker_color_param_visibility(self, visible: bool):
        """
        Toggle the visibility of the marker_color Parameter widget.

        Parameters
        ----------
        visible : bool
            Visible status flag.
        """
        self._editor.toggle_param_widget_visibility("overlay_color", visible)

    @QtCore.Slot()
    def show_plot_items(
        self, *kind: tuple[Literal["azimuthal", "radial", "roi", "all"]]
    ):
        """
        Show the items for the given kind from the plot.

        Parameters
        ----------
        *kind : tuple[Literal["azimuthal", "radial", "roi", "all"]]
            The kind or markers to be removed.
        """
        kind = ["azimuthal", "radial", "roi"] if "all" in kind else kind
        if "radial" in kind:
            _pxsize = self._config["exp"].get_param_value("detector_pxsizex") * 1e-6
            _range = self._plugin.get_radial_range_in_units("r / mm")
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

    def remove_plot_items(
        self, *kind: tuple[Literal["azimuthal", "radial", "roi", "all"]]
    ):
        """
        Remove the items for the given kind from the plot.

        Parameters
        ----------
        *kind : tuple[Literal["azimuthal", "radial", "roi", "all"]]
            The kind or markers to be removed.
        """
        kind = ["azimuthal", "radial", "roi"] if "all" in kind else kind
        for _kind in kind:
            if _kind in ["azimuthal", "radial"]:
                self._plot.remove(legend=f"{_kind}_lower", kind="item")
                self._plot.remove(legend=f"{_kind}_upper", kind="item")
            self._plot.remove(legend=_kind, kind="item")
        if "roi" in kind:
            self._config["roi_plotted"] = False

    @QtCore.Slot()
    def _process_exp_update(self):
        """
        Process updates of the DiffractionExperiment.
        """
        self._config["beamcenter"] = self._config["exp"].beamcenter
        self._config["det_dist"] = self._config["exp"].get_param_value("detector_dist")
        if self._config["roi_plotted"]:
            self.show_plot_items("roi")

    @QtCore.Slot()
    def _start_selection(self, type_: Literal["radial", "azimuthal"]):
        """
        Start the selection of the integration region.

        Parameters
        ----------
        type_ : Literal["radial", "azimuthal"]
            The type of region to be selected.
        """
        if not self._plot.isEnabled():
            return
        _other_type = "radial" if type_ == "azimuthal" else "azimuthal"

        self.set_param_value_and_widget(
            f"{type_[:3]}_use_range", f"Specify {type_} range"
        )
        self._config[f"{type_}_active"] = True
        self._config[f"{type_}_n"] = 0
        self.remove_plot_items("all")
        self.show_plot_items(_other_type)
        self.toggle_enable(False)
        self.sig_toggle_selection_mode.emit(True)
        self._plot.sig_new_point_selected.connect(getattr(self, f"_new_{type_}_point"))

    def set_param_value_and_widget(self, key: str, value: object):
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
        self._editor.update_widget_value(key, value)

    def _show_integration_region(self):
        """
        Show the integration region in the plot.
        """
        _pxsize = self._config["exp"].get_param_value("detector_pxsizex") * 1e-6
        _rad_range = self._plugin.get_radial_range_in_units("r / mm")
        if _rad_range is not None:
            _rad_range = (
                _rad_range[0] * 1e-3 / _pxsize,
                _rad_range[1] * 1e-3 / _pxsize,
            )
        _azi_range = self._plugin.get_azimuthal_range_in_rad()
        self._config["roi_plotted"] = True
        self._plot.draw_integration_region(_rad_range, _azi_range)

    def update_input_widgets(self):
        """
        Configure the input widget visibility based on the Parameter config.
        """
        if "rad_use_range" in self._editor.param_widgets:
            _flag = (
                self._plugin.get_param_value("rad_use_range") == "Specify radial range"
            )
            self._editor.toggle_param_widget_visibility("rad_range_lower", _flag)
            self._editor.toggle_param_widget_visibility("rad_range_upper", _flag)
        if "azi_use_range" in self._editor.param_widgets:
            _flag = (
                self._plugin.get_param_value("azi_use_range")
                == "Specify azimuthal range"
            )
            self._editor.toggle_param_widget_visibility("azi_range_lower", _flag)
            self._editor.toggle_param_widget_visibility("azi_range_upper", _flag)

    @QtCore.Slot(float, float)
    def _new_radial_point(self, xpos: float, ypos: float):
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
        _r = _r_px * self._config["exp"].get_param_value("detector_pxsizex") * 1e-6
        _r_in_mm = _r * 1e3
        _val = convert_radial_value(
            _r_in_mm,
            "r / mm",
            self._plugin.get_param_value("rad_unit"),
            self._config["exp"].xray_wavelength_in_m,
            self._config["exp"].det_dist_in_m,
        )
        _bounds = "lower" if self._config["radial_n"] == 0 else "upper"
        self._editor.toggle_param_widget_visibility(f"rad_range_{_bounds}", True)
        self.set_param_value_and_widget(f"rad_range_{_bounds}", np.round(_val, 5))
        if self._config["radial_n"] == 0:
            self._plot.draw_circle(_r_px, f"radial_{_bounds}")
        self._config["radial_n"] += 1
        if self._config["radial_n"] > 1:
            self._plot.sig_new_point_selected.disconnect(self._new_radial_point)
            self.reset_selection_mode()
            self.remove_plot_items("all")
            self.show_plot_items("roi")

    @QtCore.Slot(float, float)
    def _new_azimuthal_point(self, xpos: float, ypos: float):
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
        self._editor.toggle_param_widget_visibility(f"azi_range_{_bounds}", True)
        self.set_param_value_and_widget(
            f"azi_range_{_bounds}", np.round(_factor * _chi, 5)
        )
        if self._config["azimuthal_n"] == 0:
            self._plot.draw_line_from_beamcenter(_chi, f"azimuthal_{_bounds}")
        self._config["azimuthal_n"] += 1

        if self._config["azimuthal_n"] > 1:
            self._plot.sig_new_point_selected.disconnect(self._new_azimuthal_point)
            self.reset_selection_mode()
            self.remove_plot_items("all")
            if not self._plugin.is_range_valid():
                self.set_param_value_and_widget("azi_use_range", "Full detector")
                self.update_input_widgets()
                self.show_plot_items("roi")
                raise UserConfigError(
                    "The pyFAI integration range must either be in the interval "
                    "[0°, 360°] or [-180°, 180°]. Please select matching limits."
                )
            self.show_plot_items("roi")
            _low, _high = self._plugin.get_azimuthal_range_native()
            self.set_param_value_and_widget("azi_range_lower", _low)
            self.set_param_value_and_widget("azi_range_upper", _high)

    @QtCore.Slot(str)
    def _change_azi_unit(self, new_unit: Literal["chi / deg", "chi / rad"]):
        """
        Change the azimuthal unit for the integration region.

        Parameters
        ----------
        new_unit : Literal["chi / deg", "chi / rad"]
            The new unit for chi.
        """
        _low = self._plugin.get_param_value("azi_range_lower")
        _high = self._plugin.get_param_value("azi_range_upper")
        _factor = 180 / np.pi if new_unit == "chi / deg" else np.pi / 180
        self.set_param_value_and_widget("azi_range_lower", np.round(_low * _factor, 6))
        self.set_param_value_and_widget("azi_range_upper", np.round(_high * _factor, 6))

    @QtCore.Slot(str)
    def _change_rad_unit(
        self, new_unit: Literal["2theta / deg", "Q / nm^-1", "r / mm"]
    ):
        """
        Change the unit for the radial integration region.

        Parameters
        ----------
        new_unit : Literal["2theta / deg", "Q / nm^-1", "r / mm"]
            The new unit for the radial selection.
        """
        self._plugin.convert_radial_range_values(self._config["rad_unit"], new_unit)
        self._config["rad_unit"] = new_unit
        self._editor.update_widget_value(
            "rad_range_lower", self._plugin.get_param_value("rad_range_lower")
        )
        self._editor.update_widget_value(
            "rad_range_upper", self._plugin.get_param_value("rad_range_upper")
        )

    @QtCore.Slot(str)
    def _updated_use_range_param(
        self,
        type_: Literal["radial", "azimuthal"],
        value: Literal[
            "Full detector", "Specify radial range", "Specify azimuthal range"
        ],
    ):
        """
        Handle a new 'use radial/azimuthal range' Parameter setting.

        Parameters
        ----------
        type_ : Literal["radial", "azimuthal"]
            The type of range. Must be either radial or azimuthal
        value : Literal[
            "Full detector",
            "Specify radial range",
            "Specify azimuthal range"
        ]
            The new value of the Parameter.
        """
        _use_range = value == f"Specify {type_} range"
        self._editor.toggle_param_widget_visibility(
            f"{type_[:3]}_range_lower", _use_range
        )
        self._editor.toggle_param_widget_visibility(
            f"{type_[:3]}_range_upper", _use_range
        )
        self.show_plot_items("roi")
