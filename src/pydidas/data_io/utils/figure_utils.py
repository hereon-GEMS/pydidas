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
Module with utility functions for matplotlib figure creation.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["calculate_fig_size_arguments"]


def calculate_fig_size_arguments(
    image_shape: tuple[float], target_size_inches: int = 10
) -> tuple[tuple[float, float], float]:
    """
    Get the arguments to create a new figure with image data in the correct
    size.

    Parameters
    ----------
    image_shape : tuple
        The shape of the image.
    target_size_inches : int, optional
        The larger of the two image dimensions, given in inch. The default is
        10.

    Returns
    -------
    fig_shape : tuple[float]
        The shape of the figure to match the image shape.
    fig_dpi : float
        The figure dpi settings to achieve the correct size.
    """
    nx = image_shape[1]
    ny = image_shape[0]
    size_x = target_size_inches * nx / max(nx, ny)
    size_y = target_size_inches * ny / max(nx, ny)
    fig_shape = (size_x, size_y)
    fig_dpi = max(nx, ny) / target_size_inches
    return fig_shape, fig_dpi
