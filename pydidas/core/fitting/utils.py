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
Module with utilities for peak fitting.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["get_bounds_indices", "DoublePeakMixin", "TriplePeakMixin"]


from typing import List, Tuple, Union

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
    Mix-In class with common functionality for FitFuncs with a double peak.
    """

    num_peaks = 2

    @classmethod
    def profile(cls, c: Tuple[float], x: ndarray) -> ndarray:
        """
        Get the double peak profile values.

        Parameters
        ----------
        c : Tuple[float]
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
        _double_peak = cls.func(c[0:_n], x) + cls.func(c[_n : 2 * _n], x)
        _background = cls.calculate_background(c[2 * _n :], x)
        return _double_peak + _background

    @classmethod
    def guess_fit_start_params(cls, x: ndarray, y: ndarray, **kwargs) -> List[float]:
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
            - center1_bounds : Union[None, Tuple[float, float]], optional
                The low and high bounds for the first peak's center position.
            - center2_bounds : Union[None, Tuple[float, float]], optional
                The low and high bounds for the second peak's center position.
            - center1_start :  Union[None, Tuple[float, float]], optional
                The starting value for the peak1 fit. If not given, this defaults to
                the maximum position in the bounds.
            - center2_start :  Union[None, float], optional
                The starting value for the peak2 fit. If not given, this defaults to
                the maximum position in the bounds.
            - width1_start : Union[None, float], optional
                The starting sigma value for the peak 1.
            - width2_start : Union[None, float], optional
                The starting sigma value for the peak 2.

        Returns
        -------
        List[float]
            The list with the starting fit parameters.
        """
        _indices1 = get_bounds_indices(x, 1, **kwargs)
        _indices2 = get_bounds_indices(x, 2, **kwargs)
        _bg_order = kwargs.get("bg_order", None)
        y, _bg_params = cls.calculate_background_params(x, y, _bg_order)

        _params_peak1 = cls.guess_peak_start_params(
            x[_indices1], y[_indices1], 1, **kwargs
        )

        _y_temp = y - cls.func(_params_peak1, x)
        _params_peak2 = cls.guess_peak_start_params(
            x[_indices2], _y_temp[_indices2], 2, **kwargs
        )
        return _params_peak1 + _params_peak2 + _bg_params

    @classmethod
    def sort_fitted_peaks_by_position(cls, c: List[float]) -> List[float]:
        """
        Sort the peaks by their center's position.

        Parameters
        ----------
        c : List[float]
            The fitted parameters.

        Returns
        -------
        List[float]
            The sorted fitted parameters.
        """
        _index1 = cls.param_labels.index("center1")
        _index2 = cls.param_labels.index("center2")
        if c[_index1] <= c[_index2]:
            return c
        _tmp_dict = dict(zip(cls.param_labels, [None] * len(cls.param_labels)))
        for _key, _value in zip(cls.param_labels, c):
            _newkey = _key[:-1] + ("1" if _key.endswith("2") else "2")
            _tmp_dict[_newkey] = _value
        _sorted = list(_tmp_dict.values())
        if len(_sorted) < len(c):
            _sorted.extend(c[len(_sorted) :])
        return _sorted


class TriplePeakMixin:

    """
    Mix-In class with common functionality for FitFuncs with a triple peak.
    """

    num_peaks = 3

    @classmethod
    def profile(cls, c: Tuple[float], x: ndarray) -> ndarray:
        """
        Get the triple peak profile values.

        Parameters
        ----------
        c : Tuple[float]
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
    def guess_fit_start_params(cls, x: ndarray, y: ndarray, **kwargs) -> List[float]:
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
            - center<i>_bounds : Union[None, Tuple[float, float]], optional
                The low and high bounds for the <i>'s peak's center position.
            - center<i>_start :  Union[None, Tuple[float, float]], optional
                The starting value for the peak<i> fit. If not given, this defaults to
                the maximum position in the bounds.
            - width<i>_start : Union[None, float], optional
                The starting sigma value for the peak <i>.

        Returns
        -------
        List[float]
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
        cls, c: Union[ndarray, List[float]]
    ) -> List[float]:
        """
        Sort the peaks by their center's position.

        Parameters
        ----------
        c : Union[ndarray, List[float]]
            The fitted parameters.

        Returns
        -------
        List[float]
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
