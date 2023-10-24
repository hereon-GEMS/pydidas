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
Module with utility functions used in the silx_plot package.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["get_2d_silx_plot_ax_settings"]


from numpy import ndarray


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
