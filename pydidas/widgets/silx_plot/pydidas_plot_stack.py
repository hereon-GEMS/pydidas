# This file is part of pydidas.
#
# Copyright 2021-, Helmholtz-Zentrum Hereon
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
Module with the PydidasPlotStack, a QStackedWidget with two plots for 1d and 2d
datasets.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ["PydidasPlotStack"]


from typing import Union

from qtpy import QtCore, QtWidgets

from ...core import Dataset
from .pydidas_plot1d import PydidasPlot1D
from .pydidas_plot2d import PydidasPlot2D


class PydidasPlotStack(QtWidgets.QStackedWidget):
    """
    A stack with two plots for 1d and 2d data which selects the correct to display.

    Parameters
    ----------
    parent : Union[QtWidgets.QWidget, None]
    use_data_info_action : bool, optional
        Flag to use the PydidasGetDataInfoAction to display information about a
        result datapoint. The default is False.
    diffraction_exp : DiffractionExperiment
        The DiffractionExperiment instance to be used in the PydidasPlot2D for
        the coordinate system.
    """

    sig_get_more_info_for_data = QtCore.Signal(float, float)

    def __init__(self, parent: Union[QtWidgets.QWidget, None] = None, **kwargs):
        QtWidgets.QStackedWidget.__init__(self, parent)
        self._frame1d = QtWidgets.QWidget()
        self._frame1d.setLayout(QtWidgets.QGridLayout())
        self._frame2d = QtWidgets.QWidget()
        self._frame2d.setLayout(QtWidgets.QGridLayout())
        self._1dplot = None
        self._2dplot = None
        self._config = {
            "use_data_info_action": kwargs.get("use_data_info_action", False),
            "diffraction_exp": kwargs.get("diffraction_exp", None),
        }
        self.addWidget(self._frame1d)
        self.addWidget(self._frame2d)

    def plot_data(self, data: Dataset, **kwargs):
        """
        Plot the given data.

        Parameters
        ----------
        data : pydidas.core.Dataset
            The data to be plotted.
        **kwargs : dict
            Any additional keywords to be passed to the plot.
        """
        _dim = data.ndim
        self._create_widget_if_required(_dim)
        self.setCurrentIndex(_dim - 1)
        _plot = getattr(self, f"_{_dim}dplot")
        _title = kwargs.pop("title", None)
        if _title is not None:
            _plot.setGraphTitle(_title)
        _plot.plot_pydidas_dataset(data, **kwargs)

    def clear_plots(self):
        """
        Clear all plots.
        """
        if self._1dplot is not None:
            self._1dplot.clear_plot()
        if self._2dplot is not None:
            self._2dplot.clear_plot()

    def _create_widget_if_required(self, dim: int):
        """
        Create the plot widget if required.

        Parameters
        ----------
        dim : int
            The data dimension
        """
        _plot = getattr(self, f"_{dim}dplot")
        if _plot is None:
            _plot = PydidasPlot1D() if dim == 1 else PydidasPlot2D(**self._config)
            setattr(self, f"_{dim}dplot", _plot)
            _widget = getattr(self, f"_frame{dim}d")
            _widget.layout().addWidget(_plot)
            if dim == 2:
                _plot.sig_get_more_info_for_data.connect(
                    self.sig_get_more_info_for_data
                )
