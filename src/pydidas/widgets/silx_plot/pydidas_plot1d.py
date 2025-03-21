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

from qtpy import QtCore, QtWidgets
from silx.gui.plot import Plot1D

from pydidas.core import Dataset
from pydidas.widgets.silx_plot._special_plot_types_button import SpecialPlotTypesButton


class PydidasPlot1D(Plot1D):
    """
    A customized silx.gui.plot.Plot1D with an additional configuration.
    """

    def __init__(self, **kwargs: dict):
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

    def plot_pydidas_dataset(self, data: Dataset, **kwargs: dict):
        """
        Plot a pydidas dataset.

        Parameters
        ----------
        data : pydidas.core.Dataset
            The data to be plotted.
        **kwargs : dict
            Additional keyword arguments to be passed to the silx plot method.
        """
        if kwargs.get("replace", True):
            self.clear_plot()

        self._plot_config = {
            "ax_label_x": data.get_axis_description(0),
            "ax_label_y": kwargs.get(
                "ylabel",
                self._y_label(
                    data.axis_labels[0],
                    data.axis_units[0],
                    data.data_label,
                    data.data_unit,
                ),
            ),
            "kwargs": {
                "linewidth": 1.5,
            }
            | {
                _key: _val
                for _key, _val in kwargs.items()
                if _key in self._allowed_kwargs
            },
        }
        self.setGraphXLabel(self._plot_config.get("ax_label_x", ""))
        self.setGraphYLabel(self._plot_config.get("ax_label_y", ""))
        self._current_raw_data[kwargs.get("legend", "Unnamed curve 1.1")] = (
            data,
            self._plot_config["kwargs"],
        )
        self.addCurve(
            data.axis_ranges[0],
            self._y_function(data.axis_ranges[0], data.array),
            **self._plot_config["kwargs"],
        )

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

    def _activeItemChanged(self, type_):
        """
        Listen for active item changed signal and broadcast signal

        :param item.ItemChangedType type_: The type of item change
        """
        if self.sender() == self._qtapp:
            return
        Plot1D._activeItemChanged(self, type_)
