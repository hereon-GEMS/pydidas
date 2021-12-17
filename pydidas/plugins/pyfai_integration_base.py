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
Module with the pyFAIintegrationBase Plugin which is inherited by all
integration plugins using pyFAI.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.0.1"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['pyFAIintegrationBase', 'pyFAI_UNITS', 'pyFAI_METHOD']

import os
import pathlib

import numpy as np
import pyFAI
import pyFAI.azimuthalIntegrator

from ..core.constants import PROC_PLUGIN
from ..core import get_generic_param_collection
from ..core.utils import pydidas_logger, LOGGING_LEVEL
from ..image_io import read_image, rebin2d
from ..experiment import ExperimentalSetup
from .base_proc_plugin import ProcPlugin


logger = pydidas_logger()
logger.setLevel(LOGGING_LEVEL)

EXP_SETTINGS = ExperimentalSetup()

pyFAI_UNITS = {'Q / nm^-1': 'q_nm^-1',
               'Q / A^-1': 'q_A^-1',
               '2theta / deg': '2th_deg',
               '2theta / rad': '2th_rad',
               'r / mm': 'r_mm',
               'chi / deg': 'chi_deg',
               'chi / rad': 'chi_rad'}

pyFAI_METHOD = {'CSR': 'csr',
                'CSR OpenCL': 'csr ocl',
                'LUT': 'lut',
                'LUT OpenCL': 'lut ocl'}


