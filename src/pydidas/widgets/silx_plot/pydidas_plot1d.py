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


import warnings
from typing import Any

import numpy as np
from qtpy import QtCore, QtWidgets
from silx.gui.plot import Plot1D

from pydidas.core import Dataset, PydidasQsettings, UserConfigError
from pydidas.widgets.silx_plot._special_plot_types_button import SpecialPlotTypesButton
from pydidas.widgets.silx_plot.utilities import get_allowed_kwargs


_QSETTINGS = PydidasQsettings()


class PydidasPlot1D(Plot1D):
    """
    A customized silx.gui.plot.Plot1D with support for pydidas Datasets.
    """

    @staticmethod
    def _check_data_dimensions(data: Dataset | np.ndarray) -> None:
        """
        Check the data dimensions.

        Parameters
        ----------
        data : Dataset or np.ndarray
            The data to display.
        """
        if data.ndim == 1:
            return
        if data.ndim > 2:
            raise UserConfigError(
                "The given dataset has more than 2 dimensions. Please check "
                f"the input data definition:\nThe input data has {data.ndim} "
                "dimensions but only 1d or 2d data can be plotted as curves or "
                "curve groups, respectively."
            )
        _n_max: int = _QSETTINGS.value("user/max_number_curves", int)  # type: ignore[assignment]
        if data.shape[0] > _n_max:
            raise UserConfigError(
                f"The number of given curves ({data.shape[0]}) exceeds the maximum "
                f"number of curves allowed ({_n_max}). \n"
                "Please limit the data range to be displayed or increase the maximum "
                "number of curves in the user settings (Options -> User config). "
                "Please note that displaying a large number of curves will slow down "
                "the plotting performance."
            )

    def __init__(self, **kwargs: Any) -> None:
        Plot1D.__init__(
            self, parent=kwargs.get("parent", None), backend=kwargs.get("backend", None)
        )
        self.getRoiAction().setVisible(False)
        self.getFitAction().setVisible(False)

        self._qtapp = QtWidgets.QApplication.instance()
        if hasattr(self._qtapp, "sig_mpl_font_change"):
            self._qtapp.sig_mpl_font_change.connect(self.update_mpl_fonts)

        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)  # noqa
        if kwargs.get("use_special_plots", True):
            self._add_special_plot_actions()
        self._y_function = SpecialPlotTypesButton.func_generic
        self._y_label = SpecialPlotTypesButton.label_generic
        self._current_raw_data = {}

    def _add_special_plot_actions(self) -> None:
        """
        Add the action to change the type of the plot.

        This action allows to display image coordinates in polar coordinates
        (with r / mm, 2theta / deg or q / nm^-1) scaling.
        """
        self._plot_type = SpecialPlotTypesButton(parent=self, plot=self)
        self._toolbar.addWidget(self._plot_type)
        self._plot_type.sig_new_plot_type.connect(self._process_plot_type)

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
            self.plot_pydidas_dataset(_data, **_kwargs)

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
            self._check_data_dimensions(data)
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
        self._check_data_dimensions(data)
        _ylabel = self._y_label(
            data.axis_labels[_i_data],
            data.axis_units[_i_data],
            data.data_label,
            data.data_unit,
        )
        _plot_kwargs = {
            "linewidth": kwargs.get("linewidth", 1.5),
            "linestyle": kwargs.get("linestyle", "-"),
            "symbol": kwargs.get("symbol", None),
            "resetzoom": False,
            "legend": kwargs.get("legend", "Curve"),
        } | get_allowed_kwargs(Plot1D.addCurve, kwargs)
        self.setGraphXLabel(data.get_axis_description(_i_data) or "index")
        self.setGraphYLabel(kwargs.get("ylabel", _ylabel))
        if kwargs.get("title"):
            self.setGraphTitle(kwargs.get("title"))
        self._current_raw_data[_plot_kwargs.get("legend")] = (data, _plot_kwargs)
        if data.ndim == 1:
            self.addCurve(
                data.axis_ranges[_i_data],
                self._y_function(data.axis_ranges[_i_data], data.array),
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
            self.setActiveCurve(_label.format(value=_x[0]))
        if _reset_zoom:
            self.resetZoom()

    # display_data is a generic alias used in all custom silx plots to have a
    # uniform interface call to display data in DataViewer-like classes
    display_data = plot_pydidas_dataset

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

    @QtCore.Slot()
    def update_mpl_fonts(self) -> None:
        """Update the plot's fonts."""
        _curve = self.getCurve()
        if _curve is None:
            return
        self.setBackend("matplotlib")  # type: ignore[arg-type]

    # TODO: check if still needed with silx 2.2.2
    def _activeItemChanged(self, type_: str) -> None:
        """Override generic Plot1D._activeItemChanged to catch QApplication signals."""
        if self.sender() == self._qtapp:
            warnings.warn("Skipping _activeItemChanged call from QApplication signal")
            return
        Plot1D._activeItemChanged(self, type_)
