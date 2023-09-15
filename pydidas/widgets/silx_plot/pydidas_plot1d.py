# This file is part of pydidas.
#
# Copyright 2023, Helmholtz-Zentrum Hereon
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
__copyright__ = "Copyright 2023, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["PydidasPlot1D"]


import inspect

from qtpy import QtCore, QtWidgets
from silx.gui.plot import Plot1D


class PydidasPlot1D(Plot1D):
    """
    A customized silx.gui.plot.Plot1D with an additional configuration.
    """

    def __init__(self, parent=None, backend=None):
        Plot1D.__init__(self, parent, backend)
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

    def plot_pydidas_dataset(self, data, **kwargs):
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
            "ax_label_x": (
                data.axis_labels[0]
                + (" / " + data.axis_units[0] if len(data.axis_units[0]) > 0 else "")
            ),
            "ax_label_y": (
                data.data_label
                + (" / " + data.data_unit if len(data.data_unit) > 0 else "")
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
        self.setGraphXLabel(self._plot_config["ax_label_x"])
        self.setGraphYLabel(self._plot_config["ax_label_y"])
        self.addCurve(
            data.axis_ranges[0],
            data.array,
            **self._plot_config["kwargs"],
        )

    def clear_plot(self):
        """
        Clear the plot and remove all items.
        """
        self.remove()
        self.setGraphTitle("")
        self.setGraphYLabel("")
        self.setGraphXLabel("")

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
        self.addCurve(_xarr, _yarr, **self._plot_config["kwargs"])
        self.setGraphTitle(_title)
        self.setGraphXLabel(self._plot_config["ax_label_x"])
        self.setGraphYLabel(self._plot_config["ax_label_y"])
