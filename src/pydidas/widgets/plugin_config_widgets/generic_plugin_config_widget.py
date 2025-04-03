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
__all__ = ["GenericPluginConfigWidget"]


from pathlib import Path

from qtpy import QtCore
from qtpy.QtWidgets import QStyle

from pydidas.core import Hdf5key
from pydidas.core.constants import FONT_METRIC_PARAM_EDIT_WIDTH, OUTPUT_PLUGIN
from pydidas.core.utils import apply_qt_properties
from pydidas.plugins import BasePlugin
from pydidas.widgets.factory import CreateWidgetsMixIn
from pydidas.widgets.parameter_config import ParameterEditCanvas


class GenericPluginConfigWidget(ParameterEditCanvas, CreateWidgetsMixIn):
    """
    The generic plugin configuration widget.

    For subclassing, the following modifications should be considered:

    1. The subclass needs a `update_edits` method that resets the
       configuration widgets to be in sync with the plugin parameters.
       The default implementation only updates the widget values based
       on the current plugin parameters.
    2. The init calls the `create_all_widgets` and `connect_signals` methods.
       Any customization of the widget should be done in these methods while
       leaving the init method untouched.
       Please bear in mind that the default `connect_signals` includes important
       signal connections. If you want to change the signal connections,
       please also call the default `connect_signals` method from the custom
       `connect_signals` method.
    3. The `create_all_widgets` method includes the creation of the header
       and the parameter configuration widgets, including for advanced
       parameters. If you want to change only the regular parameters,
       please consider overriding the `create_param_config_widgets` method.
    """

    sig_new_label = QtCore.Signal(int, str)

    def __init__(self, plugin: BasePlugin, node_id: int, **kwargs: dict):
        ParameterEditCanvas.__init__(self, **kwargs)
        CreateWidgetsMixIn.__init__(self)
        apply_qt_properties(
            self.layout(), contentsMargins=(0, 0, 0, 0), horizontalSpacing=0
        )
        self.plugin = plugin
        self.node_id = node_id
        self._use_advanced_params = len(self.plugin.advanced_parameters) > 0
        self.create_all_widgets()
        self.connect_signals()

    def create_all_widgets(self):
        """
        Create all widgets for the plugin configuration.
        """
        self.create_header()
        self.create_param_config_widgets()
        if self._use_advanced_params:
            self.create_advanced_param_config_widgets()
        self.finalize_init()

    def create_header(self):
        """Create the header for the plugin configuration widget."""
        self.create_label(
            "plugin_name",
            f"Plugin: {self.plugin.plugin_name}",
            bold=True,
            fontsize_offset=1,
            gridPos=(0, 0, 1, 2),
        )
        if self.node_id is not None:
            self.create_label(
                "node_id",
                f"Node ID: {self.node_id}",
                fontsize_offset=2,
                gridPos=(1, 0, 1, 2),
            )
        self.create_spacer("spacer", gridPos=(2, 0, 1, 2))
        self.create_label(
            "params",
            "Parameters:",
            fontsize_offset=2,
            gridPos=(3, 0, 1, 1),
        )
        self.create_button(
            "restore_defaults",
            "Restore default parameters",
            gridPos=(2, 0, 1, 2),
            icon="qt-std::SP_BrowserReload",
        )

    def create_param_config_widgets(self):
        """Instantiate the parameter widgets for the plugin parameters."""
        for param in self.plugin.params.values():
            if (
                param.refkey not in self.plugin.advanced_parameters
                and not param.refkey.startswith("_")
            ):
                _kwargs = {
                    "linebreak": param.dtype in [Hdf5key, Path]
                    or param.refkey == "label"
                }
                self.create_param_widget(param, **_kwargs)
        if self.plugin.plugin_type == OUTPUT_PLUGIN:
            self.param_composite_widgets["keep_results"].setVisible(False)

    def create_advanced_param_config_widgets(self):
        """Create the widgets for the advanced parameters."""
        self._advanced_params_hidden = True
        self.create_button(
            "but_toggle_advanced_params",
            "Display advanced Parameters",
            icon="qt-std::SP_TitleBarUnshadeButton",
            font_metric_width_factor=FONT_METRIC_PARAM_EDIT_WIDTH,
        )
        for _key in self.plugin.advanced_parameters:
            _param = self.plugin.get_param(_key)
            _kwargs = {
                "linebreak": _param.dtype in [Hdf5key, Path],
                "visible": False,
            }
            self.create_param_widget(_param, **_kwargs)

    def finalize_init(self):
        """
        Finalize the initialization of the widget.

        This method is called at the end of the initialization process
        and can be used to perform any additional setup or configuration.
        """
        pass

    def connect_signals(self):
        """Connect the basic signals to the widgets."""
        self._widgets["restore_defaults"].clicked.connect(self.restore_defaults)
        self.param_widgets["label"].io_edited.connect(self._label_updated)
        if self._use_advanced_params:
            self._widgets["but_toggle_advanced_params"].clicked.connect(
                self.toggle_advanced_params
            )

    @QtCore.Slot()
    def toggle_advanced_params(self):
        """
        Toggle the visibility of the advanced Parameters.
        """
        self._advanced_params_hidden = not self._advanced_params_hidden
        for _key in self.plugin.advanced_parameters:
            self.toggle_param_widget_visibility(_key, not self._advanced_params_hidden)
        self._widgets["but_toggle_advanced_params"].setText(
            "Display advanced Parameters"
            if self._advanced_params_hidden
            else "Hide advanced Parameters"
        )
        self._widgets["but_toggle_advanced_params"].setIcon(
            self.style().standardIcon(
                QStyle.SP_TitleBarUnshadeButton
                if self._advanced_params_hidden
                else QStyle.SP_TitleBarShadeButton
            )
        )

    @QtCore.Slot()
    def restore_defaults(self):
        """
        Restore the default values to all Plugin Parameters.

        This method will update both the plugin Parameters and the displayed
        widget values.
        """
        self.plugin.restore_all_defaults(confirm=True)
        self.update_edits()

    def update_edits(self):
        """
        Update the configuration widgets based on the current plugin parameters.
        """
        for param in self.plugin.params.values():
            self.update_widget_value(param.refkey, param.value)

    @QtCore.Slot(str)
    def _label_updated(self, label: str):
        """
        Process the updated label and emit a signal.

        Parameters
        ----------
        label : str
            The new label.
        """
        self.sig_new_label.emit(self.plugin.node_id, label)
