# This file is part of pydidas.
#
# Copyright 2023 - 2026, Helmholtz-Zentrum Hereon
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
Module with PydidasPlot1D class which adds configurations to the base silx Plot1D.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2026, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["PydidasPlot1D"]


from typing import Any

import numpy as np
from qtpy import QtCore, QtWidgets
from silx.gui.plot import Plot1D

from pydidas.core import Dataset
from pydidas.widgets.silx_plot._special_plot_types_button import SpecialPlotTypesButton
from pydidas.widgets.silx_plot.silx_actions import LockZoomAction
from pydidas.widgets.silx_plot.utilities import (
    check_data_dimensions,
    get_allowed_kwargs,
)


class PydidasPlot1D(Plot1D):
    """
    A customized silx.gui.plot.Plot1D with support for pydidas Datasets.
    """

    def __init__(self, **kwargs: Any) -> None:
        Plot1D.__init__(
            self, parent=kwargs.get("parent", None), backend=kwargs.get("backend", None)
        )
        self.getRoiAction().setVisible(False)  # type: ignore[attr-defined]
        self.getFitAction().setVisible(False)  # type: ignore[attr-defined]

        self._qtapp = QtWidgets.QApplication.instance()
        if hasattr(self._qtapp, "sig_mpl_font_change"):
            self._qtapp.sig_mpl_font_change.connect(self._update_mpl_fonts)

        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)  # noqa
        self._add_lock_zoom_action()
        if kwargs.get("use_special_plots", True):
            self._add_special_plot_actions()
        self._y_function = SpecialPlotTypesButton.func_generic
        self._y_label = SpecialPlotTypesButton.label_generic
        self._current_raw_data = {}

    # -----------------------------------------#
    # re-implemented public Plot1D functions  #
    # -----------------------------------------#

    def clear(self) -> None:
        """Override clear to also clear the stored data."""
        super().clear()
        self.clear_plot()

    # -----------------------------------------#
    # new public methods                      #
    # -----------------------------------------#

    def clear_plot(self, clear_data: bool = True) -> None:
        """
        Clear the plot and remove all items.

        Parameters
        ----------
        clear_data : bool, optional
            Flag to remove all items from the stored data dictionary as well.
        """
        self.setGraphTitle("")
        self.setGraphYLabel("Y")
        self.setGraphXLabel("X")
        self.remove()
        if clear_data:
            self._current_raw_data = {}

    def plot_data(self, data: np.ndarray, **kwargs: Any) -> None:
        """
        Plot a numpy ndarray.

        This method supports both generic numpy ndarrays and pydidas Dataset
        instances. If a Dataset is provided, the plot_pydidas_dataset method
        is called.

        Parameters
        ----------
        data : numpy.ndarray
            The data to be plotted.
        **kwargs : Any
            Additional keyword arguments to be passed to the silx plot method.
            Supported arguments are all those supported by silx Plot1D.addCurve,
            as well as:

            x : numpy.ndarray, optional
                The x values to be used for the plot. If not provided, the index
                of the data array will be used.
        """
        if isinstance(data, Dataset):
            self.plot_pydidas_dataset(data, **kwargs)
        else:
            check_data_dimensions(data, 1)
            x = kwargs.pop("x", None)
            if x is None or x.size != data.size:  # type: ignore[union-attr]
                x = np.arange(data.size)
            # sanitize kwargs for addCurve
            kwargs = get_allowed_kwargs(Plot1D.addCurve, kwargs)
            if data.ndim == 1:
                self.addCurve(x, data, **kwargs)
            else:
                legend = kwargs.pop("legend", "Curve")
                for _i in range(data.shape[0]):
                    _legend = f"{legend} #{_i}"
                    self.addCurve(x, data[_i], legend=_legend, **kwargs)

    def plot_pydidas_dataset(self, data: Dataset, **kwargs: Any) -> None:
        """
        Plot a pydidas dataset.

        Parameters
        ----------
        data : pydidas.core.Dataset
            The data to be plotted.
        **kwargs : Any
            Additional keyword arguments to be passed to the silx plot method.
            Supported keywords are:

            resetzoom : bool, optional
                Flag to reset the zoom after plotting. The default is True.
            replace : bool, optional
                Flag to clear the plot before adding new curves. The default is
                True.
            linewidth : float, optional
                The line width for the curves. The default is 1.5.
            linestyle : str, optional
                The line style for the curves. The default is '-'.
            symbol : str or None, optional
                The symbol for the curves. The default is None.
            ylabel : str, optional
                The y-axis label. If not provided, it will be automatically
                generated from the data metadata.
            title : str, optional
                The plot title.
            legend : str, optional
                The legend for the curve(s).
        """
        _reset_zoom = kwargs.pop("resetzoom", True)
        if kwargs.pop("replace", True):
            self.clear_plot()
        _i_data = 0 if data.ndim == 1 else 1
        check_data_dimensions(data, 1)
        _plot_kwargs = self._process_plot_kwargs(kwargs)
        self._set_graph_labels(kwargs, data)
        self._current_raw_data[_plot_kwargs.get("legend")] = (data, _plot_kwargs)
        if data.ndim == 1:
            self.addCurve(
                data.axis_ranges[0],
                self._y_function(data.axis_ranges[0], data.array),
                **_plot_kwargs,
            )
        else:
            _label = data.axis_labels[0] + " = {value:.4f} " + data.axis_units[0]
            _x = data.axis_ranges[1]
            for _index, _pos in enumerate(data.axis_ranges[0]):
                _plot_kwargs.update({"legend": _label.format(value=_pos)})
                self.addCurve(
                    _x,
                    self._y_function(_x, data.array[_index]),
                    **_plot_kwargs,
                )
            self.setActiveCurve(_label.format(value=data.axis_ranges[0][0]))
        if _reset_zoom and not self._lock_zoom_action.locked:
            self.resetZoom()

    # display_data is a generic alias used in all custom silx plots to have a
    # uniform interface call to display data in DataViewer-like classes
    display_data = plot_pydidas_dataset

    # -----------------------------------------#
    # private plot methods                     #
    # -----------------------------------------#

    def _set_graph_labels(self, kwargs: dict[str, Any], data: Dataset) -> None:
        """
        Set the graph x and y labels.

        Parameters
        ----------
        kwargs : dict[str, Any]
            The calling kwargs.
        data : Dataset
            The data to be plotted.
        """
        _i_data = 0 if data.ndim == 1 else 1
        _ylabel = self._y_label(
            data.axis_labels[_i_data],
            data.axis_units[_i_data],
            data.data_label,
            data.data_unit,
        )
        self.setGraphYLabel(kwargs.get("ylabel", _ylabel))
        self.setGraphXLabel(data.get_axis_description(_i_data) or "index")

    def _process_plot_kwargs(self, kwargs: dict[str, Any]) -> dict[str, Any]:
        """
        Get the sanitized plot kwargs.

        Parameters
        ----------
        kwargs : dict[str, Any]
            The calling kwargs.

        Returns
        -------
        dict[str, Any]
            The kwargs to be passed to the silx plot method.
        """
        if kwargs.get("title"):
            self.setGraphTitle(kwargs.get("title"))  # type: ignore[arg-type]
        return {
            "linewidth": kwargs.get("linewidth", 1.5),
            "linestyle": kwargs.get("linestyle", "-"),
            "symbol": kwargs.get("symbol", None),
            "resetzoom": False,
            "legend": kwargs.get("legend", "Curve"),
        } | get_allowed_kwargs(Plot1D.addCurve, kwargs)

    # -----------------------------------------#
    # private initialization methods          #
    # -----------------------------------------#

    def _add_lock_zoom_action(self) -> None:
        """Add a lock zoom action to the plot."""
        self._lock_zoom_action = LockZoomAction(self, parent=self)  # type: ignore[arg-type]
        self.group.addAction(self._lock_zoom_action)  # type: ignore[attr-defined]
        self.addAction(self._lock_zoom_action)  # type: ignore[arg-type]
        self._toolbar.insertAction(  # type: ignore[attr-defined]
            self.xAxisAutoScaleAction,
            self._lock_zoom_action,  # type: ignore[attr-defined]
        )

    def _add_special_plot_actions(self) -> None:
        """
        Add the action to change the type of the plot.

        This action allows to display image coordinates in polar coordinates
        (with r / mm, 2theta / deg or q / nm^-1) scaling.
        """
        self._plot_type = SpecialPlotTypesButton(parent=self, plot=self)  # type: ignore[arg-type]
        self._toolbar.addWidget(self._plot_type)  # type: ignore[attr-defined]
        self._plot_type.sig_new_plot_type.connect(self._process_plot_type)

    # -----------------------------------------#
    # private update methods                   #
    # -----------------------------------------#

    @QtCore.Slot()
    def _process_plot_type(self) -> None:
        """
        Process the changed plot type and set the function to update the plotted value.
        """
        self.clear_plot(clear_data=False)
        self._y_function = self._plot_type.plot_yfunc
        self._y_label = self._plot_type.plot_ylabel
        for _legend, (_data, _kwargs) in self._current_raw_data.items():
            _kwargs["legend"] = _legend
            _kwargs["resetzoom"] = True
            self.plot_pydidas_dataset(_data, **_kwargs)

    @QtCore.Slot()
    def _update_mpl_fonts(self) -> None:
        """Update the plot's fonts."""
        _curve = self.getCurve()
        if _curve is None:
            return
        self.setBackend("matplotlib")  # type: ignore[arg-type]
