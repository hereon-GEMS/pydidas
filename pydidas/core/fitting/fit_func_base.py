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
Module with the FitFuncBase class which all fitting functions should inherit from.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2024, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["FitFuncBase"]


from typing import Dict, List, Tuple, Union

import numpy as np
from numpy import amin, ndarray
from scipy import interpolate

from ..exceptions import UserConfigError
from .fit_func_meta import FitFuncMeta


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

    @staticmethod
    def func(c: Tuple[float], x: ndarray) -> ndarray:
        """
        Get the function values. The default is simply a 1:1 mapping.

        Parameters
        ----------
        c : Tuple[float]
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
    def profile(cls, c: Tuple[float], x: ndarray) -> ndarray:
        """
        Calculate the profile for the given peak fit function.

        Classes with functions which use more than 3 parameters need to set the class
        attribute 'num_peak_params' correspondingly.

        Parameters
        ----------
        c : Tuple[float]
            The tuple with the fit parameters.
            c[0] : amplitude
            c[1] : gamma/sigma
            c[2] : center
            c[3], optional: A background offset.
            c[4], optional: The polynomial coefficient for a first order background.
        x : np.ndarray
            The x data points

        Returns
        -------
        np.ndarray
            The function values for the given x values.
        """
        _profile = cls.func(c[0 : cls.num_peak_params], x)
        _background = cls.calculate_background(c[cls.num_peak_params :], x)
        return _profile + _background

    @classmethod
    def guess_fit_start_params(
        cls, x: ndarray, y: ndarray, **kwargs: Dict
    ) -> List[float]:
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
        List[float]
            The list with the starting fit parameters.
        """
        bg_order = kwargs.get("bg_order", None)
        y, _bg_params = cls.calculate_background_params(x, y, bg_order)
        _peak_params = cls.guess_peak_start_params(x, y, None, **kwargs)
        return _peak_params + _bg_params

    @classmethod
    def calculate_background_params(
        cls, x: ndarray, y: ndarray, bg_order: Union[None, int]
    ) -> Tuple[ndarray, Tuple[float, float]]:
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
        bg_params : list
            The parameters to describe the background.
        """
        if bg_order is None:
            return y, []
        if bg_order not in [0, 1]:
            raise ValueError("The selected background order is not supported")
        if bg_order == 0:
            _bg0 = amin(y)
            y = y - _bg0
            return y, [_bg0]
        _bg1 = (y[-1] - y[0]) / (x[-1] - x[0])
        _bg0 = y[0] - _bg1 * x[0]
        _new_y = y - (_bg1 * x + _bg0)
        return _new_y, [_bg0, _bg1]

    @classmethod
    def guess_peak_start_params(
        cls, x: ndarray, y: ndarray, index: Union[None, int], **kwargs
    ) -> List:
        """
        Guess the start params for the fit for the given x and y values.

        Parameters
        ----------
        x : nd.ndarray
            The x points of the data.
        y : np.ndarray
            The data values.
        index : Union[None, str]
            The peak index. Use None for a non-indexed single peak or the integer peak
            number (starting with 1).
        **kwargs : dict
            Optional keyword arguments.
        """
        return [0] * len(cls.param_labels)

    @staticmethod
    def get_y_value(xpos: float, x: ndarray, y: ndarray) -> float:
        """
        Get the y value for the given x position.

        Parameters
        ----------
        xpos : float
            The demanded position.
        x : ndarray
            The x position.
        y : ndarray
            The y function values.

        Returns
        -------
        float
            The y value at position xpos.
        """
        if not np.amin(x) <= xpos <= np.amax(x):
            raise UserConfigError(
                f"The specified peak x position {xpos} is outside of the given x data"
                f"range [{np.round(np.amin(x), 5)}, {np.round(np.amax(x), 5)}]!"
            )
        if xpos in x:
            _index = np.where(x == xpos)[0][0]
            _y0 = y[_index]
        else:
            _interp = interpolate.interp1d(x, y)
            _y0 = _interp(xpos)
        return _y0

    @staticmethod
    def get_fwhm_indices(x0: float, y0: float, x: ndarray, y: ndarray) -> ndarray:
        """
        Get the consecutive indices where the data is larger than half the peak height.

        Parameters
        ----------
        x0 : float
            The x0 center position.
        y0 : float
            The y value at x0.
        x : ndarray
            The full x-range.
        y : ndarray
            The data values for x.

        Returns
        -------
        ndarray
            The array with the index values where y is larger than 0.5 * y0
        """
        _high_x = np.where(y >= 0.5 * y0)[0]
        _delta = np.diff(_high_x)
        if set(_delta) in [set(), set([1])]:
            return _high_x
        _delta_jumps = np.where(_delta != 1)[0] + 1
        _range_indices = np.sort(
            np.concatenate(([0], _delta_jumps, _delta_jumps, [_high_x.size]))
        ).reshape(_delta_jumps.size + 1, 2)
        for _i_low, _i_high in _range_indices:
            _indices = _high_x[_i_low:_i_high]
            _x_low = x[_indices[0]]
            _x_high = x[_indices[-1]]
            if _x_low <= x0 <= _x_high:
                return _high_x[_i_low:_i_high]
        return np.zeros((0,))

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
        return list(c)

    @staticmethod
    def calculate_background(c: Union[Tuple, List], x: ndarray) -> ndarray:
        """
        Calculate the background defined by the input parameters c.

        Parameters
        ----------
        c : Union[Tuple, List]
            The parameters for the background.
        x : ndarray
            The x point values.

        Returns
        -------
        ndarray
            The background
        """
        if len(c) == 0:
            return 0 * x
        if len(c) == 1:
            return 0 * x + c[0]
        if len(c) == 2:
            return c[0] + x * c[1]
        raise ValueError("The order of the background is not supported.")

    @classmethod
    def delta(cls, c, x, data):
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

    @staticmethod
    def area(c: Tuple) -> float:
        """
        Get the peak area based on the values of the parameters.

        For all normalized fitting functions, the area is equal to the amplitude term.

        Parameters
        ----------
        c : tuple
            The tuple with the function parameters.

        Returns
        -------
        float
            The function area.
        """
        return c[0]

    @classmethod
    def fwhm(cls, c: Tuple[float]):
        """
        Get the FWHM of the fit from the values of the parameters.

        This method needs to be implemented by each fitting function.

        Parameters
        ----------
        c : Tuple[float]
            The tuple with the function parameters.

        Returns
        -------
        float
            The function FWHM.
        """
        raise NotImplementedError(
            "The FWHM method must be implemented by the specific FitFunc"
        )

    @classmethod
    def center(cls, c: Tuple[float]) -> float:
        """
        Get the center position of the fit.

        Parameters
        ----------
        c : Tuple[float]
            The tuple with the function parameters.

        Returns
        -------
        float
            The peak's center.
        """
        return c[cls.num_peak_params - 1]

    @classmethod
    def background_at_peak(cls, c: Tuple[float]) -> Union[float, ndarray]:
        """
        Get the background level at the peak position.

        Parameters
        ----------
        c : Tuple[float]
            The tuple with the function parameters.

        Returns
        -------
        Union[float, ndarray]
            The background at the peak center. For single peaks, the value is returned
            as float. For multiple peaks, it is returned as ndarray.
        """
        _n_peak_params = cls.num_peaks * cls.num_peak_params
        _i_center = cls.center_param_index
        _centers = np.asarray(
            c[_i_center : (_i_center + _n_peak_params) : cls.num_peak_params]
        )
        _bgs = cls.calculate_background(c[_n_peak_params:], _centers)
        if _bgs.size == 1:
            return _bgs[0]
        return _bgs
