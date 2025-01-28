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
Module with the FitFuncBase class which all fitting functions should inherit from.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2024 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["FitFuncBase"]

import copy
from numbers import Real
from typing import Dict, Optional, Union

import numpy as np
from numpy import amin, ndarray
from scipy import interpolate

from pydidas.core.exceptions import UserConfigError
from pydidas.core.fitting.fit_func_meta import FitFuncMeta
from pydidas.core.utils import flatten


class FitFuncBase(metaclass=FitFuncMeta):
    """
    Base class for fit functions.

    The class should normally be accessed through the FitFuncMeta registry.
    """

    name = "base fit function"
    param_bounds_low = []
    param_bounds_high = []
    param_labels = []
    num_peaks = 1
    num_peak_params = 3
    center_param_index = 2
    amplitude_param_index = 0

    @staticmethod
    def func(c: tuple[Real], x: ndarray) -> ndarray:
        """
        Get the function values. The default is simply a 1:1 mapping.

        Parameters
        ----------
        c : tuple[Real]
            The fit parameters.
        x : ndarray
            The input x data points.

        Returns
        -------
        ndarray
            The function values for the given data points.
        """
        return x

    @classmethod
    def profile(cls, c: tuple[Real], x: ndarray) -> ndarray:
        """
        Calculate the profile for the given peak fit function.

        Classes with functions which use more than 3 parameters need to set the class
        attribute 'num_peak_params' correspondingly.

        Parameters
        ----------
        c : tuple[Real]
            The tuple with the fit parameters. The specific parameters are
            defined by the respective fit function plus (optionally) one or
            two background parameters.
        x : np.ndarray
            The x data points

        Returns
        -------
        np.ndarray
            The function values for the given x values.
        """
        _peaks = sum(
            cls.func(
                c[_i_peak * cls.num_peak_params : (_i_peak + 1) * cls.num_peak_params],
                x,
            )
            for _i_peak in range(cls.num_peaks)
        )
        _background = cls.calculate_background(c, x)
        return _peaks + _background

    @classmethod
    def calculate_background(cls, c: tuple[Real], x: ndarray) -> ndarray:
        """
        Calculate the background defined by the input parameters c.

        Parameters
        ----------
        c : tuple[Real]
            The parameters for the background.
        x : ndarray
            The x point values.

        Returns
        -------
        ndarray
            The background
        """
        _c_bg = c[cls.num_peaks * cls.num_peak_params :]
        if len(_c_bg) == 0:
            return 0 * x
        if len(_c_bg) == 1:
            return 0 * x + _c_bg[0]
        if len(_c_bg) == 2:
            return _c_bg[0] + x * _c_bg[1]
        raise ValueError("The order of the background is not supported.")

    @classmethod
    def delta(cls, c: tuple[Real], x: ndarray, data: ndarray) -> ndarray:
        """
        Get the difference between the fit and the data.

        Parameters
        ----------
        c : tuple
            The tuple with the function parameters.
        x : np.ndarray
            The x points to calculate the function values.
        data : np.ndarray
            The data values.

        Returns
        -------
        np.ndarray
            The difference of function - data
        """
        return cls.profile(c, x) - data

    @classmethod
    def area(cls, c: tuple[Real]) -> tuple[Real]:
        """
        Get the peak area based on the values of the parameters.

        For all normalized fitting functions, the area is equal
        to the amplitude term. Other fitting functions need to
        redefine this method.

        Parameters
        ----------
        c : tuple
            The tuple with the function parameters.

        Returns
        -------
        tuple[Real]
            The area for each peak defined in the fitting function.
        """
        _indices = [
            cls.amplitude_param_index + i * cls.num_peak_params
            for i in range(0, cls.num_peaks)
        ]
        return tuple(c[_index] for _index in _indices)

    @classmethod
    def amplitude(cls, c: tuple[Real]) -> tuple[Real]:
        """
        Get the amplitude of the peak from the values of the parameters.

        Note that the peak amplitude is not the same as the fitted amplitude
        which is a scaling factor for the peak function.
        """
        raise NotImplementedError

    @classmethod
    def fwhm(cls, c: tuple[Real]) -> tuple[Real]:
        """
        Get the FWHM of the fit from the values of the parameters.

        This method needs to be implemented by each fitting function.

        Parameters
        ----------
        c : tuple[Real]
            The tuple with the function parameters.

        Returns
        -------
        tuple(Real)
            The function FWHM.
        """
        raise NotImplementedError(
            "The FWHM method must be implemented by the specific FitFunc"
        )

    @classmethod
    def center(cls, c: tuple[Real]) -> tuple[Real]:
        """
        Get the center position(s) of the fit.

        Parameters
        ----------
        c : tuple[Real]
            The tuple with the function parameters.

        Returns
        -------
        tuple[Real]
            The center positions for all peaks.
        """
        return tuple(c[_index] for _index in cls._center_param_indices())

    @classmethod
    def _center_param_indices(cls, num_peaks: Optional[int] = None) -> list[int]:
        """
        Get the indices for the center parameters.

        Parameters
        ----------
        num_peaks : Optional[int]
            The number of peaks. If None, the number of peaks is taken
            from the class attribute.
        """
        num_peaks = cls.num_peaks if num_peaks is None else num_peaks
        if num_peaks > cls.num_peaks:
            raise ValueError(
                f"The requested number of peaks `{num_peaks}` is larger than the"
                f"number of peaks defined by the function: `{cls.num_peaks}`."
            )
        return [
            cls.center_param_index + i * cls.num_peak_params
            for i in range(0, num_peaks)
        ]

    @classmethod
    def position(cls, c: tuple[Real]) -> tuple[Real]:
        """
        Get the peak position of the fit.

        The position is a wrapper for the center method.
        Please refer to the center method for more details.
        """
        return cls.center(c)

    @classmethod
    def background(cls, c: tuple[Real]) -> tuple[Real]:
        """
        Get the background level at the peak position.

        This is a wrapper for the background_at_peak method. Please refer to
        the background_at_peak method for more details.
        """
        return cls.background_at_peak(c)

    @classmethod
    def background_at_peak(cls, c: tuple[Real]) -> tuple[Real]:
        """
        Get the background level at the peak position.

        Parameters
        ----------
        c : tuple[Real]
            The tuple with the function parameters.

        Returns
        -------
        tuple[Real]
            The background at the peak center or centers.
        """
        _n_peak_params = cls.num_peaks * cls.num_peak_params
        _i_center = cls.center_param_index
        _centers = np.asarray(
            c[_i_center : (_i_center + _n_peak_params) : cls.num_peak_params]
        )
        _bgs = cls.calculate_background(c, _centers)
        return tuple(_bgs)

    @classmethod
    def guess_fit_start_params(
        cls, x: ndarray, y: ndarray, **kwargs: Dict
    ) -> tuple[Real]:
        """
        Guess the start params for the fit for the given x and y values.

        Parameters
        ----------
        x : nd.ndarray
            The x points of the data.
        y : np.ndarray
            The data values.
        **kwargs : Dict
            Additional kwargs for background order (bg_order) or starting values for
            the fit params.

        Returns
        -------
        list[Real]
            The list with the starting fit parameters.
        """

        def _calc_starting_params(local_kws: dict) -> tuple[Real]:
            """Calculate the starting parameters for all the given peaks."""
            _peak_params = []
            _y_temp = _y.copy()
            for _index in range(cls.num_peaks):
                _params = cls.guess_peak_start_params(x, _y_temp, _index, **local_kws)
                _peak_params.extend(_params)
                _y_temp = _y_temp - cls.func(_params, x)
            return cls.sort_fitted_peaks_by_position(
                tuple(_peak_params) + _bg_params, num_peaks=_index + 1
            )

        bg_order = kwargs.get("bg_order", None)
        _y, _bg_params = cls.estimate_background_params(x, y, bg_order)
        if cls.num_peaks == 1:
            _peak_params = (
                cls.guess_peak_start_params(x, _y, None, **kwargs) * cls.num_peaks
            )
            return _peak_params + _bg_params

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

    @classmethod
    def estimate_background_params(
        cls, x: ndarray, y: ndarray, bg_order: Union[None, int]
    ) -> tuple[ndarray, tuple[Real]]:
        """
        Calculate the parameters for the background and remove it from the values.

        Parameters
        ----------
        x : nd.ndarray
            The x points of the data.
        y : np.ndarray
            The data values.
        bg_order : Union[None, 0, 1]
            The order of the background.

        Returns
        -------
        y : np.ndarray
            The background-corrected values
        bg_params : tuple
            The parameters to describe the background.
        """
        if bg_order is None:
            return y, ()
        if bg_order not in [0, 1]:
            raise ValueError("The selected background order is not supported")
        if bg_order == 0:
            _bg0 = amin(y)
            y = y - _bg0
            return y, (_bg0,)
        _bg1 = (y[-1] - y[0]) / (x[-1] - x[0])
        _bg0 = y[0] - _bg1 * x[0]
        _new_y = y - (_bg1 * x + _bg0)
        return _new_y, (_bg0, _bg1)

    @classmethod
    def guess_peak_start_params(
        cls, x: ndarray, y: ndarray, index: Union[None, int], **kwargs
    ) -> tuple[Real]:
        """
        Guess the start params for the fit for the given x and y values.

        Parameters
        ----------
        x : nd.ndarray
            The x points of the data.
        y : np.ndarray
            The data values.
        index : Union[None, str]
            The peak index. Use None for a non-indexed single peak
            or the integer peak number.
        **kwargs : dict
            Optional keyword arguments.
        """
        return (0,) * cls.num_peak_params

    @staticmethod
    def get_y_value(xpos: Real, x: ndarray, y: ndarray) -> Real:
        """
        Get the y value for the given x position.

        Parameters
        ----------
        xpos : Real
            The demanded position.
        x : ndarray
            The x position.
        y : ndarray
            The y function values.

        Returns
        -------
        Real
            The y value at position xpos.
        """
        if not np.amin(x) <= xpos <= np.amax(x):
            raise UserConfigError(
                f"The specified peak x position {xpos} is outside of the given x data"
                f"range [{np.round(np.amin(x), 5)}, {np.round(np.amax(x), 5)}]!"
            )
        if xpos in x:
            _index = np.where(x == xpos)[0][0]
            return y[_index]
        _interp = interpolate.interp1d(x, y)
        return _interp(xpos)

    @staticmethod
    def get_fwhm_indices(x0: Real, y0: Real, x: ndarray, y: ndarray) -> ndarray:
        """
        Get the consecutive indices where the data is larger than half the peak height.

        Parameters
        ----------
        x0 : Real
            The x0 center position.
        y0 : Real
            The y value at x0.
        x : ndarray
            The full x-range.
        y : ndarray
            The data values for x.

        Returns
        -------
        ndarray
            The array with the indices where y is larger than 0.5 * y0
        """
        _high_x = np.where(y >= 0.5 * y0)[0]
        _delta = np.diff(_high_x)
        if np.all(_delta == 1):
            return _high_x
        _ranges = np.split(_high_x, np.where(_delta != 1)[0] + 1)
        for _range in _ranges:
            if x[_range[0]] <= x0 <= x[_range[-1]]:
                return _range
        return np.array([])

    @classmethod
    def sort_fitted_peaks_by_position(
        cls, c: tuple[Real], num_peaks: Optional[int] = None
    ) -> tuple[Real]:
        """
        Sort the peaks by their center's position.

        Parameters
        ----------
        c : tuple[Real]
            The fitted parameters.
        num_peaks : Optional[int]
            The number of peaks to sort. If None, the number of peaks
            is taken from the class attribute. The num_peaks parameter
            should only be used if the number of peaks is different from
            the generic number of peaks, i.e. if the function is used
            during initial peak pos guessing.

        Returns
        -------
        tuple[Real]
            The sorted fitted parameters.
        """
        num_peaks = cls.num_peaks if num_peaks is None else num_peaks
        if num_peaks == 1:
            return c
        _indices = np.argsort([c[i] for i in cls._center_param_indices(num_peaks)])
        _temp_c = flatten(
            [
                c[_index * cls.num_peak_params : (_index + 1) * cls.num_peak_params]
                for _index in _indices
            ],
            astype=tuple,
        )
        _temp_c += c[num_peaks * cls.num_peak_params :]
        return tuple(_temp_c)
