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
Module with utility functions used in the silx_plot package.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["get_2d_silx_plot_ax_settings"]


from pydidas.core import Dataset


def get_2d_silx_plot_ax_settings(data: Dataset) -> tuple[float, float]:
    """
    Get the axis settings to have pixels centered at their values.

    Parameters
    ----------
    data : Dataset
        The dataset to get the axis settings from.

    Returns
    -------
    origins : tuple[float, float]
        The values for the axis origins.
    scales : tuple[float, float]
        The values for the axis scales to squeeze it into the correct
        dimensions for silx plotting.
    """
    origins = []
    scales = []
    # calling axis #1 with x first because silx expects (x, y) values.
    for _dim in (1, 0):
        _ax = data.get_axis_range(_dim)
        _delta = (_ax.max() - _ax.min()) / _ax.size
        scales.append(_delta * (_ax.size + 1) / _ax.size)
        origins.append(_ax[0] - _delta / 2)
    return tuple(origins), tuple(scales)
