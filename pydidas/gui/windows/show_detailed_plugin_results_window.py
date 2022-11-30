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
Module with the ShowDetailedPluginResultsWindow class which allows to handle and show
additional data for the selected plugin.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ["ShowDetailedPluginResultsWindow"]

from qtpy import QtCore, QtWidgets

from ...core.utils import SignalBlocker, update_size_policy
from ...core.constants import STANDARD_FONT_SIZE
from ...widgets.silx_plot import create_silx_plot_stack, get_2d_silx_plot_ax_settings
from .pydidas_window import PydidasWindow


class ShowDetailedPluginResultsWindow(PydidasWindow):
    """
    Window to display detailed plugin results.
    """

    show_frame = False
    sig_new_selection = QtCore.Signal(str)
    sig_minimized = QtCore.Signal()

    def __init__(self, parent=None, results=None, **kwargs):
        PydidasWindow.__init__(self, parent, title="Detailed plugin results", **kwargs)
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
            fontsize=STANDARD_FONT_SIZE + 4,
            bold=True,
            gridPos=(0, 0, 1, 2),
        )
        self.create_empty_widget("metadata", gridPos=(1, 0, 2, 1))
        self.create_combo_box(
            "selector",
            parent_widget=self._widgets["metadata"],
            gridPos=(-1, 0, 1, 1),
            fixedWidth=250,
        )
        self.create_label(
            "metadata_title",
            "Metadata:",
            parent_widget=self._widgets["metadata"],
            gridPos=(-1, 0, 1, 1),
            fixedWidth=250,
            fontsize=STANDARD_FONT_SIZE + 2,
        )
        self.create_label(
            "metadata_label",
            "",
            parent_widget=self._widgets["metadata"],
            gridPos=(-1, 0, 1, 1),
            fixedWidth=250,
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
        return QtCore.QSize(1200, 600)

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
            if f"plot{_index}_stack" in self._widgets:
                self._widgets[f"plot{_index}_stack"].setVisible(
                    _index < self._config["n_plots"]
                )
                for _dim in [1, 2]:
                    self._widgets[f"plot{_index}_{_dim}d"].clear()

    def __create_necessary_plots(self):
        """
        Create all required plots
        """
        for _index in range(self._config["n_plots"]):
            if f"plot{_index}_stack" in self._widgets:
                continue
            _y = 1 + _index // 2
            _x = 1 + _index % 2
            create_silx_plot_stack(self, gridPos=(_y, _x, 1, 1))
            self.__rename_plots(_index)
            update_size_policy(
                self._widgets[f"plot{_index}_stack"], horizontalStretch=0.5
            )

    def __rename_plots(self, target):
        """
        Rename the generic plot_stacks and plots to allow different plots.

        Parameters
        ----------
        target : int
            The subplot number.
        """
        self._widgets[f"plot{target}_stack"] = self._widgets["plot_stack"]
        self._widgets[f"plot{target}_1d"] = self._widgets["plot1d"]
        self._widgets[f"plot{target}_2d"] = self._widgets["plot2d"]

    def __update_metadata(self):
        """
        Update the metadata of the results.
        """
        if set(self._results.keys()) == {None}:
            self._widgets["selector"].setVisible(False)
            self.__select_point(None)
        else:
            with SignalBlocker(self._widgets["selector"]):
                self._widgets["selector"].clear()
                self._widgets["selector"].addItems(list(self._results.keys()))
            self._widgets["selector"].setCurrentIndex(0)
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
            _label = _item.get("label", "")
            _title = _titles.get(_i_plot, "")
            _data = _item["data"]
            if _data.ndim == 1:
                _ylabel = _plot_ylabels.get(_i_plot, "")
                self._widgets[f"plot{_i_plot}_stack"].setCurrentIndex(0)
                self._plot1d(_i_plot, _data, _label, _ylabel)
                self._widgets[f"plot{_i_plot}_1d"].setGraphTitle(_title)
            elif _data.ndim == 2:
                self._widgets[f"plot{_i_plot}_stack"].setCurrentIndex(1)
                self._plot2d(_i_plot, _data)
                self._widgets[f"plot{_i_plot}_2d"].setGraphTitle(_title)

    def __clear_plots(self):
        """
        Clear all items from the plots.
        """
        _n_plots = self._config["n_plots"]
        for _index in range(_n_plots):
            self._widgets[f"plot{_index}_1d"].clear()
            self._widgets[f"plot{_index}_2d"].clear()

    def _plot1d(self, i_plot, data, label, plot_ylabel=None):
        """
        Plot a 1D-dataset in the 1D plot widget.

        Parameters
        ----------
        i_plot : int
            The plot number.
        data : pydidas.core.Dataset
            The data to be plotted.
        label : str
            The curve label.
        plot_ylabel : Union[None, str], optional
            The y axis label for the plot.
        """
        _plot = self._widgets[f"plot{i_plot}_1d"]
        _axlabel = data.axis_labels[0] + (
            " / " + data.axis_units[0] if len(data.axis_units[0]) > 0 else ""
        )
        _plot.addCurve(
            data.axis_ranges[0],
            data.array,
            linewidth=1.5,
            legend=label,
            xlabel=_axlabel,
            ylabel=plot_ylabel,
        )

    def _plot2d(self, i_plot, data):
        """
        Plot a 2D-dataset in the 2D plot widget.

        Parameters
        ----------
        i_plot : int
            The plot number.
        data : pydidas.core.Dataset
            The data to be plotted.
        """
        _plot = self._widgets[f"plot{i_plot}_2d"]
        _ax_labels = [
            data.axis_labels[i]
            + (" / " + data.axis_units[i] if len(data.axis_units[0]) > 0 else "")
            for i in [0, 1]
        ]
        _originx, _scalex = get_2d_silx_plot_ax_settings(data.axis_ranges[1])
        _originy, _scaley = get_2d_silx_plot_ax_settings(data.axis_ranges[0])
        _plot.addImage(
            data,
            replace=True,
            copy=False,
            origin=(_originx, _originy),
            scale=(_scalex, _scaley),
        )
        _plot.setGraphYLabel(_ax_labels[0])
        _plot.setGraphXLabel(_ax_labels[1])

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