class pyFAIintegrationBase(ProcPlugin):
    """
    Provide basic functionality for the concrete integration plugins.
    """
    plugin_name = 'PyFAI integration base'
    basic_plugin = True
    plugin_type = PROC_PLUGIN
    default_params = get_generic_param_collection(
        'int_rad_npoint', 'int_rad_unit', 'int_rad_use_range',
        'int_rad_range_lower', 'int_rad_range_upper', 'int_azi_npoint',
        'int_azi_unit', 'int_azi_use_range', 'int_azi_range_lower',
        'int_azi_range_upper', 'int_method', 'det_mask')
    input_data_dim = 2
    output_data_dim = 2
    new_dataset = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._ai = None
        self._mask = None
        self.params['det_mask']._Parameter__meta['optional'] = True

    def pre_execute(self):
        """
        Check the use_global_mask Parameter and load the mask image.
        """
        if self._ai is None:
            _lambda_in_A = EXP_SETTINGS.get_param_value('xray_wavelength')
            self._ai = pyFAI.azimuthalIntegrator.AzimuthalIntegrator(
                dist=EXP_SETTINGS.get_param_value('detector_dist'),
                poni1=EXP_SETTINGS.get_param_value('detector_poni1'),
                poni2=EXP_SETTINGS.get_param_value('detector_poni2'),
                rot1=EXP_SETTINGS.get_param_value('detector_rot1'),
                rot2=EXP_SETTINGS.get_param_value('detector_rot2'),
                rot3=EXP_SETTINGS.get_param_value('detector_rot3'),
                detector=EXP_SETTINGS.get_detector(),
                wavelength=1e-10 * _lambda_in_A)
        self.load_and_store_mask()

    def load_and_store_mask(self):
        """
        Load and store the mask.

        If defined (and the file exists), the locally defined detector mask
        Parameter will be used. If not, the global QSetting detector mask
        will be used.
        """
        _mask_param = self.get_param_value('det_mask')
        _mask_qsetting = self.q_settings_get_global_value('det_mask')
        if _mask_param != pathlib.Path():
            if os.path.isfile(_mask_param):
                self._mask = read_image(_mask_param)
                return
            logger.warning(
                ('The locally defined detector mask file "%s" does not exist.'
                 ' Falling back  to the default defined in the global '
                 'settings.'), _mask_param)
        if os.path.isfile(_mask_qsetting):
            self._mask = read_image(_mask_qsetting)
            _roi, _bin = self.get_single_ops_from_legacy()
            self._mask = np.where(rebin2d(self._mask[_roi], _bin) > 0, 1, 0)
        else:
            self._mask = None

    def calculate_result_shape(self):
        """
        Get the shape of the integrated dataset to set up the CRS / LUT.

        Returns
        -------
        Union[int, tuple]
            The new shape. For 1-dimensional integration, a single integer is
            returned. For 2-dimensional integrations a tuple of two integers
            is returned.
        """
        raise NotImplementedError('Must be implemented by the concrete '
                                  'pyFAI integration plugin')
        # if self.output_data_dim == 2:
        #     self._config['result_shape'] = (
        #         self.get_param_value('int_rad_npoint'),
        #         self.get_param_value('int_azi_npoint'))
        # elif (self.get_param_value('int_rad_npoint', 1) == 1 and
        #         self.get_param_value('int_azi_npoint', 1) > 1):
        #     self._config['result_shape'] = (
        #         self.get_param_value('int_azi_npoint'), )
        # elif (self.get_param_value('int_rad_npoint', 1) > 1 and
        #         self.get_param_value('int_azi_npoint', 1) == 1):
        #     self._config['result_shape'] = (
        #         self.get_param_value('int_rad_npoint'), )
        # else:
        #     print('Shapes (rad/azi): ', self.get_param_value('int_rad_npoint'),
        #           self.get_param_value('int_rad_npoint'))
        #     raise ValueError('Could not determine the new shape from the '
        #                      'defined number of points')

    def get_radial_range(self):
        """
        Get the radial range from the Parameters.

        If use_radial_range is True and both the lower and upper range limits
        are larger than zero, the  tuple with both values is returned.
        Otherwise, the return is None  which corresponds to pyFAI auto ranges.

        Returns
        -------
        Union[None, tuple]
            The radial range for the pyFAI integration.
        """
        if self.get_param_value('int_rad_use_range'):
            _lower = self.get_param_value('int_rad_range_lower')
            _upper = self.get_param_value('int_rad_range_upper')
            if 0 <= _lower < _upper:
                return (_lower, _upper)
            logger.warning('Warning: Radial range was not correct and'
                           ' has been ignored.')
        return None

    def get_azimuthal_range_in_rad(self):
        """
        Get the azimuthal range from the Parameters in radians.

        If use_azimuthal_range is True and both the lower and upper range
        limits are larger than zero, the  tuple with both values is returned.
        Otherwise, the return is None  which corresponds to pyFAI auto ranges.

        Returns
        -------
        Union[None, tuple]
            The azimuthal range for the pyFAI integration.
        """
        _range = self.get_azimuthal_range_native()
        if _range is not None:
            if 'deg' in self.get_param_value('int_azi_unit'):
                _range = (np.pi / 180 * _range[0], np.pi / 180 * _range[1])
        return _range

    def get_azimuthal_range_in_deg(self):
        """
        Get the azimuthal range from the Parameters in degree.

        If use_azimuthal_range is True and both the lower and upper range
        limits are larger than zero, the  tuple with both values is returned.
        Otherwise, the return is None  which corresponds to pyFAI auto ranges.

        Returns
        -------
        Union[None, tuple]
            The azimuthal range for the pyFAI integration.
        """
        _range = self.get_azimuthal_range_native()
        if _range is not None:
            if 'rad' in self.get_param_value('int_azi_unit'):
                _range = (180 / np.pi * _range[0], 180 / np.pi * _range[1])
        return _range

    def get_azimuthal_range_native(self):
        """
        Get the azimuthal range from the Parameters in native units.

        If use_azimuthal_range is True and both the lower and upper range
        limits are larger than zero, the  tuple with both values is returned.
        Otherwise, the return is None  which corresponds to pyFAI auto ranges.

        Returns
        -------
        Union[None, tuple]
            The azimuthal range for the pyFAI integration.
        """
        if self.get_param_value('int_azi_use_range'):
            _lower = self.get_param_value('int_azi_range_lower')
            _upper = self.get_param_value('int_azi_range_upper')
            if 0 <= _lower < _upper:
                return (_lower, _upper)
            logger.warning('Warning: Azimuthal range was not correct and'
                           ' has been ignored.')
        return None

    def get_pyFAI_unit_from_param(self, param_name):
        """
        Get the unit of the Parameter called param_name in pyFAI notation.

        Parameters
        ----------
        param_name : str
            The reference key of the Parameter with the unit.

        Returns
        -------
        str
            The unit in pyFAI notation.
        """
        return pyFAI_UNITS[self.get_param_value(param_name)]


    def execute(self, data, **kwargs):
        """
        To be implemented by the concrete subclass.
        """
