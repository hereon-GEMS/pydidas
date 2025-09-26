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
Module with PydidasPlot1D class which adds configurations to the base silx Plot1D.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["PydidasPlot1D"]


import inspect
from typing import Any

from qtpy import QtCore, QtWidgets
from silx.gui.plot import Plot1D

from pydidas.core import Dataset, PydidasQsettings, UserConfigError
from pydidas.widgets.silx_plot._special_plot_types_button import SpecialPlotTypesButton


_QSETTINGS = PydidasQsettings()


class PydidasPlot1D(Plot1D):
    """
    A customized silx.gui.plot.Plot1D with an additional configuration.
    """

    @staticmethod
    def _check_data_dimensions(data: Dataset):
        """
        Check the data dimensions.

        Parameters
        ----------
        data : Dataset
            The data to display.
        """
        if not data.ndim == 2:
            raise UserConfigError(
                "The given dataset does not have exactly 2 dimensions. Please check "
                f"the input data definition:\n The input data has {data.ndim} "
                "dimensions."
            )
        _n_max = _QSETTINGS.value("user/max_number_curves", int)
        if data.shape[0] > _n_max:
            raise UserConfigError(
                f"The number of given curves ({data.shape[0]}) exceeds the maximum "
                f"number of curves allowed ({_n_max}). \n"
                "Please limit the data range to be displayed or increase the maximum "
                "number of curves in the user settings (Options -> User config). "
                "Please note that displaying a large number of curves will slow down "
                "the plotting performance."
            )

    def __init__(self, **kwargs: Any):
        Plot1D.__init__(
            self, parent=kwargs.get("parent", None), backend=kwargs.get("backend", None)
        )
        self._allowed_kwargs = [
            _key
            for _key, _value in inspect.signature(self.addCurve).parameters.items()
            if _value.default is not inspect.Parameter.empty
        ]

        self.getRoiAction().setVisible(False)
        self.getFitAction().setVisible(False)

        self._qtapp = QtWidgets.QApplication.instance()
        if hasattr(self._qtapp, "sig_mpl_font_change"):
            self._qtapp.sig_mpl_font_change.connect(self.update_mpl_fonts)

        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        if kwargs.get("use_special_plots", True):
            self._add_special_plot_actions()
        self._y_function = SpecialPlotTypesButton.func_generic
        self._y_label = SpecialPlotTypesButton.label_generic
        self._current_raw_data = {}
        self._plot_config = {}

    def _add_special_plot_actions(self):
        """
        Add the action to change the type of the plot.

        This action allows to display image coordinates in polar coordinates
        (with r / mm, 2theta / deg or q / nm^-1) scaling.
        """
        self._plot_type = SpecialPlotTypesButton(parent=self, plot=self)
        self._toolbar.addWidget(self._plot_type)
        self._plot_type.sig_new_plot_type.connect(self._process_plot_type)

    def _process_plot_type(self):
        """
        Process the changed plot type and set the function to update the plotted value.
        """
        self.clear_plot(clear_data=False)
        self._y_function = self._plot_type.plot_yfunc
        self._y_label = self._plot_type.plot_ylabel()
        for _legend, (_data, _kwargs) in self._current_raw_data.items():
            _kwargs["legend"] = _legend
            self.plot_pydidas_dataset(_data, **_kwargs)

    def plot_pydidas_dataset(self, data: Dataset, **kwargs: Any):
        """
        Plot a pydidas dataset.

        Parameters
        ----------
        data : pydidas.core.Dataset
            The data to be plotted.
        **kwargs : Any
            Additional keyword arguments to be passed to the silx plot method.
        """
        if kwargs.get("replace", True):
            self.clear_plot()
        _i_data = 0 if data.ndim == 1 else 1
        if data.ndim > 1:
            self._check_data_dimensions(data)
        _ylabel = self._y_label(
            data.axis_labels[_i_data],
            data.axis_units[_i_data],
            data.data_label,
            data.data_unit,
        )
        _allowed_kwargs = {
            _key: _val for _key, _val in kwargs.items() if _key in self._allowed_kwargs
        }
        self._plot_config = {
            "ax_label_x": data.get_axis_description(_i_data) or "index",
            "ax_label_y": kwargs.get("ylabel", _ylabel),
            "title": kwargs.get("title", ""),
            "kwargs": {
                "linewidth": kwargs.get("linewidth", 1.5),
                "linestyle": kwargs.get("linestyle", "-"),
                "symbol": kwargs.get("symbol", None),
            }
            | _allowed_kwargs,
        }
        self.setGraphXLabel(self._plot_config.get("ax_label_x", ""))
        self.setGraphYLabel(self._plot_config.get("ax_label_y", ""))
        if self._plot_config.get("title"):
            self.setGraphTitle(self._plot_config["title"])
        self._current_raw_data[kwargs.get("legend", "Curve")] = (
            data,
            self._plot_config["kwargs"],
        )
        if data.ndim == 1:
            self.addCurve(
                data.axis_ranges[_i_data],
                self._y_function(data.axis_ranges[_i_data], data.array),
                **self._plot_config["kwargs"],
            )
        else:
            _label = data.axis_labels[0] + " = {value:.4f} " + data.axis_units[0]
            _x = data.axis_ranges[1]
            for _index, _pos in enumerate(data.axis_ranges[0]):
                self.addCurve(
                    _x,
                    self._y_function(_x, data.array[_index]),
                    legend=_label.format(value=_pos),
                    # xlabel=self._plot_config["kwargs"]["ax_label_x"],
                    ylabel=_ylabel,
                )
            self.setActiveCurve(_label.format(value=_x[0]))

    # display_data is a generic alias used in all custom silx plots to have a
    # uniform interface call to display data
    display_data = plot_pydidas_dataset

    def clear_plot(self, clear_data: bool = True):
        """
        Clear the plot and remove all items.

        Parameters
        ----------
        clear_data : bool, optional
            Flag to remove all items from the stored data dictionary as well.
        """
        self.remove()
        self.setGraphTitle("")
        self.setGraphYLabel("")
        self.setGraphXLabel("")
        if clear_data:
            self._current_raw_data = {}

    @QtCore.Slot()
    def update_mpl_fonts(self):
        """
        Update the plot's fonts.
        """
        _curve = self.getCurve()
        if _curve is None:
            return
        _xarr, _yarr, _, _ = _curve.getData()
        _title = self.getGraphTitle()
        self.getBackend().fig.gca().cla()
        self.addCurve(_xarr, _yarr, **self._plot_config.get("kwargs", {}))
        self.setGraphTitle(_title)
        self.setGraphXLabel(self._plot_config.get("ax_label_x", ""))
        self.setGraphYLabel(self._plot_config.get("ax_label_y", ""))

    # TODO: check if still needed with silx 2.2.2
    def _activeItemChanged(self, type_):
        """
        Listen for active item changed signal and broadcast signal

        :param item.ItemChangedType type_: The type of item change
        """
        if self.sender() == self._qtapp:
            return
        Plot1D._activeItemChanged(self, type_)
