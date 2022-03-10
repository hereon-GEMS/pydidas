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
Module with the FitSinglePeak Plugin which can be used to fit a single peak
in 1d data.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.1.1"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['SubtractBackgroundImage']


import numpy as np
from scipy.optimize import least_squares

from pydidas.core.constants import (PROC_PLUGIN, GAUSSIAN, LORENTZIAN,
                                    PSEUDO_VOIGT)
from pydidas.core import get_generic_param_collection, Dataset, AppConfigError
from pydidas.plugins import ProcPlugin
from pydidas.image_io import rebin2d






class FitSinglePeak(ProcPlugin):
    """
    Subtract a background image from the data.
    """
    plugin_name = 'Fit single peak'
    basic_plugin = False
    plugin_type = PROC_PLUGIN
    default_params = get_generic_param_collection(
        'fit_func', 'fit_bg_order', 'fit_lower_limit', 'fit_upper_limit')
    input_data_dim = 1
    output_data_dim = 2
    new_dataset = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._ffunc = None
        self._fitparam_labels = []
        self._fitparam_startpoints = []
        self._fitparam_bounds = (tuple(), tuple())

    def pre_execute(self):
        """
        Set up the required functions and fit variable labels.
        """
        self._fitparam_labels = []
        self._fitparam_startpoints = []
        if self.get_param_value('fit_func') == 'Gaussian':
            self._ffunc = GAUSSIAN
        elif self.get_param_value('fit_func') == 'Lorentzian':
            self._ffunc = LORENTZIAN
        elif self.get_param_value('fit_func') == 'Pseudo-Voigt':
            self._ffunc = PSEUDO_VOIGT
            self._fitparam_labels = ['fraction']
            self._fitparam_startpoints = [0.5]
            self._fitparam_bounds = ((0, ), (1, ))

    def execute(self, data, **kwargs):
        """
        Fit a peak to the data.

        Note that a

        Parameters
        ----------
        data : pydidas.core.Dataset
            The input Dataset
        **kwargs : dict
            Any calling keyword arguments.

        Returns
        -------
        _data : pydidas.core.Dataset
            The image data.
        kwargs : dict
            Any calling kwargs, appended by any changes in the function.
        """
        _xnew, _data = self._get_data_range(data)
        self._update_fit_startparams(_xnew, _data)
        _bg_order = self.get_param_value('fit_bg_order')
        _res = least_squares(self._ffunc, self._fitparam_startpoints,
                             args=(_xnew, _data.array, _bg_order),
                             bounds=self._fitparam_bounds)
        _new_params = _res.x
        _new_data = self._create_new_dataset(_xnew, _data, _new_params)
        kwargs['fit_params'] = _new_params
        kwargs['fit_func'] = self._ffunc.__name__
        kwargs['fit_param_labels'] = self._fitparam_labels
        return _new_data, kwargs

    def _get_data_range(self, data):
        """
        Get the data in the range specified by the

        Parameters
        ----------
        data : pydidas.core.Dataset
            The input data

        Returns
        -------
        xnew : np.ndarray
            The xaxis values of the selected data slice.
        data_new : np.ndarray
            The selected data slice.
        """
        _xlow = self.get_param_value('fit_lower_limit')
        _xhigh = self.get_param_value('fit_upper_limit')
        _range = np.where((data.axis_ranges[0] >= _xlow)
                          & (data.axis_ranges[0] <= _xhigh))[0]
        if _range.size < 5:
            raise AppConfigError('The data range for the fit is too small '
                                 'with less than 5 data points.')
        _xnew = data.axis_ranges[0][_range]
        _data_new = data[_range]
        return _xnew, _data_new

    def _update_fit_startparams(self, x, data):
        """
        Update the fit starting Parameters based on the x-range and the data.

        Parameters
        ----------
        x : np.ndarray
            The x-axis data points.
        data : np.ndarray
            The data values.
        """
        _amp = np.amax(data) - np.amin(data)
        _center = x[np.argmax(data)]
        # guess that the interval is twice the FWHM
        _sigma = (x[-1] - x[0]) / 2 / 2.35
        self._fitparam_startpoints.extend([_amp, _sigma, _center])
        self._fitparam_labels.extend(['amplitude', 'sigma', 'center'])
        _bounds = (self._fitparam_bounds[0] + (0, 0, -np.inf),
                   self._fitparam_bounds[1] + (np.inf, np.inf, np.inf))
        _bg_order = self.get_param_value('fit_bg_order')
        if _bg_order is not None:
            self._fitparam_startpoints.append(np.amin(data))
            self._fitparam_labels.append('background p0')
            _bounds = (_bounds[0] + (0,), _bounds[1] + (np.inf,))
        if _bg_order == 1:
            self._fitparam_startpoints.append(0)
            self._fitparam_labels.append('background p1')
            _bounds = (_bounds[0] + (-np.inf,), _bounds[1] + (np.inf,))
        self._fitparam_bounds = _bounds

    def _create_new_dataset(self, x, data, datafit_params):
        """
        Create a new Dataset from the original data and the data fit including
        all the old metadata.

        Note that this method does not upate the new metadata with the fit
        parameters. The new dataset includes a second dimensions with entries
        for the raw data, the data fit and the residual.

        Parameters
        ----------
        x : np.ndarray
            The x-axis data points.
        data : np.ndarray
            The data values.
        datafit_params : np.ndarray
            The parameters

        Returns
        -------
        new_data : pydidas.core.Dataset
            The new dataset.
        """
        _datafit = self._ffunc(datafit_params, x, 0 * x,
                               self.get_param_value('fit_bg_order'))
        _new_data = Dataset([data, _datafit, data - _datafit])
        _new_data.axis_labels[1] = data.axis_labels[0]
        _new_data.axis_units[1] = data.axis_units[0]
        _new_data.axis_ranges[1] = x
        _new_data.axis_labels[0] = 'Data and fit'
        _new_data.axis_ranges[0] = ['data', 'fit', 'residual']
        _new_data.metadata = data.metadata
        _new_data.metadata['fit_params'] = datafit_params
        _new_data.metadata['fit_func'] = self._ffunc.__name__
        _new_data.metadata['fit_param_labels'] = self._fitparam_labels
        return _new_data
