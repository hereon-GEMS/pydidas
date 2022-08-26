# This file is part of pydidas.
#
# pydidas is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
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
to store the pixel mask.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ["TweakPluginParameterWindow"]

import copy

import numpy as np
from qtpy import QtWidgets, QtCore

from pydidas.core.constants import FIX_EXP_POLICY
from pydidas.core.utils import ShowBusyMouse
from pydidas.widgets import ScrollArea, BaseFrame
from pydidas.widgets.parameter_config import ConfigurePluginWidget, ParameterEditFrame
from pydidas.widgets.silx_plot import (
    create_silx_plot_stack,
    get_2d_silx_plot_ax_settings,
)
from pydidas.gui.windows import PydidasWindow, ShowDetailedPluginResults


class TweakPluginParameterWindow(QtWidgets.QMainWindow, PydidasWindow):
    """
    Window to display detailed plugin results.
    """

    show_frame = False
    sig_closed = QtCore.Signal()
    sig_new_params = QtCore.Signal(int)
    sig_this_frame_activated = QtCore.Signal()

    def __init__(self, parent=None, **kwargs):
        QtWidgets.QMainWindow.__init__(self)
        PydidasWindow.__init__(
            self, parent, title="Tweak plugin parameters", init_layout=False, **kwargs
        )
        self.__plugin = None
        self._config = self._config | {
            "initial_results": None,
            "detailed_results": None,
            "current_results": None,
            "parent": parent,
            "accept_changes": False,
        }

    def build_frame(self):
        """
        Build the frame and create all widgets.
        """
        self._central = BaseFrame()
        self._central.frame_activated(self._central.frame_index)
        self._central.setVisible(True)
        self.setCentralWidget(self._central)

        self._central.create_label(
            "label_title",
            "Tweak plugin parameters",
            fontsize=14,
            bold=True,
            gridPos=(0, 0, 1, 1),
        )
        self._widgets["config_area"] = ParameterEditFrame(
            parent=None,
            init_layout=True,
            lineWidth=5,
            sizePolicy=FIX_EXP_POLICY,
            fixedWidth=385,
        )
        self._central.create_any_widget(
            "config_scroll_area",
            ScrollArea,
            minimumHeight=500,
            widget=self._widgets["config_area"],
            fixedWidth=410,
            sizePolicy=(
                QtWidgets.QSizePolicy.Expanding,
                QtWidgets.QSizePolicy.Expanding,
            ),
            gridPos=(1, 0, 1, 1),
        )
        self.create_any_widget(
            "plugin_param_edit",
            ConfigurePluginWidget,
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

        create_silx_plot_stack(self._central, gridPos=(1, 1, 1, 1))

        self._widgets["detailed_results"] = ShowDetailedPluginResults()

        _dock_widget = QtWidgets.QDockWidget("Details")
        _dock_widget.setWidget(self._widgets["detailed_results"])
        _dock_widget.setFeatures(
            QtWidgets.QDockWidget.DockWidgetMovable
            | QtWidgets.QDockWidget.DockWidgetFloatable
        )
        _dock_widget.setBaseSize(500, 50)
        self.addDockWidget(QtCore.Qt.BottomDockWidgetArea, _dock_widget)

    def connect_signals(self):
        self._widgets["but_run_plugin"].clicked.connect(self.run_plugin)
        self._widgets["but_confirm"].clicked.connect(self.confirm_parameters)
        self._widgets["but_cancel"].clicked.connect(self.discard_parameter_changes)

    def tweak_plugin(self, plugin, results):
        """
        Tweak the selected plugin.

        Parameters
        ----------
        plugin : pydidas.plugins.BasePlugin
            The plugin instance to be tweaked.
        """
        self._config["accept_changes"] = False
        self.__plugin = plugin
        self.__original_plugin_params = copy.deepcopy(plugin.params)
        self._config["initial_results"] = results
        self._widgets["plugin_param_edit"].configure_plugin(0, plugin)
        self._widgets["plugin_param_edit"]._widgets["restore_defaults"].setVisible(
            False
        )
        self.__plot_plugin_results(results)
        self.__process_detailed_results()

    def __plot_plugin_results(self, results):
        """
        Plot the plugin results in the respective plot window.

        Parameters
        ----------
        results : pydidas.core.Dataset
            The plugin results.
        """
        results.convert_all_none_properties()
        self._central._widgets["plot_stack"].setCurrentIndex(results.ndim - 1)
        if results.ndim == 1:
            self._plot1d(
                results,
                f"{self.__plugin.plugin_name} results",
                plot_ylabel=results.data_label,
            )
        elif results.ndim == 2:
            self._plot2d(
                results,
                f"{self.__plugin.plugin_name} results",
            )

    def _plot1d(self, data, label, plot_ylabel=None):
        """
        Plot a 1D-dataset in the 1D plot widget.

        Parameters
        ----------
        plot : pydidas.widgets.silx_plot.PydidasPlot1D
            The silx plot widget to show the data.
        data : pydidas.core.Dataset
            The data to be plotted.
        label : str
            The curve label.
        plot_ylabel : Union[None, str], optional
            The y axis label for the plot.
        """
        _axlabel = data.axis_labels[0] + (
            " / " + data.axis_units[0] if len(data.axis_units[0]) > 0 else ""
        )
        self._central._widgets["plot1d"].addCurve(
            data.axis_ranges[0],
            data.array,
            replace=True,
            linewidth=1.5,
            legend=label,
            xlabel=_axlabel,
            ylabel=plot_ylabel,
        )

    def _plot2d(self, data, label):
        """
        Plot a 2D-dataset in the 2D plot widget.

        Parameters
        ----------
        data : pydidas.core.Dataset
            The data to be plotted.
        label : str
            The curve label.
        """
        _ax_labels = [
            data.axis_labels[i]
            + (" / " + data.axis_units[i] if len(data.axis_units[0]) > 0 else "")
            for i in [0, 1]
        ]
        _originx, _scalex = get_2d_silx_plot_ax_settings(data.axis_ranges[1])
        _originy, _scaley = get_2d_silx_plot_ax_settings(data.axis_ranges[0])
        self._central._widgets["plot2d"].addImage(
            data,
            replace=True,
            copy=False,
            origin=(_originx, _originy),
            scale=(_scalex, _scaley),
        )
        self._central._widgets["plot2d"].setGraphYLabel(_ax_labels[0])
        self._central._widgets["plot2d"].setGraphXLabel(_ax_labels[1])

    def __process_detailed_results(self):
        """
        Process the detailed results for the plugin, if it has the respective
        attribute.
        """
        if hasattr(self.__plugin, "get_detailed_results"):
            _details = self.__plugin.get_detailed_results()
            self._config["detailed_results"] = _details
            self._widgets["detailed_results"].update_results(_details, "")
        else:
            self._config["detailed_results"] = None
            self._widgets["detailed_results"].update_results({}, "")

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
            self.__plot_plugin_results(_res)
            self.__process_detailed_results()

    @QtCore.Slot()
    def confirm_parameters(self):
        """
        Confirm the selected Parameters and hide the TweakPluginParameters window.
        """
        self._config["accept_changes"] = True
        self.setVisible(False)
        self.sig_new_params.emit(self.__plugin.node_id)
        self.sig_closed.emit()

    @QtCore.Slot()
    def discard_parameter_changes(self):
        """
        Discard the made changes to the Plugin Parameters and reset them to the
        original values.
        """
        self._config["accept_changes"] = False
        self.setVisible(False)
        self.__plugin.params = copy.deepcopy(self.__original_plugin_params)
        self.sig_closed.emit()

    @QtCore.Slot()
    def closeEvent(self, event):
        """
        Handle the close event and discard

        Parameters
        ----------
        event : QtCore.QEvent
            The closing event.
        """
        if not self._config["accept_changes"]:
            self.discard_parameter_changes()
        QtWidgets.QMainWindow.closeEvent(self, event)
