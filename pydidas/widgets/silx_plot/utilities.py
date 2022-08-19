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
__all__ = ["get_2d_silx_plot_ax_settings", "get_pydidas_qt_icon"]

import os

from qtpy import QtGui

from ...core.utils import get_pydidas_icon_path


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


def get_pydidas_qt_icon(filename):
    """
    Get the QIcon from the file with the given name.

    Parameters
    ----------
    filename : str
        The filename of the image. Only the filename in the pydidas icon path is
        needed.

    Returns
    -------
    QtGui.QIcon
        The QIcon created from the image file.
    """
    return QtGui.QIcon(os.path.join(get_pydidas_icon_path(), filename))
