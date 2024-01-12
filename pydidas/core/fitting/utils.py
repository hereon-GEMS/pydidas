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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Pydidas. If not, see <http://www.gnu.org/licenses/>.

"""
Module with utilities for fitting multiple peaks.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2024, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["get_bounds_indices", "DoublePeakMixin", "TriplePeakMixin"]


import copy
from typing import Union

from numpy import amax, amin, delete, ndarray, r_, where

from ..exceptions import UserConfigError


def get_bounds_indices(x: ndarray, index: int, **kwargs: dict) -> ndarray:
    """
    Get the indices for the bounds of the center positions.

    Parameters
    ----------
    x : ndarray
        The x position array.
    index : int
        The peak index
    **kwargs : dict
        Any calling kwargs.

    Returns
    -------
    ndarray
        The array with the indices which are inside of the bounds.
    """
    _bounds = kwargs.get(f"center{index}_bounds", (amin(x), amax(x)))
    _indices = where((x >= _bounds[0]) & (x <= _bounds[1]))[0]
    if _indices.size == 0:
        raise UserConfigError(
            f"The given bounds ({round(_bounds[0], 5)}, "
            f"{round(_bounds[1], 5)}) for the center {index} position of the "
            "fit do not include any datapoints! Please check the data range and "
            "boundaries."
        )
    return _indices


class DoublePeakMixin:

    """
    Mix-In class with common functionality for FitFuncs with multiple peaks.
    """

    num_peaks = 2

    @classmethod
    def profile(cls, c: tuple[float], x: ndarray) -> ndarray:
        """
        Get the double peak profile values.

        Parameters
        ----------
        c : tuple[float]
            The tuple with the function fitting parameters. Detailed parameters are
            specified by the concrete function.
        x : np.ndarray
            The x data points.

        Returns
        -------
        np.ndarray
            The function values for the given x values.
        """
        _n_params = cls.num_peak_params
        _peaks = sum(
            cls.func(c[_i_peak * _n_params : (_i_peak + 1) * _n_params], x)
            for _i_peak in range(cls.num_peaks)
        )
        _background = cls.calculate_background(c[cls.num_peaks * _n_params :], x)
        return _peaks + _background

    @classmethod
    def guess_fit_start_params(cls, x: ndarray, y: ndarray, **kwargs) -> list[float]:
        """
        Guess the start params for the fit for the given x and y values.

        Parameters
        ----------
        x : nd.ndarray
            The x points of the data.
        y : np.ndarray
            The data values.
        **kwargs : dict
            Additional kwarg arguments. {i} can take any number between 1 and the
            maximum number of supported peaks. Supported keywords are:
            - bg_order : Union[None, 0, 1], optional
                The order of the background. The default is None.
            - center{i]_bounds : Union[None, tuple[float, float]], optional
                The low and high bounds for the i-th peak's center position.
            - center{i}_start :  Union[None, tuple[float, float]], optional
                The starting value for the peak{i} fit. If not given, this defaults to
                the data maximum in the bounds.
            - width{i}_start : Union[None, float], optional
                The starting sigma value for the peak i.

        Returns
        -------
        list[float]
            The list with the starting fit parameters.
        """

        def _calc_starting_params(
            *indices: tuple[ndarray], **local_kwargs: dict
        ) -> list[float]:
            """Calculate the starting parameters for all the given peaks."""
            _peak_params = []
            _y_temp = y.copy()
            for _index in range(cls.num_peaks):
                _params = cls.guess_peak_start_params(
                    x[indices[_index]],
                    _y_temp[indices[_index]],
                    _index + 1,
                    **local_kwargs,
                )
                _peak_params.extend(_params)
                _y_temp = _y_temp - cls.func(_params, x)

            _peak_params = cls.sort_fitted_peaks_by_position(_peak_params + _bg_params)
            return _peak_params

        _indices = [
            get_bounds_indices(x, 1 + _i_peak, **kwargs)
            for _i_peak in range(cls.num_peaks)
        ]
        y, _bg_params = cls.calculate_background_params(
            x, y, kwargs.get("bg_order", None)
        )

        _tmp_kwargs = copy.deepcopy(kwargs)
        _tmp_kwargs["bounds"] = (cls.param_bounds_low, cls.param_bounds_high)
        for _i in range(1, 1 + cls.num_peaks):
            _ = _tmp_kwargs.pop(f"center{_i}_start", None)
        _params1 = _calc_starting_params(*_indices, **_tmp_kwargs)

        _new_kwargs = copy.deepcopy(kwargs)
        for _i in range(1, 1 + cls.num_peaks):
            if f"center{_i}_start" not in _new_kwargs:
                _new_kwargs[f"center{_i}_start"] = _params1[
                    cls.param_labels.index(f"center{_i}")
                ]
        _params = _calc_starting_params(*_indices, **_new_kwargs)
        return _params

    @classmethod
    def sort_fitted_peaks_by_position(cls, c: Union[ndarray, list]) -> list[float]:
        """
        Sort the peaks by their center's position.

        Parameters
        ----------
        c : list[float]
            The fitted parameters.

        Returns
        -------
        list[float]
            The sorted fitted parameters.
        """
        _center_indices = [
            cls.param_labels.index(f"center{_i}") for _i in range(1, 1 + cls.num_peaks)
        ]
        _centers = r_[[c[_center_index] for _center_index in _center_indices]]
        _sorted_centers = r_[sorted(_centers[:])]
        if (_centers == _sorted_centers).all():
            return c
        _copy = list(c.copy()) if isinstance(c, ndarray) else c.copy()
        _sorted_peaks = []
        for _ in range(cls.num_peaks):
            _i0 = _centers.argmin() * cls.num_peak_params
            _centers = delete(_centers, _centers.argmin())
            for _ in range(cls.num_peak_params):
                _sorted_peaks.append(_copy.pop(_i0))
        _sorted_peaks = _sorted_peaks + _copy
        return _sorted_peaks


class TriplePeakMixin:

    """
    Mix-In class with common functionality for FitFuncs with a triple peak.
    """

    num_peaks = 3

    @classmethod
    def profile(cls, c: tuple[float], x: ndarray) -> ndarray:
        """
        Get the triple peak profile values.

        Parameters
        ----------
        c : tuple[float]
            The tuple with the function fitting parameters. Detailed parameters are
            specified by the concrete function.
        x : np.ndarray
            The x data points.

        Returns
        -------
        np.ndarray
            The function values for the given x values.
        """
        _n = cls.num_peak_params
        _triple_peak = (
            cls.func(c[0:_n], x)
            + cls.func(c[_n : 2 * _n], x)
            + cls.func(c[2 * _n : 3 * _n], x)
        )
        _background = cls.calculate_background(c[3 * _n :], x)
        return _triple_peak + _background

    @classmethod
    def guess_fit_start_params(cls, x: ndarray, y: ndarray, **kwargs) -> list[float]:
        """
        Guess the start params for the fit for the given x and y values.

        Parameters
        ----------
        x : nd.ndarray
            The x points of the data.
        y : np.ndarray
            The data values.
        **kwargs : dict
            Additional kwarg arguments. Supported keywords are:
            - bg_order : Union[None, 0, 1], optional
                The order of the background. The default is None.
            - center<i>_bounds : Union[None, tuple[float, float]], optional
                The low and high bounds for the <i>'s peak's center position.
            - center<i>_start :  Union[None, tuple[float, float]], optional
                The starting value for the peak<i> fit. If not given, this defaults to
                the maximum position in the bounds.
            - width<i>_start : Union[None, float], optional
                The starting sigma value for the peak <i>.

        Returns
        -------
        list[float]
            The list with the starting fit parameters.
        """

        _indices1 = get_bounds_indices(x, 1, **kwargs)
        _indices2 = get_bounds_indices(x, 2, **kwargs)
        _indices3 = get_bounds_indices(x, 3, **kwargs)
        _bg_order = kwargs.get("bg_order", None)
        y, _bg_params = cls.calculate_background_params(x, y, _bg_order)

        _params_peak1 = cls.guess_peak_start_params(
            x[_indices1], y[_indices1], 1, **kwargs
        )

        _y_temp = y - cls.func(_params_peak1, x)
        _params_peak2 = cls.guess_peak_start_params(
            x[_indices2], _y_temp[_indices2], 2, **kwargs
        )

        _y_temp = _y_temp - cls.func(_params_peak2, x)
        _params_peak3 = cls.guess_peak_start_params(
            x[_indices3], _y_temp[_indices3], 3, **kwargs
        )
        return _params_peak1 + _params_peak2 + _params_peak3 + _bg_params

    @classmethod
    def sort_fitted_peaks_by_position(
        cls, c: Union[ndarray, list[float]]
    ) -> list[float]:
        """
        Sort the peaks by their center's position.

        Parameters
        ----------
        c : Union[ndarray, list[float]]
            The fitted parameters.

        Returns
        -------
        list[float]
            The sorted fitted parameters.
        """
        _index1 = cls.param_labels.index("center1")
        _index2 = cls.param_labels.index("center2")
        _index3 = cls.param_labels.index("center3")
        _copy = list(c.copy()) if isinstance(c, ndarray) else c.copy()
        if c[_index1] <= c[_index2] <= c[_index3]:
            return _copy
        _centers = r_[c[_index1], c[_index2], c[_index3]]
        _tmp_peaks = []
        for _ in range(2):
            _i0 = _centers.argmin() * cls.num_peak_params
            _centers = delete(_centers, _centers.argmin())
            for _ in range(cls.num_peak_params):
                _tmp_peaks.append(_copy.pop(_i0))
        _tmp_peaks = _tmp_peaks + _copy
        return _tmp_peaks
