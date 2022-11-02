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
Module with PydidasPlot1D class which adds configurations to the base silx Plot1D.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ["PydidasPlot1D"]

from qtpy import QtCore
from silx.gui.plot import Plot1D


class PydidasPlot1D(Plot1D):
    """
    A customized silx.gui.plot.Plot1D with an additional configuration.
    """

    def __init__(self, parent=None, backend=None):
        Plot1D.__init__(self, parent, backend)

        self.getRoiAction().setVisible(False)
        self.getFitAction().setVisible(False)

        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

    def plot_pydidas_dataset(self, data, replace=True, title=None, legend=None):
        """
        Plot a pydidas dataset.

        Parameters
        ----------
        data : pydidas.core.Dataset
            The data to be plotted.
        replace : bool
            Keyword to replace the active plot. If False, the new graph will be added
            to the existing graph. THe default is True.
        title : Union[None, str], optional
            The title for the plot. If None, no title will be added to the plot.
        legend : Union[None, str], optional
            If desired, a legend entry for this curve. If None, no legend
            entry will be added. The default is None.
        """
        if replace:
            self.clear_plot()

        _x_axlabel = data.axis_labels[0] + (
            " / " + data.axis_units[0] if len(data.axis_units[0]) > 0 else ""
        )
        _y_axlabel = data.data_label + (
            " / " + data.data_unit if len(data.data_unit) > 0 else ""
        )
        self.addCurve(
            data.axis_ranges[0],
            data.array,
            linewidth=1.5,
            legend=legend,
            replace=replace,
        )
        self.setGraphYLabel(_y_axlabel)
        self.setGraphXLabel(_x_axlabel)
        if title is not None:
            self.setGraphTitle(title)

    def clear_plot(self):
        """
        Clear the plot and remove all items.
        """
        self.remove()
        self.setGraphTitle("")
        self.setGraphYLabel("")
        self.setGraphXLabel("")
