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
Module with the Subtract1dBackgroundProfile Plugin which can be used to
subtract a given background profile from a 1-d dataset, e.g. integrated
diffraction data.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['Subtract1dBackgroundProfile']

from pathlib import Path

import numpy as np

from pydidas.core.constants import PROC_PLUGIN
from pydidas.core import ParameterCollection, Parameter
from pydidas.data_io import import_data
from pydidas.plugins import ProcPlugin


class Subtract1dBackgroundProfile(ProcPlugin):
    """
    Subtract a given background profile from 1-d data.

    This plugin simple substracts the given profile from all datasets. A
    lower threshold can be given, for example to prevent negative values.
    """
    plugin_name = 'Subtract 1D background profile'
    basic_plugin = False
    plugin_type = PROC_PLUGIN
    default_params = ParameterCollection(
        Parameter('kernel_width', int, 5, name='Averaging width',
                  tooltip=('The width of the averaging kernel (which is only '
                           'applied to the data for fitting).')),
        Parameter('threshold_low', float, None, allow_None=True,
                  name='Lower threshold',
                  tooltip=('The lower threhold. Any values in the corrected'
                           ' dataset smaller than the threshold will be set '
                           'to the threshold value.')),
        Parameter('profile_file', Path, Path(),
                  name='Filename of profile file',
                  tooltip=('The filename of the file with the background '
                           'profile.')))
    input_data_dim = 1
    output_data_dim = 1

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._thresh = None

    def pre_execute(self):
        """
        Set-up the fit and store required values.
        """
        self._thresh = self.get_param_value('threshold_low')
        if self._thresh is not None and not np.isfinite(self._thresh):
            self._thresh = None

        _fname = self.get_param_value('profile_name')
        _profile = import_data(_fname)

        _kernel = self.get_param_value('kernel_width')
        if _kernel > 0:
            _kernel = np.ones(_kernel) / _kernel
            _klim_low = _kernel // 2
            _klim_high = _kernel - 1 - _kernel // 2

        _profile[_klim_low:-_klim_high] = np.convolve(
            _profile, _kernel, mode='valid')
        self._profile = _profile

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
        data = data - self._profile

        if self._thresh is not None:
            _indices = np.where(data < self._thresh)[0]
            data[_indices] = self._thresh

        return data, kwargs
