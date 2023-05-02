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
Module with the SelectIntegrationRegionWindow class which allows to select an
integration region for a plugin.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ["SelectIntegrationRegionWindow"]


from functools import partial
from pathlib import Path
from typing import Literal, Tuple

import numpy as np
from qtpy import QtCore

from ...contexts import DiffractionExperimentContext
from ...core import Dataset, UserConfigError, get_generic_param_collection
from ...core.constants import STANDARD_FONT_SIZE
from ...core.utils import apply_qt_properties, get_chi_from_x_and_y
from ...data_io import import_data
from ..dialogues import QuestionBox
from ..framework import PydidasWindow
from ..misc import SelectImageFrameWidget
from ..silx_plot import PydidasPlot2DwithIntegrationRegions


class SelectIntegrationRegionWindow(PydidasWindow):
    """
    A widget which allows to select points in a given image.
    """

    container_width = 320
    default_params = get_generic_param_collection(
        "filename", "hdf5_key", "hdf5_frame", "marker_color"
    )

    def __init__(self, plugin, parent=None, **kwargs):

        PydidasWindow.__init__(
            self, parent, title="Select integration region", activate_frame=False
        )
        apply_qt_properties(self.layout(), contentsMargins=(10, 10, 10, 10))

        self._EXP = kwargs.get("diffraction_exp", DiffractionExperimentContext())
        self._plugin = plugin
        self._original_plugin_param_values = plugin.get_param_values_as_dict()
        self.add_params(plugin.params)
        self._config = self._config | dict(
            radial_active=False,
            azimuthal_active=False,
            beamcenter=self._EXP.beamcenter,
            det_dist=self._EXP.get_param_value("detector_dist"),
            rad_unit=self._plugin.get_param_value("rad_unit"),
            closing_confirmed=False,
            only_show_roi=kwargs.get("only_show_roi", False),
        )
        self._image = None
        self.frame_activated(self.frame_index)

    def build_frame(self):
        """
        Build the frame and create widgets.
        """
        self.create_label(
            "label_title",
            "Select integration region",
            fontsize=STANDARD_FONT_SIZE + 1,
            fixedWidth=self.container_width,
            bold=True,
        )
        self.create_empty_widget(
            "left_container", fixedWidth=self.container_width, minimumHeight=400
        )
        _p_w_kwargs = dict(
            width_total=self.container_width,
            width_io=120,
            width_text=180,
            width_unit=0,
            parent_widget=self._widgets["left_container"],
        )
        self.create_spacer(None, fixedWidth=25, gridPos=(1, 1, 1, 1))
        self.add_any_widget(
            "plot",
            PydidasPlot2DwithIntegrationRegions(cs_transform=True),
            minimumWidth=700,
            minimumHeight=700,
            gridPos=(1, 2, 1, 1),
        )
        self.create_spacer(None, parent_widget=self._widgets["left_container"])
        self.create_label(
            "label_note",
            (
                "Note: The math for calculating the angles is only defined for "
                "detectors with square pixels."
            ),
            parent_widget=self._widgets["left_container"],
            fontsize=STANDARD_FONT_SIZE,
            bold=True,
        )
        self.create_line(None, parent_widget=self._widgets["left_container"])
        self.create_label(
            "label_file",
            "Select input file:",
            parent_widget=self._widgets["left_container"],
            fontsize=STANDARD_FONT_SIZE + 1,
            underline=True,
        )
        self.add_any_widget(
            "file_selector",
            SelectImageFrameWidget(
                *self.params.values(),
                import_reference="SelectIntegrationRegion__import",
                widget_width=self.container_width,
            ),
            parent_widget=self._widgets["left_container"],
            fixedWidth=self.container_width,
        )

        self.create_line(None, parent_widget=self._widgets["left_container"])
        self.create_param_widget(self.get_param("marker_color"), **_p_w_kwargs)
        self.param_widgets["marker_color"].io_edited.connect(
            self._widgets["plot"].set_new_marker_color
        )
        if self._config["only_show_roi"]:
            return
        self.create_line(None, parent_widget=self._widgets["left_container"])

        if "rad_use_range" in self.params:
            self.create_label(
                "label_rad",
                "Radial integration region",
                fontsize=STANDARD_FONT_SIZE,
                fixedWidth=self.container_width,
                bold=True,
                parent_widget=self._widgets["left_container"],
            )
            self.create_param_widget(self.get_param("rad_use_range"), **_p_w_kwargs)
            self.create_button(
                "but_select_radial",
                "Select radial integration region",
                fixedWidth=self.container_width,
                fixedHeight=25,
                parent_widget=self._widgets["left_container"],
            )
            for _pname in ["rad_unit", "rad_range_lower", "rad_range_upper"]:
                self.create_param_widget(self.get_param(_pname), **_p_w_kwargs)
            self.toggle_param_widget_visibility("rad_range_lower", False)
            self.toggle_param_widget_visibility("rad_range_upper", False)
            self.create_line(None, parent_widget=self._widgets["left_container"])
        if "azi_use_range" in self.params:
            self.create_label(
                "label_azi",
                "Azimuthal integration region",
                fontsize=STANDARD_FONT_SIZE,
                fixedWidth=self.container_width,
                bold=True,
                parent_widget=self._widgets["left_container"],
            )
            self.create_param_widget(self.get_param("azi_use_range"), **_p_w_kwargs)
            self.create_button(
                "but_select_azimuthal",
                "Select azimuthal integration region",
                fixedWidth=self.container_width,
                fixedHeight=25,
                parent_widget=self._widgets["left_container"],
            )
            for _pname in ["azi_unit", "azi_range_lower", "azi_range_upper"]:
                self.create_param_widget(self.get_param(_pname), **_p_w_kwargs)
            self.toggle_param_widget_visibility("azi_range_lower", False)
            self.toggle_param_widget_visibility("azi_range_upper", False)
            self.create_line(None, parent_widget=self._widgets["left_container"])

        self.create_button(
            "but_reset_to_start_values",
            "Reset all changes",
            fixedWidth=self.container_width,
            fixedHeight=25,
            parent_widget=self._widgets["left_container"],
        )
        self.create_button(
            "but_confirm",
            "Confirm integration region",
            fixedWidth=self.container_width,
            fixedHeight=25,
            parent_widget=self._widgets["left_container"],
        )

    def connect_signals(self):
        """
        Connect all signals.
        """
        self._widgets["file_selector"].sig_new_file_selection.connect(self.open_image)
        self._widgets["file_selector"].sig_file_valid.connect(self._toggle_fname_valid)
        if self._config["only_show_roi"]:
            return
        if "rad_use_range" in self.params:
            self.param_widgets["rad_use_range"].io_edited.connect(
                partial(self._updated_use_range_param, "radial")
            )
            self._widgets["but_select_radial"].clicked.connect(
                partial(self._start_selection, "radial")
            )
            self.param_widgets["rad_unit"].io_edited.connect(self._change_rad_unit)
            self.param_widgets["rad_range_lower"].io_edited.connect(
                partial(self.show_plot_items, "roi")
            )
            self.param_widgets["rad_range_upper"].io_edited.connect(
                partial(self.show_plot_items, "roi")
            )
        if "azi_use_range" in self.params:
            self.param_widgets["azi_use_range"].io_edited.connect(
                partial(self._updated_use_range_param, "azimuthal")
            )
            self._widgets["but_select_azimuthal"].clicked.connect(
                partial(self._start_selection, "azimuthal")
            )
            self.param_widgets["azi_unit"].io_edited.connect(self._change_azi_unit)
            self.param_widgets["azi_range_lower"].io_edited.connect(
                partial(self.show_plot_items, "roi")
            )
            self.param_widgets["azi_range_upper"].io_edited.connect(
                partial(self.show_plot_items, "roi")
            )
        self._widgets["but_reset_to_start_values"].clicked.connect(self._reset_plugin)
        self._EXP.sig_params_changed.connect(self._process_exp_update)
        self._sig_point_selected = self._widgets["plot"].sig_new_point_selected
        self._widgets["but_confirm"].clicked.connect(self._confirm_changes)

    def finalize_ui(self):
        """
        Finalize the UI and update the input widgets.
        """
        _nx = self._EXP.get_param_value("detector_npixx")
        _ny = self._EXP.get_param_value("detector_npixy")
        if _nx == 0 or _ny == 0:
            raise UserConfigError(
                "No detector has been defined. Cannot display the integration region."
            )
        self._image = Dataset(np.zeros((_ny, _ny)))
        self._widgets["plot"].plot_pydidas_dataset(self._image, title="")
        self.show_plot_items("roi")
        if self._config["only_show_roi"]:
            self._config["closing_confirmed"] = True
            return
        self._update_input_widgets()

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
        self._widgets["plot"].setEnabled(is_valid)

    @QtCore.Slot(str, object)
    def open_image(self, filename, kwargs):
        """
        Open an image with the given filename and display it in the plot.

        Parameters
        ----------
        filename : Union[str, Path]
            The filename and path.
        kwargs : dict
            Additional parameters to open a specific frame in a file.
        """
        self._image = import_data(filename, **kwargs)
        _path = Path(filename)
        self._reset_selection_mode()
        self._widgets["plot"].plot_pydidas_dataset(self._image, title=_path.name)
        self._widgets["plot"].changeCanvasToDataAction._actionTriggered()
        self._update_input_widgets()
        self.show_plot_items("roi")

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
        self.set_param_value_and_widget(
            f"{type_[:3]}_use_range", f"Specify {type_} range"
        )
        self._config[f"{type_}_active"] = True
        self._config[f"{type_}_n"] = 0
        self._widgets["plot"].remove_plot_items("all")
        self.show_plot_items(_other_type)
        self._toggle_widget_selection_mode(True)
        self._sig_point_selected.connect(getattr(self, f"_new_{type_}_point"))

    def _toggle_widget_selection_mode(self, selection):
        """
        Toggle the selection mode which disables the Parameter widgets.

        Parameters
        ----------
        selection : bool
            Flag whether the selection mode is active.
        """
        for _type in ["radial", "azimuthal"]:
            if f"but_select_{_type}" in self._widgets:
                self._widgets[f"but_select_{_type}"].setEnabled(not selection)
                self.param_widgets[f"{_type[:3]}_use_range"].setEnabled(not selection)
                self.param_widgets[f"{_type[:3]}_range_lower"].setEnabled(not selection)
                self.param_widgets[f"{_type[:3]}_range_upper"].setEnabled(not selection)
                self.param_widgets[f"{_type[:3]}_unit"].setEnabled(not selection)

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
        _plot = self._widgets["plot"]
        kind = ["azimuthal", "radial", "roi"] if "all" in kind else kind
        if "radial" in kind:
            _pxsize = self._EXP.get_param_value("detector_pxsizex") * 1e-6
            _range = self._plugin.get_radial_range_as_r()
            if _range is not None:
                _plot.draw_circle(_range[0] * 1e-3 / _pxsize, "radial_lower")
                _plot.draw_circle(_range[1] * 1e-3 / _pxsize, "radial_upper")
        if "azimuthal" in kind:
            _range = self._plugin.get_azimuthal_range_in_rad()
            if _range is not None:
                _plot.draw_line_from_beamcenter(_range[0], "azimuthal_lower")
                _plot.draw_line_from_beamcenter(_range[1], "azimuthal_upper")
        if "roi" in kind:
            self._show_integration_region()

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
        self._widgets["plot"].draw_integration_region(_rad_range, _azi_range)

    def _update_input_widgets(self):
        """
        Configure the input widget visibility based on the Parameter config.
        """
        if "rad_use_range" in self.param_widgets:
            _flag = self.get_param_value("rad_use_range") == "Specify radial range"
            self.toggle_param_widget_visibility("rad_range_lower", _flag)
            self.toggle_param_widget_visibility("rad_range_upper", _flag)
        if "azi_use_range" in self.param_widgets:
            _flag = self.get_param_value("azi_use_range") == "Specify azimuthal range"
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

        if self.get_param_value("rad_unit") == "r / mm":
            _val = _r * 1e3
        elif self.get_param_value("rad_unit") == "Q / nm^-1":
            _lambda = self._EXP.get_param_value("xray_wavelength") * 1e-10
            _val = (4 * np.pi / _lambda) * np.sin(_2theta / 2) * 1e-9
        elif self.get_param_value("rad_unit") == "2theta / deg":
            _val = 180 / np.pi * _2theta
        _bounds = "lower" if self._config["radial_n"] == 0 else "upper"
        self.toggle_param_widget_visibility(f"rad_range_{_bounds}", True)
        self.set_param_value_and_widget(f"rad_range_{_bounds}", np.round(_val, 5))
        if self._config["radial_n"] == 0:
            self._widgets["plot"].draw_circle(_r_px, f"radial_{_bounds}")
        self._config["radial_n"] += 1
        if self._config["radial_n"] > 1:
            self._sig_point_selected.disconnect(self._new_radial_point)
            self._reset_selection_mode()
            self._widgets["plot"].remove_plot_items("all")
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
        _factor = 180 / np.pi if "deg" in self.get_param_value("azi_unit") else 1
        _bounds = "lower" if self._config["azimuthal_n"] == 0 else "upper"
        self.toggle_param_widget_visibility(f"azi_range_{_bounds}", True)
        self.set_param_value_and_widget(
            f"azi_range_{_bounds}", np.round(_factor * _chi, 5)
        )
        if self._config["azimuthal_n"] == 0:
            self._widgets["plot"].draw_line_from_beamcenter(
                _chi, f"azimuthal_{_bounds}"
            )
        self._config["azimuthal_n"] += 1

        if self._config["azimuthal_n"] > 1:
            self._sig_point_selected.disconnect(self._new_azimuthal_point)
            self._reset_selection_mode()
            self._widgets["plot"].remove_plot_items("all")
            if not self._plugin.is_range_valid():
                self.set_param_value_and_widget("azi_use_range", "Full detector")
                self._update_input_widgets()
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
    def _change_azi_unit(self, new_unit):
        """
        Change the azimuthal unit for the integration region.

        Parameters
        ----------
        new_unit : str
            The new unit for chi.
        """
        _low = self.get_param_value("azi_range_lower")
        _high = self.get_param_value("azi_range_upper")
        _factor = 180 / np.pi if new_unit == "chi / deg" else np.pi / 180
        self.set_param_value_and_widget("azi_range_lower", np.round(_low * _factor, 6))
        self.set_param_value_and_widget("azi_range_upper", np.round(_high * _factor, 6))

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
            "rad_range_lower", self.get_param_value("rad_range_lower")
        )
        self.update_widget_value(
            "rad_range_upper", self.get_param_value("rad_range_upper")
        )

    def _reset_selection_mode(self):
        """
        Reset the selection mode and restore button functionality.
        """
        self._config["radial_active"] = False
        self._config["radial_n"] = 0
        self._config["azimuthal_active"] = False
        self._config["azimuthal_n"] = 0
        self._toggle_widget_selection_mode(False)

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

    @QtCore.Slot()
    def _reset_plugin(self):
        """
        Reset the plugin to the start values.
        """
        for _key, _val in self._original_plugin_param_values.items():
            if _key in self.param_widgets:
                self.set_param_value_and_widget(_key, _val)
            else:
                self.set_param_value(_key, _val)
        self._reset_selection_mode()
        self._update_input_widgets()
        self.show_plot_items("roi")

    @QtCore.Slot()
    def _confirm_changes(self):
        """
        Confirm all changes made to the plugin and close the window.
        """
        self._config["closing_confirmed"] = True
        self.close()

    def closeEvent(self, event):
        """
        Handle the Qt close event and add a question if closing without saving results.

        Parameters
        ----------
        event : Qore.QEvent
            The closing event.
        """
        if self._config["closing_confirmed"]:
            event.accept()
            return
        _reply = QuestionBox(
            "Exit confirmation",
            "Do you want to close the Select integration region "
            "window and discard all changes? To accept the changes, please use the "
            "'Confirm integration region' button.",
        ).exec_()
        if not _reply:
            event.ignore()
            return
        self._reset_plugin()
        event.accept()
