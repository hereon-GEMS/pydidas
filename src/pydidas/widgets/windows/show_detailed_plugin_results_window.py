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
Module with the ShowDetailedPluginResultsWindow class which allows to handle and show
additional data for the selected plugin.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["ShowDetailedPluginResultsWindow"]


from qtpy import QtCore, QtWidgets

from pydidas.core.constants import ALIGN_TOP_LEFT, FONT_METRIC_HALF_CONSOLE_WIDTH
from pydidas.core.utils import update_size_policy
from pydidas.widgets.framework import PydidasWindow
from pydidas.widgets.silx_plot import PydidasPlotStack


class ShowDetailedPluginResultsWindow(PydidasWindow):
    """
    Window to display detailed plugin results.
    """

    show_frame = False
    sig_new_selection = QtCore.Signal(str)
    sig_minimized = QtCore.Signal()

    def __init__(self, results=None, **kwargs):
        PydidasWindow.__init__(self, title="Detailed plugin results", **kwargs)
        self._config["n_plots"] = 0
        self._results = results
        if results is not None:
            self.update_results(results)

    def build_frame(self):
        """
        Build the frame and create all widgets.
        """
        self.create_label(
            "label_title",
            "Detailed plugin results",
            bold=True,
            fontsize_offset=4,
            gridPos=(0, 0, 1, 2),
        )
        self.create_empty_widget(
            "metadata",
            gridPos=(1, 0, 2, 1),
            font_metric_width_factor=FONT_METRIC_HALF_CONSOLE_WIDTH,
        )
        self.create_combo_box(
            "selector",
            font_metric_width_factor=FONT_METRIC_HALF_CONSOLE_WIDTH,
            gridPos=(-1, 0, 1, 1),
            parent_widget="metadata",
        )
        self.create_label(
            "metadata_title",
            "Metadata:",
            font_metric_width_factor=FONT_METRIC_HALF_CONSOLE_WIDTH,
            fontsize_offset=2,
            gridPos=(-1, 0, 1, 1),
            parent_widget="metadata",
        )
        self.create_label(
            "metadata_label",
            "",
            alignment=ALIGN_TOP_LEFT,
            font_metric_height_factor=20,
            font_metric_width_factor=FONT_METRIC_HALF_CONSOLE_WIDTH,
            gridPos=(-1, 0, 1, 1),
            parent_widget="metadata",
            wordWrap=True,
        )

    def connect_signals(self):
        """
        Connect all the required signals for the frame.
        """
        self._widgets["selector"].currentTextChanged.connect(self.__select_point)

    def sizeHint(self):
        """
        Set the sizeHint for the preferred size.

        Returns
        -------
        QtCore.QSize
            The desired size.
        """
        _font_height = QtWidgets.QApplication.instance().font_height
        return QtCore.QSize(70 * _font_height, 40 * _font_height)

    def update_results(self, results, title=None):
        """
        Update the displayed results.

        Parameters
        ----------
        results : dict
            The dictionary with the new results.
        """
        self._results = results
        self._config["result_keys"] = list(results.keys())
        self.__update_title(title)
        if len(self._config["result_keys"]) > 0:
            _n_plots = results[self._config["result_keys"][0]].get("n_plots", 0)
            self._config["n_plots"] = _n_plots
            self.__prepare_widgets()
            self.__update_metadata()
            self.__plot_results(self._config["result_keys"][0])

    def __update_title(self, title):
        """
        Update the title label.

        Parameters
        ----------
        title : Union[None, str]
            The new title.
        """
        if title is not None:
            self._widgets["label_title"].setText("Detailed plugin results: " + title)
        else:
            self._widgets["label_title"].setText("Detailed plugin results")

    def __prepare_widgets(self):
        """
        Prepare all widgets.
        """
        self.__create_necessary_plots()
        for _index in range(4):
            if f"plot_{_index}" in self._widgets:
                self._widgets[f"plot_{_index}"].setVisible(
                    _index < self._config["n_plots"]
                )
                self._widgets[f"plot_{_index}"].clear_plots()

    def __create_necessary_plots(self):
        """
        Create all required plots.
        """
        for _index in range(self._config["n_plots"]):
            if f"plot_{_index}" in self._widgets:
                continue
            _y = 1 + _index // 2
            _x = 1 + _index % 2
            self.create_any_widget(
                f"plot_{_index}",
                PydidasPlotStack,
                gridPos=(_y, _x, 1, 1),
                minimumWidth=500,
            )
            update_size_policy(self._widgets[f"plot_{_index}"], horizontalStretch=1)

    def __update_metadata(self):
        """
        Update the metadata of the results.
        """
        if set(self._results.keys()) == {None}:
            self._widgets["selector"].setVisible(False)
            self.__select_point(None)
        else:
            with QtCore.QSignalBlocker(self._widgets["selector"]):
                self._widgets["selector"].clear()
                self._widgets["selector"].addItems(list(self._results.keys()))
            self._widgets["selector"].setCurrentIndex(0)
            self._widgets["selector"].setVisible(True)
            self.__select_point(self._config["result_keys"][0])

    @QtCore.Slot(str)
    def __select_point(self, key):
        """
        Select a datapoint to display.

        Parameters
        ----------
        key : str
            The key to identify the results.
        """
        _has_metadata = "metadata" in self._results[key].keys()
        if _has_metadata:
            _meta_text = self._results[key]["metadata"]
            self._widgets["metadata_label"].setText(_meta_text)
        self._widgets["metadata_title"].setVisible(_has_metadata)
        self._widgets["metadata_label"].setVisible(_has_metadata)
        self.__plot_results(key)

    def __plot_results(self, key):
        """
        Plot the provided results.

        Parameters
        ----------
        key : Union[str, None]
            The key to find the specific results.
        """
        _point_result = self._results[key]
        _plot_ylabels = _point_result.get("plot_ylabels", {})
        _titles = _point_result.get("plot_titles", {})
        self.__clear_plots()
        for _item in _point_result.get("items", []):
            _i_plot = _item["plot"]
            _data = _item["data"]
            self._widgets[f"plot_{_i_plot}"].plot_data(
                _data,
                title=_titles.get(_i_plot, ""),
                legend=_item.get("label", ""),
                ylabel=_plot_ylabels.get(_i_plot, ""),
                replace=False,
            )

    def __clear_plots(self):
        """
        Clear all items from all plots.
        """
        for _index in range(self._config["n_plots"]):
            self._widgets[f"plot_{_index}"].clear_plots()

    def closeEvent(self, event):
        """
        Re-implement the closeEvent to also emit a signal that this Window has been
        closed.

        Parameters
        ----------
        event : QEvent
            The closing event.
        """
        self.sig_minimized.emit()
        QtWidgets.QWidget.closeEvent(self, event)
