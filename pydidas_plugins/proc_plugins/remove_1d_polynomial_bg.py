# This file is part of pydidas.
#
# pydidas is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Pydidas is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Pydidas. If not, see <http://www.gnu.org/licenses/>.

"""
Module with the Remove1dPolynomialBackground Plugin which can be used to
subtract a polynomial background from a 1-d dataset, e.g. integrated
diffraction data.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['Remove1dPolynomialBackground']

import numpy as np
from numpy.polynomial import Polynomial

from pydidas.core.constants import PROC_PLUGIN
from pydidas.core import ParameterCollection, Parameter
from pydidas.plugins import ProcPlugin


class Remove1dPolynomialBackground(ProcPlugin):
    """
    Subtract a polynomial background from a 1-dimensional profile.

    This plugin uses a multi-tiered approach to remove the background. The
    background is calculated using the following approach:
    First, the data is smoothed by an averaging filter to remove noise.
    Second, local minima in the smoothed dataset are extracted and a polynomial
    background is fitted to these local minima. All local minima which are
    higher by more than 20% with respect to a linear fit between their
    neighboring local minima are discarded.
    Third, the residual between the background and the smoothed data is
    calculated and the x-positions of all local minima of the residual are
    used in conjunction with their data values to fit a final background.
    """
    plugin_name = 'Remove 1D polynomial background'
    basic_plugin = False
    plugin_type = PROC_PLUGIN
    default_params = ParameterCollection(
        Parameter('threshold_low', float, None, allow_None=True,
                  name='Lower threshold',
                  tooltip=('The lower threhold. Any values in the corrected'
                           ' dataset smaller than the threshold will be set '
                           'to the threshold value.')),
        Parameter('fit_order', int, 3, name='Polynomial fit order',
                  tooltip=('The polynomial order for the fit. This value '
                           'should typically not exceed3 or 4.')),
        Parameter('include_limits', int, 0, choices=[True, False],
                  name='Always include endpoints',
                  tooltip=('Flag to force the inclusion of both endpoints '
                           'in the initial points for the fit.')),
        Parameter('kernel_width', int, 5, name='Averaging width',
                  tooltip=('The width of the averaging kernel (which is only '
                           'applied to the data for fitting).')))
    input_data_dim = 1
    output_data_dim = 1

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._thresh = None
        self._fit_order = 3
        self._include_limits = False
        self._kernel = np.ones(5) / 5
        self._klim_low = 2
        self._klim_high = -2
        self._local_minina_threshold = 1.2

    def pre_execute(self):
        """
        Set-up the fit and store required values.
        """
        self._thresh = self.get_param_value('threshold_low')
        if self._thresh is not None and not np.isfinite(self._thresh):
            self._thresh = None
        self._fit_order = self.get_param_value('fit_order')
        self._include_limits = self.get_param_value('include_limits')

        _kernel = self.get_param_value('kernel_width')
        if _kernel > 0:
            self._kernel = np.ones(_kernel) / _kernel
            self._klim_low = _kernel // 2
            self._klim_high = _kernel - 1 - _kernel // 2
        else:
            self._kernel = None

    def execute(self, data, **kwargs):
        """
        Apply a mask to an image (2d data-array).

        Parameters
        ----------
        data : Union[pydidas.core.Dataset, np.ndarray]
            The image / frame data .
        **kwargs : dict
            Any calling keyword arguments.

        Returns
        -------
        _data : pydidas.core.Dataset
            The image data.
        kwargs : dict
            Any calling kwargs, appended by any changes in the function.
        """
        if self._kernel is not None:
            data[self._klim_low:-self._klim_high] = np.convolve(
                data, self._kernel, mode='valid')

        _x = np.arange(data.size)

        # find and fit the local minima
        local_min = np.where((data[1:-1] < np.roll(data, 1)[1:-1])
                             & (data[1:-1] < np.roll(data, -1)[1:-1]))[0] + 1
        local_min = self.__filter_local_minima_by_offset(local_min, data, 1.2)

        if self._include_limits:
            local_min = np.insert(local_min, 0, 0)
            local_min = np.insert(local_min, data.size, data.size -1)

        _p_prelim = Polynomial.fit(local_min, data[local_min], self._fit_order)

        # calculate the residual and fit residual's local minima
        _res = (data - _p_prelim(_x)) / data
        _local_res_min = (np.where((_res[1:-1] < np.roll(_res, 1)[1:-1])
                                   & (_res[1:-1] < np.roll(_res, -1)[1:-1]))[0]
                          + 1)
        _tmpindices = np.where(_res[_local_res_min] <= 0.002)[0]
        _local_res_min = _local_res_min[_tmpindices]

        _p_final = Polynomial.fit(_local_res_min, data[_local_res_min], 3)

        data = data - _p_final(_x)
        if self._thresh is not None:
            data = np.where(data < self._thresh, self._thresh, data)

        return data, kwargs

    @staticmethod
    def __filter_local_minima_by_offset(xpos, data, offset):
        """
        Filter local minima from a list of positions by evaluating their offset
        from the linear connection between neighbouring local minima.

        Parameters
        ----------
        xpos : np.ndarray
            The x positions of the datapoints
        data : np.ndarray
            The data values for the points.
        offset : float
            The threshold value offset at which to discard local minima.

        Returns
        -------
        xpos : np.ndarray
            The updated and filtered x positions.
        """
        _index = 1
        while _index < xpos.size - 1:
            _dx = xpos[_index + 1] - xpos[_index - 1]
            _dy = data[xpos[_index + 1]] - data[xpos[_index - 1]]
            _ypos = ((xpos[_index] - xpos[_index - 1]) / _dx
                     * _dy + data[xpos[_index - 1]])
            if data[xpos[_index]] >= offset * _ypos:
                xpos = np.delete(xpos, _index, 0)
            else:
                _index += 1
        return xpos
