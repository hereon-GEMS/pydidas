# This file is part of pydidas.
#
# Copyright 2024 - 2025, Helmholtz-Zentrum Hereon
# SPDX-License-Identifier: GPL-3.0-only
#
# pydidas is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 3 as
# published by the Free Software Foundation.
#
# Pydidas is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or _NESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Pydidas. If not, see <http://www.gnu.org/licenses/>.

"""
The math_utils module includes functions for mathematical operations used in pydidas.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2024 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["calculate_histogram_limits"]


from numbers import Real

import numpy as np

from pydidas.core.exceptions import UserConfigError
from pydidas.core.pydidas_q_settings import PydidasQsettings


__NUM_BINS = 32768


def calculate_histogram_limits(data: np.ndarray) -> tuple:
    """
    Calculate the limits for the histogram display, based on the user settings.

    Parameters
    ----------
    data : np.ndarray
        The image data to calculate the histogram limits for.

    Returns
    -------
    tuple[float, float]
        A tuple with the low and high limits for the histogram display
    """
    _data_min = data.min()
    _data_max = data.max()

    _qsettings = PydidasQsettings()

    _threshold_low = _qsettings.value(
        "user/histogram_outlier_fraction_low", dtype=float
    )
    _threshold_high = 1 - _qsettings.value(
        "user/histogram_outlier_fraction_high", dtype=float
    )
    if _threshold_high - _threshold_low <= 0:
        raise UserConfigError(
            "The selected outlier fractions are too large. No data left to display."
        )
    _cmap_limit_low = None
    _cmap_limit_high = None
    _filtered_data = data[np.isfinite(data)]
    if _threshold_high < 1:
        _cmap_limit_high = __calc_upper_limit(_filtered_data, _threshold_high)
    if _threshold_low > 0:
        _cmap_limit_low = __calc_lower_limit(
            _filtered_data, _threshold_low, _cmap_limit_high
        )
    if isinstance(_cmap_limit_low, Real) and _cmap_limit_low > _data_max:
        _cmap_limit_low = _data_min - 1e-3 * (_data_max - _data_min)
    if isinstance(_cmap_limit_high, Real) and _cmap_limit_high < _data_min:
        _cmap_limit_high = _data_max + 1e-3 * (_data_max - _data_min)
    return _cmap_limit_low, _cmap_limit_high


def __calc_upper_limit(data: np.ndarray, threshold_high: float) -> float:
    """
    Calculate the upper limit for the histogram display.

    Parameters
    ----------
    data : np.ndarray
        The image data to calculate the histogram limits for.
    threshold_high : float
        The relative threshold of high data values data to be ignored.

    Returns
    -------
    float
        The upper limit for the histogram display.
    """
    _counts, _edges = np.histogram(data, bins=__NUM_BINS)
    _cumcounts = np.cumsum(_counts / data.size)
    _bin_index_low = np.max(np.where(_cumcounts <= threshold_high)[0], initial=-1)
    try:
        # new range must be range of bin following low bin:
        _new_range = (_edges[_bin_index_low + 1], _edges[_bin_index_low + 2])
    except IndexError:
        _index = max(_bin_index_low, 0)
        _new_range = (_edges[_index], _edges[_index + 1])
    _counts_fine, _edges_fine = np.histogram(data, bins=__NUM_BINS, range=_new_range)
    _cumcounts_fine = np.cumsum(_counts_fine / data.size) + _cumcounts[_bin_index_low]
    _index_new = np.max(np.where(_cumcounts_fine <= threshold_high)[0], initial=0)
    return _edges_fine[_index_new + 1]


def __calc_lower_limit(
    data: np.ndarray, threshold_low: float, cmap_high_lim: float
) -> float:
    """
    Calculate the lower limit for the histogram display.

    Parameters
    ----------
    data : np.ndarray
        The image data to calculate the histogram limits for.
    threshold_low : float
        The relative threshold of low data values data to be ignored.
    cmap_high_lim : float
        The upper limit for the histogram display.

    Returns
    -------
    float
        The lower limit for the histogram display.
    """
    _range = (
        data.min(),
        cmap_high_lim if cmap_high_lim is not None else data.max(),
    )
    if _range[0] >= _range[1]:
        _range = (_range[0] - 1e-4, _range[0] + 1e-4)
    _counts, _edges = np.histogram(data, bins=__NUM_BINS, range=_range)
    _cumcounts = np.cumsum(_counts / data.size)
    _bin_index_fine = np.max(np.where(_cumcounts <= threshold_low)[0], initial=0)
    _new_range = (_edges[_bin_index_fine], _edges[_bin_index_fine + 1])
    _counts_fine, _edges_fine = np.histogram(
        data,
        bins=__NUM_BINS,
        range=(_edges[_bin_index_fine], _edges[_bin_index_fine + 1]),
    )
    _cumcounts_fine = np.cumsum(_counts_fine / data.size) + _cumcounts[_bin_index_fine]
    _index_new = np.min(np.where(_cumcounts_fine >= threshold_low)[0], initial=0)
    return _edges_fine[_index_new]
