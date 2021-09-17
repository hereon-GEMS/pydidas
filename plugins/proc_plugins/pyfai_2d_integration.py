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
Module with the PyFAI2dIntegration Plugin which allows to integrate diffraction
patterns into a 2D radial/azimuthal map.

"""

__author__      = "Malte Storm"
__copyright__   = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.0.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['PyFAI2dIntegration']


from pydidas.plugins import pyFAIintegrationBase


class PyFAI2dIntegration(pyFAIintegrationBase):
    """
    Integrate an image in 2D using pyFAI.

    For a full documentation of the Plugin, please refer to the pyFAI
    documentation.
    """
    plugin_name = 'PyFAI 2D integration'
    basic_plugin = False
    input_data_dim = 2
    output_data_dim = 2

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._mask = None
        self._maskval = None
        self.set_param_value('int_rad_npoint', 720)

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
        _newdata = self._ai.integrate_2d(
            data, self.get_param_value('int_rad_npoint'),
            npt_azim=self.get_param_value('int_azi_npoint'),
            polarization_factor=1,
            unit=self.get_pyFAI_unit_from_param('int_rad_unit'),
            radial_range=self.get_radial_range(),
            azimuth_range=self.get_azimuthal_range_in_deg())
        return _newdata, kwargs
