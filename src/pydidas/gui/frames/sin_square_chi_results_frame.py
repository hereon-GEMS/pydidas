# This file is part of pydidas
#
# Copyright 2025, Helmholtz-Zentrum Hereon
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
Module with the SinSquareChiResultsFrame which is used to display results from
the sin square chi residual stress analysis plugins.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["SinSquareChiResultsFrame"]

from functools import partial
from pathlib import Path
from typing import Any

import numpy as np
from qtpy import QtCore

from pydidas_plugins.residual_stress_plugins.store_sin_2chi_data import (
    StoreSinTwoChiData,
)
from pydidas_plugins.residual_stress_plugins.store_sin_square_chi_data import (
    StoreSinSquareChiData,
)

from pydidas.core import (
    UserConfigError,
    get_generic_param_collection,
)
from pydidas.core.constants import FONT_METRIC_CONFIG_WIDTH
from pydidas.core.utils import apply_qt_properties
from pydidas.gui.frames.builders.sin_square_chi_results_frame_builder import (
    SIN_SQUARE_CHI_RESULTS_FRAME_BUILD_INFORMATION,
)
from pydidas.widgets import PydidasFileDialog
from pydidas.widgets.dialogues import WarningBox
from pydidas.widgets.factory import EmptyWidget
from pydidas.widgets.framework import BaseFrame
from pydidas.widgets.plotting import GridCurvePlot
from pydidas.workflow import ProcessingResults, WorkflowResults
from pydidas_qtcore import PydidasQApplication


_DEFAULT_PARAMS = get_generic_param_collection(
    "selected_data_source",
    "selected_sin_square_chi_node",
    "selected_sin_2chi_node",
    "plot_type",
    "show_sin_square_chi_results",
    "show_sin_square_chi_branches",
    "autoscale_sin_square_chi_results",
    "sin_square_chi_limit_low",
    "sin_square_chi_limit_high",
    "show_sin_2chi_results",
    "autoscale_sin_2chi_results",
    "sin_2chi_limit_low",
    "sin_2chi_limit_high",
    "num_horizontal_plots",
    "num_vertical_plots",
)

_PARAMS_NOT_TO_RESTORE = [
    "selected_data_source",
    "selected_sin_square_chi_node",
    "selected_sin_2chi_node",
    "plot_type",
    "autoscale_sin_square_chi_results",
    "sin_square_chi_limit_low",
    "sin_square_chi_limit_high",
    "autoscale_sin_2chi_results",
    "sin_2chi_limit_low",
    "sin_2chi_limit_high",
]


_RESULTS = WorkflowResults()


