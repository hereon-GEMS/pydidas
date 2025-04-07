# This file is part of pydidas.
#
# Copyright 2024 - 2025, Helmholtz-Zentrum Hereon
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
Module with the TweakPluginParameterWindow class which is a stand-alone frame
to modify and store the Parameters of a Plugin.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2024 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["TweakPluginParameterWindow"]


import copy

import numpy as np
from qtpy import QtCore, QtWidgets

from pydidas.core.constants import FONT_METRIC_PARAM_EDIT_WIDTH
from pydidas.core.utils import ShowBusyMouse
from pydidas.widgets.framework import PydidasWindow
from pydidas.widgets.parameter_config import (
    ParameterEditCanvas,
)
from pydidas.widgets.plugin_config_widgets import EditPluginParametersWidget
from pydidas.widgets.scroll_area import ScrollArea
from pydidas.widgets.silx_plot import PydidasPlotStack
from pydidas.widgets.windows.show_detailed_plugin_results_window import (
    ShowDetailedPluginResultsWindow,
)


class TweakPluginParameterWindow(PydidasWindow):
    """
    Window to to modify Plugin Parameters on the fly and inspect results.

    The TweakPluginParameterWindow displays detailed plugin results in combination
    with all Plugin Parameters to allow running the Plugin with different values.
    """

    show_frame = False
    sig_closed = QtCore.Signal()
    sig_new_params = QtCore.Signal(int)
    sig_this_frame_activated = QtCore.Signal()

    def __init__(self, **kwargs: dict):
        PydidasWindow.__init__(self, title="Tweak plugin parameters", **kwargs)
        self.__plugin = None
        self.__qtapp = QtWidgets.QApplication.instance()
        self._config = self._config | {
            "initial_results": None,
            "detailed_results": None,
            "current_results": None,
            "parent": kwargs.get("parent", None),
            "accept_changes": False,
        }

    def build_frame(self):
        """
        Build the frame and create all widgets.
        """
        self.create_label(
            "label_title",
            "Tweak plugin parameters",
            bold=True,
            fontsize_offset=4,
            gridPos=(0, 0, 1, 2),
        )
        self._widgets["config_area"] = ParameterEditCanvas(
            font_metric_width_factor=FONT_METRIC_PARAM_EDIT_WIDTH
        )
        self.create_any_widget(
            "config_scroll_area",
            ScrollArea,
            minimumHeight=500,
            resize_to_widget_width=True,
            widget=self._widgets["config_area"],
        )
        self.create_any_widget(
            "plugin_param_edit",
            EditPluginParametersWidget,
            font_metric_width_factor=FONT_METRIC_PARAM_EDIT_WIDTH,
            parent_widget=self._widgets["config_area"],
        )
        self.create_line(
            "line0",
            parent_widget=self._widgets["config_area"],
        )
        self.create_button(
            "but_run_plugin",
            "Run plugin with current parameters",
            parent_widget=self._widgets["config_area"],
        )
        self.create_line(
            "line1",
            parent_widget=self._widgets["config_area"],
        )
        self.create_button(
            "but_confirm",
            "Confirm current parameters and close window",
            parent_widget=self._widgets["config_area"],
        )
        self.create_line(
            "line2",
            parent_widget=self._widgets["config_area"],
        )
        self.create_button(
            "but_cancel",
            "Cancel parameter editing and discard changes",
            parent_widget=self._widgets["config_area"],
        )
        self.create_any_widget(
            "plot",
            PydidasPlotStack,
            gridPos=(1, 1, 1, 1),
        )
        self._widgets["detailed_results"] = ShowDetailedPluginResultsWindow()

    def connect_signals(self):
        """
        Connect the signals for the buttons to their respective slots.
        """
        self._widgets["but_run_plugin"].clicked.connect(self.run_plugin)
        self._widgets["but_confirm"].clicked.connect(self.confirm_parameters)
        self._widgets["but_cancel"].clicked.connect(self.discard_parameter_changes)

    def finalize_ui(self):
        """
        finalize the UI initialization.
        """
        self._widgets["config_scroll_area"].force_width_from_size_hint()

    def tweak_plugin(self, plugin, results):
        """
        Tweak the selected plugin.

        Parameters
        ----------
        plugin : pydidas.plugins.BasePlugin
            The plugin instance to be tweaked.
        """
        self._widgets["config_scroll_area"].adjustSize()
        self._config["accept_changes"] = False
        self.__plugin = plugin
        self.__original_plugin_params = copy.deepcopy(plugin.params)
        self._config["initial_results"] = results
        self._widgets["plugin_param_edit"].configure_plugin(
            plugin.node_id, plugin, allow_restore_defaults=False
        )
        self._widgets["plot"].plot_data(
            results, title=f"{self.__plugin.plugin_name} results", replace=True
        )
        self.__process_detailed_results()

    def __process_detailed_results(self):
        """
        Process the detailed results for the plugin, if it has the respective
        attribute.
        """
        if hasattr(self.__plugin, "detailed_results"):
            _details = self.__plugin.detailed_results
            self._config["detailed_results"] = _details
            self._widgets["detailed_results"].update_results(
                _details,
                (
                    f"Tweak plugin {self.__plugin.plugin_name} "
                    f"(node #{self.__plugin.node_id:03d})"
                ),
            )
            self._widgets["detailed_results"].setVisible(True)
            self._widgets["detailed_results"].raise_()
        else:
            self._config["detailed_results"] = None
            self._widgets["detailed_results"].update_results({}, "")
            self._widgets["detailed_results"].setVisible(False)

    @QtCore.Slot()
    def __update_scroll_area_width(self):
        """
        Update the width of the scroll area based on the ParameterEditWidget.
        """

    @QtCore.Slot()
    def run_plugin(self):
        """
        Run the plugin with the current Parameters.
        """
        with ShowBusyMouse():
            _arg = self.__plugin._config["input_data"]
            if isinstance(_arg, np.ndarray):
                _arg = self.__plugin._config["input_data"].copy()
            _kwargs = self.__plugin._config["input_kwargs"].copy()
            self.__plugin.pre_execute()
            _res, _new_kws = self.__plugin.execute(_arg, **_kwargs)
            self._widgets["plot"].plot_data(
                _res, title=f"{self.__plugin.plugin_name} results", replace=True
            )

            self.__process_detailed_results()

    @QtCore.Slot()
    def confirm_parameters(self):
        """
        Confirm the selected Parameters and hide the TweakPluginParameters window.
        """
        self._config["accept_changes"] = True
        self.setVisible(False)
        self.sig_new_params.emit(self.__plugin.node_id)
        self._widgets["detailed_results"].setVisible(False)
        self.sig_closed.emit()

    @QtCore.Slot()
    def discard_parameter_changes(self):
        """
        Discard the made changes to the Plugin Parameters and reset them to the
        original values.
        """
        self._config["accept_changes"] = False
        self.setVisible(False)
        if self.__plugin is not None:
            self.__plugin.params = copy.deepcopy(self.__original_plugin_params)
        self._widgets["detailed_results"].setVisible(False)
        self.sig_closed.emit()

    @QtCore.Slot()
    def closeEvent(self, event):
        """
        Handle the close event and discard any possible changes.

        Parameters
        ----------
        event : QtCore.QEvent
            The closing event.
        """
        if not self._config["accept_changes"]:
            self.discard_parameter_changes()
        self._widgets["detailed_results"].close()
        QtWidgets.QWidget.closeEvent(self, event)

    def hide(self):
        """
        Overload the generic hide method to hide the details window as well.
        """
        self._widgets["detailed_results"].setVisible(False)
        QtWidgets.QWidget.hide(self)
