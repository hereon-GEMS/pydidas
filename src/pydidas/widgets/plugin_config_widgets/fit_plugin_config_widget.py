# This file is part of pydidas.
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
# along with Pydidas. If not, see <http://www.gnu.org/licenses/>.

"""
Module with the FitPluginConfigWidget which is a custom configuration widget
for peak fitting plugins.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["FitPluginConfigWidget"]


from functools import partial
from typing import NewType

from qtpy import QtCore

from pydidas.core.constants import FONT_METRIC_PARAM_EDIT_WIDTH, POLICY_EXP_FIX
from pydidas.core.generic_params import FIT_OUTPUT_OPTIONS
from pydidas.widgets.plugin_config_widgets.generic_plugin_config_widget import (
    GenericPluginConfigWidget,
)


BaseFitPlugin = NewType("BaseFitPlugin", type)


class FitPluginConfigWidget(GenericPluginConfigWidget):
    """
    A custom widget to modify the Parameters for peak fitting plugins.

    The widget adds a list of tickboxes to select the fit output.
    """

    def create_param_config_widgets(self):
        self._params_already_added = ["fit_output"]
        _plugin_output = self.plugin.get_param_value("fit_output").split("; ")
        self._fit_output = {
            _key: (_key in _plugin_output) for _key in FIT_OUTPUT_OPTIONS
        }
        for _key in ["keep_results", "label", "process_data_dim", "fit_func"]:
            _param = self.plugin.get_param(_key)
            self.create_param_widget(_param, linebreak=_key == "label")
            self._params_already_added.append(_key)
        self.create_empty_widget("checkbox_widget", sizePolicy=POLICY_EXP_FIX)
        self.create_label(
            "label_fit_output",
            "Fit output values:",
            font_metric_width_factor=FONT_METRIC_PARAM_EDIT_WIDTH,
            gridPos=(0, 0, 1, 2),
            parent_widget="checkbox_widget",
        )
        self.create_empty_widget(
            "spacer_fit_output",
            parent_widget="checkbox_widget",
            font_metric_width_factor=0.1 * FONT_METRIC_PARAM_EDIT_WIDTH,
        )
        for _index, _key in enumerate(FIT_OUTPUT_OPTIONS):
            self.create_check_box(
                f"checkbox_{_key}",
                _key,
                checked=_key in _plugin_output,
                font_metric_width_factor=0.9 * FONT_METRIC_PARAM_EDIT_WIDTH,
                gridPos=(_index + 1, 1, 1, 1),
                parent_widget="checkbox_widget",
            )
            self._widgets[f"checkbox_{_key}"].stateChanged.connect(
                partial(self._box_checked, _key)
            )
        for _key, _param in self.plugin.params.items():
            if (
                _key not in self._params_already_added
                and _key not in self.plugin.advanced_parameters
            ):
                self.create_param_widget(_param)

    @QtCore.Slot(int)
    def _box_checked(self, name: str, state: int):
        """
        Handle the signal that the checkbox for the fit output has been edited.

        Parameters
        ----------
        name : str
            The name of the output parameter.
        state : int
            The new checked state.
        """
        self._fit_output[name] = bool(state)
        self._update_fit_output()

    def _update_fit_output(self):
        """
        Update the fit output parameter from the checkboxes.
        """
        _active = [_key for _key, _value in self._fit_output.items() if _value is True]
        if _active == []:
            self.plugin.set_param_value("fit_output", "no output")
        else:
            self.plugin.set_param_value("fit_output", "; ".join(_active))

    def update_edits(self):
        """
        Update the configuration fields of the plugin.

        This method is used restore the default parameter values.
        """
        for param in self.plugin.params.values():
            if param.refkey != "fit_output":
                self.update_widget_value(param.refkey, param.value)
            if param.refkey == "fit_output":
                _keys = param.value.split("; ")
                for _key in self._fit_output:
                    self._fit_output[_key] = _key in _keys
                    self._widgets[f"checkbox_{_key}"].setChecked(_key in _keys)