class SinSquareChiResultsFrame(BaseFrame):
    """
    A class to visualize the results of a sin-square chi analysis.
    """

    menu_icon = "pydidas::frame_icon_sin_square_visualization"
    menu_title = "Sin square chi results visualization"
    menu_entry = "Analysis tools/Sin square chi results visualization"
    default_params = _DEFAULT_PARAMS
    params_not_to_restore = _PARAMS_NOT_TO_RESTORE

    @staticmethod
    def _get_data_min_and_max(data: np.ndarray) -> tuple[float, float]:
        if data is None:
            raise UserConfigError("No data available to update limits.")
        try:
            _min = float(np.nanmin(data))
            _max = float(np.nanmax(data))
            _delta = _max - _min
            _min = round(_min - 0.05 * _delta, 6)
            _max = round(_max + 0.05 * _delta, 6)

        except RuntimeWarning:
            _min, _max = 0, 1
            WarningBox("Empty data", "The data does not include any valid values.")
        return _min, _max

    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)
        self.__qtapp = PydidasQApplication.instance()
        self.set_default_params()
        self.__import_dialog = PydidasFileDialog()
        self.__current_results = ProcessingResults()
        self._sin_square_chi_node_keys = {"no selection": -1}
        self._sin_2chi_node_keys = {"no selection": -1}
        self._sin_square_chi_data = None
        self._sin_2chi_data = None

    def build_frame(self) -> None:
        """
        Build the frame and populate it with widgets.
        """
        self._widgets["config"] = EmptyWidget(
            font_metric_width_factor=FONT_METRIC_CONFIG_WIDTH
        )
        for _name, _args, _kwargs in SIN_SQUARE_CHI_RESULTS_FRAME_BUILD_INFORMATION:
            _method = getattr(self, _name)
            if "widget" in _kwargs:
                _kwargs["widget"] = self._widgets[_kwargs["widget"]]
            _method(*_args, **_kwargs)
        apply_qt_properties(self.layout(), columnStretch=(1, 1))

    def connect_signals(self) -> None:
        """
        Connect all required signals and slots between widgets and class
        methods.
        """
        self._widgets["button_load_workflow_results"].clicked.connect(
            self._import_workflow_results
        )
        self._widgets["button_import_from_directory"].clicked.connect(
            self._import_from_directory
        )
        self.param_widgets["autoscale_sin_square_chi_results"].sig_new_value.connect(
            partial(self._update_scaling_visibility, "square_chi")
        )
        self.param_widgets["autoscale_sin_2chi_results"].sig_new_value.connect(
            partial(self._update_scaling_visibility, "2chi")
        )
        for _key in [
            "autoscale_sin_square_chi_results",
            "sin_square_chi_limit_low",
            "sin_square_chi_limit_high",
            "autoscale_sin_2chi_results",
            "sin_2chi_limit_low",
            "sin_2chi_limit_high",
        ]:
            _ref = "square" if "square" in _key else "two_chi"
            self.param_widgets[_key].sig_new_value.connect(
                partial(self.__set_scaling, _ref)
            )
        for _key in [
            "selected_sin_2chi_node",
            "selected_sin_square_chi_node",
            "show_sin_square_chi_branches",
            "show_sin_square_chi_results",
            "show_sin_2chi_results",
        ]:
            self.param_widgets[_key].sig_value_changed.connect(
                self._update_plotted_data
            )
        self._widgets["button_update_sin_2chi_limits"].clicked.connect(
            self._update_sin_2chi_limits_from_data
        )
        self._widgets["button_update_sin_square_chi_limits"].clicked.connect(
            self._update_sin_square_chi_limits_from_data
        )
        self.param_widgets["num_horizontal_plots"].sig_new_value.connect(
            partial(self.__update_plot_numbers, "hor")
        )
        self.param_widgets["num_vertical_plots"].sig_new_value.connect(
            partial(self.__update_plot_numbers, "vert")
        )

    def finalize_ui(self) -> None:
        """
        Finalize the UI initialization.
        """
        self._plots: GridCurvePlot = self._widgets["visualization"]
        self.reset_selection()

    def restore_state(self, state: dict) -> None:
        """Restore the frame's state from stored information."""
        BaseFrame.restore_state(self, state)
        if self._config["built"]:
            self._plots.set_plot_numbers(
                self.get_param_value("num_vertical_plots"),
                self.get_param_value("num_horizontal_plots"),
            )

    def update_selected_data_source(self, data_source: str) -> None:
        """
        Update the selected data source parameter.

        Parameters
        ----------
        data_source : str
            The new data source to set.
        """
        self.param_widgets["selected_data_source"].setReadOnly(False)  # noqa E1101
        self.set_param_and_widget_value("selected_data_source", data_source)
        self.param_widgets["selected_data_source"].setReadOnly(True)  # noqa E1101

    @QtCore.Slot()
    def _import_workflow_results(self):
        """
        Import workflow results from a file dialog.
        """
        self.__current_results.update_from_processing_results(_RESULTS)
        self.update_selected_data_source("Workflow results")
        self.reset_selection()
        self._update_selection_choices()

    @QtCore.Slot()
    def _import_from_directory(self):
        """
        Open a file dialog to import data from a directory.
        """
        _dir = self.__import_dialog.get_existing_directory(
            caption="Import data from directory",
            qsettings_ref="SinSquareChiResultsFrame__import_dir",
        )
        if _dir is not None:
            self.__current_results.import_data_from_directory(_dir)
            _stem = Path(_dir).stem
            self.update_selected_data_source("Directory: " + _stem)
            self.reset_selection()
            self._update_selection_choices()

    def reset_selection(self) -> None:
        """
        Reset the selection of sin-square chi and sin(2*chi) nodes.

        This method will reset the selected nodes to their initial state.
        """
        self._sin_2chi_data = None
        self._sin_square_chi_data = None
        self.set_param_value("selected_sin_square_chi_node", "no selection")
        self.set_param_value("selected_sin_2chi_node", "no selection")
        self._plots.set_datasets(square=None, two_chi=None)
        self._plots.set_titles(square="sin^2(chi)", two_chi="sin(2*chi)")
        for _key in ["square", "two_chi"]:
            self._plots.set_xscaling(_key, (-0.05, 1.05), update_plot=False)
            self._plots.set_y_autoscaling(_key, update_plot=False)

    def _update_selection_choices(self) -> None:
        """
        Update the choices for the sin-square chi and sin(2*chi) nodes.

        This method will update the parameter choices based on the current
        results.
        """
        self._plots.set_scan(self.__current_results.frozen_scan)
        self._sin_square_chi_node_keys = {
            self.__current_results._config["result_titles"][_key]: _key
            for _key, _val in self.__current_results._config["plugin_names"].items()
            if StoreSinSquareChiData.plugin_name in _val
        } | {"no selection": -1}
        self.set_param_value_and_choices(
            "selected_sin_square_chi_node",
            list(self._sin_square_chi_node_keys)[0],
            list(self._sin_square_chi_node_keys),
        )
        self.param_widgets["selected_sin_square_chi_node"].update_choices(
            self.params["selected_sin_square_chi_node"].choices
        )
        self._sin_2chi_node_keys = {
            self.__current_results._config["result_titles"][_key]: _key
            for _key, _val in self.__current_results._config["plugin_names"].items()
            if StoreSinTwoChiData.plugin_name in _val
        } | {"no selection": -1}
        self.set_param_value_and_choices(
            "selected_sin_2chi_node",
            list(self._sin_2chi_node_keys)[0],
            list(self._sin_2chi_node_keys),
        )
        self.param_widgets["selected_sin_2chi_node"].update_choices(
            self.params["selected_sin_2chi_node"].choices
        )
        if (
            len(self._sin_2chi_node_keys) <= 2
            and len(self._sin_square_chi_node_keys) <= 2
        ):
            self._update_plotted_data()

    @QtCore.Slot()
    def _update_plotted_data(self) -> None:
        """
        Update the data used in the plots.
        """
        for _key in ["square_chi", "2chi"]:
            _node_str = self.get_param_value(f"selected_sin_{_key}_node")
            _node_id = getattr(self, f"_sin_{_key}_node_keys")[_node_str]
            _show = self.get_param_value(f"show_sin_{_key}_results")
            if _node_id > 0 and _show:
                _data = self.__current_results.get_results_for_flattened_scan(_node_id)
                if _key == "square_chi" and not self.get_param_value(
                    "show_sin_square_chi_branches"
                ):
                    _data = _data[:, 2:, :]
                _data = np.roll(_data, 1, axis=1)
            else:
                _data = None
            setattr(self, f"_sin_{_key}_data", _data)
        self._plots.set_datasets(
            square=self._sin_square_chi_data, two_chi=self._sin_2chi_data
        )

    @QtCore.Slot(str)
    def _update_scaling_visibility(self, results: str, autoscale: str) -> None:
        """
        Update the visibility of the scaling widgets based on the autoscale parameter.

        Parameters
        ----------
        results : str
            The key of the result for which the autoscale parameter is set.
        autoscale : str
            The autoscale parameter value as a string ("TRUE" or "FALSE").
        """
        autoscale = autoscale.upper() == "TRUE"
        for _key in [f"sin_{results}_limit_low", f"sin_{results}_limit_high"]:
            self.param_composite_widgets[_key].setVisible(not autoscale)
        self._widgets[f"button_update_sin_{results}_limits"].setVisible(not autoscale)

    @QtCore.Slot()
    def __set_scaling(self, result_key: str) -> None:
        """
        Set the scaling for the sin-square chi or sin(2*chi) results.

        Parameters
        ----------
        result_key : str
            The type of results to set the scaling for ("square" or "2chi").
        """
        _key = "square_chi" if result_key == "square" else "2chi"
        _use_autoscale = self.get_param_value(f"autoscale_sin_{_key}_results")
        if _use_autoscale:
            self._plots.set_y_autoscaling(result_key)
            return
        _low = self.get_param_value(f"sin_{_key}_limit_low")
        _high = self.get_param_value(f"sin_{_key}_limit_high")
        self._plots.set_yscaling(result_key, (_low, _high))

    @QtCore.Slot()
    def _update_sin_square_chi_limits_from_data(self) -> None:
        """
        Update the sin^2(chi) limits from the selected data.
        """
        _min, _max = self._get_data_min_and_max(self._sin_square_chi_data)
        self.set_param_and_widget_value("sin_square_chi_limit_low", _min)
        self.set_param_and_widget_value("sin_square_chi_limit_high", _max)
        self.__set_scaling("square")

    @QtCore.Slot()
    def _update_sin_2chi_limits_from_data(self) -> None:
        """
        Update the sin(2*chi) limits from the selected data.
        """
        _min, _max = self._get_data_min_and_max(self._sin_2chi_data)
        self.set_param_and_widget_value("sin_2chi_limit_low", _min)
        self.set_param_and_widget_value("sin_2chi_limit_high", _max)
        self.__set_scaling("two_chi")

    @QtCore.Slot(str)
    def __update_plot_numbers(self, direction: str, value: str) -> None:
        """
        Update the number of horizontal or vertical plots in the grid.

        Parameters
        ----------
        direction : str
            The direction to update ("hor" for horizontal, "vert" for vertical).
        value : str
            The value of the parameter that triggered the update.
        """
        if direction == "hor":
            self._plots.n_plots_hor = int(value)
        elif direction == "vert":
            self._plots.n_plots_vert = int(value)
        else:
            raise ValueError(
                f"Direction must be `hor` or `vert`. Received: `{direction}`."
            )
