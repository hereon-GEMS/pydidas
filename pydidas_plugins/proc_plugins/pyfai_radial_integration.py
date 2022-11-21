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
Module with the PyFAIradialIntegration Plugin which allows radial integration
to acquire azimuthal profiles.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ["PyFAIradialIntegration"]

from pydidas.plugins import pyFAIintegrationBase
from pydidas.core import Dataset


class PyFAIradialIntegration(pyFAIintegrationBase):
    """
    Integrate in image radially to get an azimuthal profile using pyFAI.

    For a full documentation of the Plugin, please refer to the pyFAI
    documentation.
    """

    plugin_name = "pyFAI radial integration"
    basic_plugin = False
    output_data_dim = 1

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._mask = None
        self._maskval = None
        self.set_param_value("rad_npoint", 1000)

    def pre_execute(self):
        """
        Pre-execute the plugin and store the Parameters required for the execution.
        """
        pyFAIintegrationBase.pre_execute(self)
        self._ai_params["npt_azim"] = self.get_param_value("azi_npoint")
        self._ai_params["npt_rad"] = self.get_param_value("rad_npoint")
        self._ai_params["unit"] = self.get_pyFAI_unit_from_param("azi_unit")
        self._ai_params["radial_unit"] = self.get_pyFAI_unit_from_param("rad_unit")
        self._ai_params["radial_range"] = self.get_radial_range()
        self._ai_params["azimuth_range"] = self.get_azimuthal_range_in_deg()
        _label, _unit = self.params["azi_unit"].value.split("/")
        self._dataset_info = {
            "axis_labels": [_label.strip()],
            "axis_units": [_unit.strip()],
            "data_label": "integrated intensity",
            "data_unit": "counts",
        }

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
        _newdata = self._ai.integrate_radial(
            data,
            self._ai_params["npt_azim"],
            npt_rad=self._ai_params["npt_rad"],
            polarization_factor=1,
            unit=self._ai_params["unit"],
            radial_unit=self._ai_params["radial_unit"],
            radial_range=self._ai_params["radial_range"],
            azimuth_range=self._ai_params["azimuth_range"],
            method=self._config["method"],
        )
        _dataset = Dataset(_newdata[1], axis_ranges=[_newdata[0]], **self._dataset_info)
        return _dataset, kwargs

    def calculate_result_shape(self):
        """
        Get the shape of the integrated dataset to set up the CRS / LUT.

        Returns
        -------
        tuple
            The new shape. This is a tuple with a single integer value.
        """
        self._config["result_shape"] = (self.get_param_value("azi_npoint"),)
