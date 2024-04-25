# This file is part of pydidas.
#
# Copyright 2023 - 2024, Helmholtz-Zentrum Hereon
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
Module with utility functions used in the silx_plot package.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2024, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["get_2d_silx_plot_ax_settings", "user_config_update_func"]

from contextlib import nullcontext

from numpy import ndarray
from qtpy import QtCore


def get_2d_silx_plot_ax_settings(axis: ndarray) -> tuple[float, float]:
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


@QtCore.Slot(str, str)
def user_config_update_func(self, key: str, value: str):
    """
    Handle a user config update.

    Parameters
    ----------
    key : str
        The name of the updated key.
    value :
        The new value of the updated key.
    """
    if key not in ["cmap_name", "cmap_nan_color"]:
        return
    _current_image = self.getImage()
    if _current_image is None:
        _current_cmap = self.getDefaultColormap()
        _context = nullcontext()
    else:
        _current_cmap = _current_image.getColormap()
        _context = QtCore.QSignalBlocker(_current_image)
    with _context:
        if key == "cmap_name":
            _current_cmap.setName(value.lower())
        elif key == "cmap_nan_color":
            _current_cmap.setNaNColor(value)
