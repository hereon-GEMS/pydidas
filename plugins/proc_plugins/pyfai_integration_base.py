# This file is part of pydidas.

# pydidas is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# Pydidas is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with Pydidas. If not, see <http://www.gnu.org/licenses/>.

"""
Module with the PyFAIintegration Plugin which is used to call

"""

__author__      = "Malte Storm"
__copyright__   = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.0.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['PyFAIintegrationBase']


import numpy as np

import pyFAI

from pydidas.core import ParameterCollection, get_generic_parameter
from pydidas.plugins import ProcPlugin, PROC_PLUGIN
from pydidas.core.experimental_settings import ExperimentalSettings

EXP_SETTINGS = ExperimentalSettings()

class PyFAIintegrationBase(ProcPlugin):
    """
    Apply a mask to image files.
    """
    plugin_name = 'PyFAI integration base'
    basic_plugin = True
    plugin_type = PROC_PLUGIN
    default_params = ParameterCollection(
        get_generic_parameter('int_rad_npoint'),
        get_generic_parameter('int_rad_unit'),
        get_generic_parameter('int_rad_use_range'),
        get_generic_parameter('int_rad_range_lower'),
        get_generic_parameter('int_rad_range_upper'),
        get_generic_parameter('int_azi_npoint'),
        get_generic_parameter('int_azi_unit'),
        get_generic_parameter('int_azi_use_range'),
        get_generic_parameter('int_azi_range_lower'),
        get_generic_parameter('int_azi_range_upper'),
        get_generic_parameter('int_method'),
        )
    input_data_dim = 2
    output_data_dim = 2

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._AI = None

    def pre_execute(self):
        """
        Check the use_global_mask Parameter and load the mask image.
        """
        self._AI = pyFAI.azimuthalIntegrator.AzimuthalIntegrator(
            dist=EXP_SETTINGS.get_param_value('detector_dist'),
            poni1=EXP_SETTINGS.get_param_value('detector_poni1'),
            poni2=EXP_SETTINGS.get_param_value('detector_poni2'),
            rot1=EXP_SETTINGS.get_param_value('detector_rot1'),
            rot2=EXP_SETTINGS.get_param_value('detector_rot2'),
            rot3=EXP_SETTINGS.get_param_value('detector_rot3'),
            detector=self.__get_detector(),
            wavelength=EXP_SETTINGS.get_param_value('wavelength'))

    def __get_detector(self):
        """
        Get the detector. First, it is checked whether a pyFAI detector can
        be instantiated from the Detector name or a new detector is created
        and values from the ExperimentalSettings are copied.

        Returns
        -------
        _det : pyFAI.detectors.Detector
            The detector object.
        """
        _name = EXP_SETTINGS.get_param_value('detector_name')
        try:
            _det = pyFAI.detector_factory(_name)
        except RuntimeError:
            _det = pyFAI.detectors.Detector()
        for key, value in [
                ['pixel1', EXP_SETTINGS.get_param_value('detector_sizey')],
                ['pixel2', EXP_SETTINGS.get_param_value('detector_sizex')],
                ['max_shape', (EXP_SETTINGS.get_param_value('detector_npixy'),
                               EXP_SETTINGS.get_param_value('detector_npixx'))]
                ]:
            if getattr(_det, key) != value:
                setattr(_det, key, value)
        return _det


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
        _maskeddata = np.where(self._mask, self._maskval, data)
        return _maskeddata, kwargs
