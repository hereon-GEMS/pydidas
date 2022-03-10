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
Module with the SubtractBackgroundImage Plugin which can be used to subtract
another image as background.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.1.1"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['SubtractBackgroundImage']


import numpy as np

from pydidas.core.constants import PROC_PLUGIN
from pydidas.core import get_generic_param_collection
from pydidas.plugins import ProcPlugin
from pydidas.image_io import rebin2d


class SubtractBackgroundImage(ProcPlugin):
    """
    Subtract a background image from the data.
    """
    plugin_name = 'Subtract background image'
    basic_plugin = False
    plugin_type = PROC_PLUGIN
    default_params = get_generic_param_collection(
        'bg_file', 'bg_hdf5_key', 'bg_hdf5_frame', 'threshold_low')
    input_data_dim = 2
    output_data_dim = 2

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._bg_image = None
        self._thresh = None

    def pre_execute(self):
        """
        Load the background image.
        """
        self._bg_image = self.load_image_from_file(
            self.get_param_value('bg_file'),
            hdf5_dset=self.get_param_value('bg_hdf5_key'),
            hdf5_frame=self.get_param_value('bg_hdf5_frame'))
        self._thresh = self.get_param_value('threshold_low')
        if self._thresh is not None and not np.isfinite(self._thresh):
            self._thresh = None

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
        if data.shape != self._bg_image.shape:
            _roi, _binning = self.get_single_ops_from_legacy()
            self._bg_image  = rebin2d(self._bg_image[_roi], _binning)
        _corrected_data = data - self._bg_image
        if self._thresh is not None:
            _corrected_data[_corrected_data < self._thresh] = self._thresh
        return _corrected_data, kwargs
