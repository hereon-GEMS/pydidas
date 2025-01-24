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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Pydidas. If not, see <http://www.gnu.org/licenses/>.

"""
Module with utilities for fitting multiple peaks.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2024 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["MultiPeakMixin"]


import copy
from numbers import Real

from numpy import ndarray


class MultiPeakMixin:
    """
    Mix-In class with common functionality for FitFuncs with multiple peaks.
    """

    @classmethod
    def guess_fit_start_params(cls, x: ndarray, y: ndarray, **kwargs) -> list[Real]:
        """
        Guess the start params for the fit for the given x and y values.

        Parameters
        ----------
        x : nd.ndarray
            The x points of the data.
        y : np.ndarray
            The data values.
        **kwargs : dict
            Additional kwarg arguments. {i} can take any number between 0 and the
            maximum number of supported peaks. Supported keywords are:
            - bg_order : Union[None, 0, 1], optional
                The order of the background. The default is None.
            - center{i}_bounds : Union[None, tuple[Real, Real]], optional
                The low and high bounds for the i-th peak's center position.
            - center{i}_start : Union[None, tuple[Real, Real]], optional
                The starting value for the peak{i} fit. If not given, this defaults to
                the data maximum in the bounds.
            - width{i}_start : Union[None, Real], optional
                The starting sigma value for the peak i.

        Returns
        -------
        list[Real]
            The list with the starting fit parameters.
        """

        def _calc_starting_params(local_kwargs: dict) -> tuple[Real]:
            """Calculate the starting parameters for all the given peaks."""
            _peak_params = []
            _y_temp = y.copy()
            for _index in range(cls.num_peaks):
                _params = cls.guess_peak_start_params(
                    x,
                    _y_temp,
                    _index,
                    **local_kwargs,
                )
                _peak_params.extend(_params)
                _y_temp = _y_temp - cls.func(_params, x)
            _peak_params = cls.sort_fitted_peaks_by_position(
                tuple(_peak_params) + _bg_params
            )
            return _peak_params

        y, _bg_params = cls.estimate_background_params(
            x, y, kwargs.get("bg_order", None)
        )
        _tmp_kwargs = copy.deepcopy(kwargs)
        _tmp_kwargs["bounds"] = (cls.param_bounds_low, cls.param_bounds_high)
        for _i in range(cls.num_peaks):
            _ = _tmp_kwargs.pop(f"center{_i}_start", None)
        _params1 = _calc_starting_params(_tmp_kwargs)
        _new_kwargs = copy.deepcopy(kwargs)
        for _i in range(cls.num_peaks):
            if f"center{_i}_start" not in _new_kwargs:
                _new_kwargs[f"center{_i}_start"] = _params1[
                    cls.param_labels.index(f"center{_i}")
                ]
        _params = _calc_starting_params(_new_kwargs)
        return _params
