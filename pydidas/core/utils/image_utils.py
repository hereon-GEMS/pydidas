# This file is part of pydidas.
#
# Copyright 2024, Helmholtz-Zentrum Hereon
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
__copyright__ = "Copyright 2024, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["calculate_histogram_limits"]


import numpy as np

from ..exceptions import UserConfigError
from ..pydidas_q_settings import PydidasQsettings


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
    _qsettings = PydidasQsettings()

    _fraction_low = _qsettings.value("user/histogram_outlier_fraction_low", dtype=float)
    _fraction_high = 1 - _qsettings.value(
        "user/histogram_outlier_fraction_high", dtype=float
    )
    if _fraction_high - _fraction_low <= 0:
        raise UserConfigError(
            "The selected outlier fractions are too large. No data left to display."
        )
    _cmap_limit_low = None
    _cmap_limit_high = None
    _filtered_data = data[np.isfinite(data)]
    if _fraction_high < 1:
        # _counts, _edges = np.histogram(_filtered_data, bins=4096)
        # _cumcounts = np.cumsum(_counts / _filtered_data.size)
        # _found_indices = np.where(_cumcounts <= _fraction_high)[0]
        # _index_low = 0 if _found_indices.size == 0 else _found_indices[-1]
        # _index_high = min(_counts.size, _index_low + 1)
        # print(_index_low, _index_high, _cumcounts[_index_low], _cumcounts[_index_high])
        #
        # _counts_fine, _edges_fine = np.histogram(
        #     _filtered_data, bins=4096, range=(_edges[_index_low], _edges[_index_high])
        # )
        # _cumcounts_fine = np.cumsum(_counts_fine / _filtered_data.size) + _cumcounts[_index_low]
        # _found_indices = np.where(_cumcounts_fine <= _fraction_high)[0]
        # _index_low_fine = 0 if _found_indices.size == 0 else _found_indices[-1]
        # _cmap_limit_high = _edges_fine[_index_low_fine]
        # Initial histogram to find the coarse range
        _counts, _edges = np.histogram(_filtered_data, bins=4096)
        _cumcounts = np.cumsum(_counts / _filtered_data.size)
        _index_low = np.max(np.where(_cumcounts <= _fraction_high)[0], initial=0)

        _counts_fine, _edges_fine = np.histogram(
            _filtered_data,
            bins=4096,
            range=(_edges[_index_low], _edges[min(_index_low + 1, _counts.size)]),
        )
        _cumcounts_fine = np.cumsum(_counts_fine / _filtered_data.size) + _cumcounts[_index_low]
        _index_low_fine = np.max(np.where(_cumcounts_fine <= _fraction_high)[0], initial=0)
        _cmap_limit_high = _edges_fine[_index_low_fine]
    if _fraction_low > 0:
        _range = (
            _filtered_data.min(),
            _cmap_limit_high if _cmap_limit_high is not None else _filtered_data.max(),
        )
        print(_range)
        _counts, _edges = np.histogram(_filtered_data, bins=4096, range=_range)
        _cumcounts = np.cumsum(_counts / _filtered_data.size)
        print(_cumcounts)
        _index_stop_edge = min(
            _counts.size, np.where(_fraction_low <= _cumcounts)[0][0] + 1
        )

        _counts_fine, _edges_fine = np.histogram(
            data, bins=32768, range=(_edges[0], _edges[_index_stop_edge])
        )
        _cumcounts_fine = np.cumsum(_counts_fine / _filtered_data.size)
        _index_stop_edge_fine = min(
            _counts_fine.size, np.where(_fraction_low <= _cumcounts_fine)[0][0] + 1
        )
        _cmap_limit_low = _edges_fine[_index_stop_edge_fine]
    return _cmap_limit_low, _cmap_limit_high
