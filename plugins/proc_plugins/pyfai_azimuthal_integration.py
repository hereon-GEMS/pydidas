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
__all__ = ['pyFAIazimuthalIntegration']


import numpy as np

import pyFAI

from pydidas.core import ParameterCollection, get_generic_parameter
from pydidas.plugins import (ProcPlugin, PROC_PLUGIN, pyFAIintegrationBase,
                             pyFAI_UNITS)
from pydidas.core.experimental_settings import ExperimentalSettings

EXP_SETTINGS = ExperimentalSettings()

class pyFAIazimuthalIntegration(pyFAIintegrationBase):
    """
    Apply a mask to image files.
    """
    plugin_name = 'pyFAI azimuthal integration'
    basic_plugin = False
    output_data_dim = 1

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.params['int_rad_unit'].choices = ['Q / nm^-1', '2\u03b8 / deg',
                                               'r / mm']
        self.set_param_value('int_rad_npoint', 1)

    def pre_execute(self):
        super().pre_execute()
        if 'CSR' in self.get_param_value('int_method'):
            self._ai.setup_CSR()

    def execute(self, data, **kwargs):
        """
        To be implemented by the concrete subclass.
        """
        _unit = pyFAI_UNITS[self.get_param_value('int_rad_unit')]
        _newdata = self._ai.integrate1d(
            data, self.get_param_value('int_azi_npoint'), unit=_unit,
            radial_range=self.get_radial_range(),
            azimuth_range=self.get_azimuthal_range())
        return _newdata, kwargs
