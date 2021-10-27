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
Module with the pyFAIazimuthalIntegration Plugin which allows azimuthal
integration of diffraction pattern to acquire a radial profile.
"""

__author__      = "Malte Storm"
__copyright__   = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.0.1"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['PyFAIazimuthalIntegration']

from pydidas.plugins import pyFAIintegrationBase
from pydidas.core import Dataset


class PyFAIazimuthalIntegration(pyFAIintegrationBase):
    """
    Integrate a diffraction pattern azimuthally to acquire a radial pattern.

    For a full documentation of the Plugin, please refer to the pyFAI
    documentation.
    """
    plugin_name = 'pyFAI azimuthal integration'
    basic_plugin = False
    input_data_dim = 2
    output_data_dim = 1

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.params['int_rad_unit'].choices = [
            'Q / nm^-1', '2theta / deg', 'r / mm']
        del self.params['int_azi_npoint']

    def execute(self, data, **kwargs):
        """
        Run the azimuthal integration on the input data.

        Parameters
        ----------
        data : np.ndarray
            The input image array.
        kwargs : dict
            Any keyword arguments from the ProcessingTree.
        """
        _newdata = self._ai.integrate1d(
            data, self.get_param_value('int_rad_npoint'),
            unit=self.get_pyFAI_unit_from_param('int_rad_unit'),
            radial_range=self.get_radial_range(),
            azimuth_range=self.get_azimuthal_range_in_deg(),
            mask=self._mask, polarization_factor=1)
        _label, _unit = self.params['int_rad_unit'].value.split('/')
        _label = _label.strip()
        _unit = _unit.strip()
        _dataset = Dataset(_newdata[1], axis_labels=[_label],
                           axis_units=[_unit], axis_scales=[_newdata[0]])
        return _dataset, kwargs
