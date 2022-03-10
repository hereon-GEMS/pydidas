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
Module with the MaskImage Plugin which can be used to apply a mask to images.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.1.1"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['MaskImage']


import numpy as np

from pydidas.core.constants import PROC_PLUGIN
from pydidas.core import ParameterCollection, get_generic_parameter
from pydidas.plugins import ProcPlugin
from pydidas.image_io import read_image, rebin2d


class MaskImage(ProcPlugin):
    """
    Apply a mask to image files.
    """
    plugin_name = 'Mask image'
    basic_plugin = False
    plugin_type = PROC_PLUGIN
    default_params = ParameterCollection(
        get_generic_parameter('use_global_mask'),
        get_generic_parameter('det_mask'),
        get_generic_parameter('det_mask_val'),
        )
    input_data_dim = 2
    output_data_dim = 2

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._mask = None
        self._maskval = None

    def pre_execute(self):
        """
        Check the use_global_mask Parameter and load the mask image.
        """
        if self.get_param_value('use_global_mask'):
            _maskfile = self.q_settings_get_global_value('det_mask')
            self._maskval = self.q_settings_get_global_value('det_mask_val')
        else:
            _maskfile = self.get_param_value('det_mask')
            self._maskval = self.get_param_value('det_mask_val')
        self._mask = read_image(_maskfile)

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
        if data.shape != self._mask.shape:
            _roi, _binning = self.get_single_ops_from_legacy()
            self._mask  = np.where(
                rebin2d(self._mask[_roi], _binning) > 0, 1, 0)
        _maskeddata = np.where(self._mask, self._maskval, data)
        return _maskeddata, kwargs
