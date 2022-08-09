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
Module with a function to add a QStackedWidget with 1d and 2d plots to the input frame.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ["create_silx_plot_stack", "get_2d_silx_plot_ax_settings"]

from qtpy import QtWidgets

from .pydidas_plot1d import PydidasPlot1D
from .pydidas_plot2d import PydidasPlot2D
from ...core.constants import (
    EXP_EXP_POLICY,
)


def create_silx_plot_stack(frame, gridPos=None):
    """
    Create a QStackedWidget with 1D and 2D plot widgets in the input frame.


    Parameters
    ----------
    frame : pydidas.core.BaseFrame
        The input frame.
    gridPos : Union[tuple, None], optional
        The gridPos for the new widget. The default is None.

    Returns
    -------
    frame : pydidas.core.BaseFrame
        The updated frame.
    """
    frame._widgets["plot1d"] = PydidasPlot1D()
    frame._widgets["plot2d"] = PydidasPlot2D()
    frame.add_any_widget(
        "plot_stack",
        QtWidgets.QStackedWidget(),
        alignment=None,
        gridPos=gridPos,
        visible=True,
        stretch=(1, 1),
        sizePolicy=EXP_EXP_POLICY,
    )
    frame._widgets["plot_stack"].addWidget(frame._widgets["plot1d"])
    frame._widgets["plot_stack"].addWidget(frame._widgets["plot2d"])


def get_2d_silx_plot_ax_settings(axis):
    """
    Get the axis settings to have pixels centered at their values.

    Parameters
    ----------
    axis : np.ndarray
        The numpy array with the axis positions.

    Returns
    -------
    _origin : float
        The value for the axis origin.
    _scale : float
        The value for the axis scale to squeeze it into the correct
        dimensions for silx ImageView.
    """
    _delta = axis[1] - axis[0]
    _scale = (axis[-1] - axis[0] + _delta) / axis.size
    _origin = axis[0] - _delta / 2
    return _origin, _scale
