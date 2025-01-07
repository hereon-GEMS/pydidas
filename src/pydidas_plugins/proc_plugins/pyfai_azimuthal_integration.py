# This file is part of pydidas.
#
# Copyright 2023 - 2025, Helmholtz-Zentrum Hereon
# SPDX-License-Identifier: GPL-3.0-only
#
# pydidas is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 3 as
# published by the Free Software Foundation.
#
# Pydidas is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Pydidas. If not, see <http://www.gnu.org/licenses/>.

"""
Module with the pyFAIazimuthalIntegration Plugin which allows azimuthal
integration of diffraction pattern to acquire a radial profile.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["PyFAIazimuthalIntegration"]


from pydidas.core import Dataset
from pydidas.plugins import pyFAIintegrationBase


class PyFAIazimuthalIntegration(pyFAIintegrationBase):
    """
    Integrate a diffraction pattern azimuthally to acquire a radial pattern.

    For a full documentation of the Plugin, please refer to the pyFAI
    documentation.
    """

    plugin_name = "pyFAI azimuthal integration"
    output_data_dim = 1

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        del self.params["azi_npoint"]

    def pre_execute(self):
        """
        Pre-execute the plugin and store the Parameters required for the execution.
        """
        pyFAIintegrationBase.pre_execute(self)
        self._ai_params = {
            "unit": self.get_pyFAI_unit_from_param("rad_unit"),
            "radial_range": self.get_radial_range(),
            "azimuth_range": self.get_azimuthal_range_in_deg(),
            "polarization_factor": self.get_param_value("polarization_factor"),
            "correctSolidAngle": self.get_param_value("correct_solid_angle"),
            "method": self._config["method"],
        }
        _label, _unit = self.params["rad_unit"].value.split("/")
        self._dataset_info = {
            "axis_labels": [_label.strip()],
            "axis_units": [_unit.strip()],
            "data_label": "integrated intensity",
            "data_unit": "counts",
        }

    def execute(self, data: Dataset, **kwargs: dict) -> tuple[Dataset, dict]:
        """
        Run the azimuthal integration on the input data.

        Parameters
        ----------
        data : pydidas.core.Dataset
            The radial integration results.
        kwargs : dict
            Any keyword arguments from the ProcessingTree.

        Returns
        -------
        _dataset : pydidas.core.Dataset
            The integrated data.
        kwargs : dict
            Any keyword arguments from the ProcessingTree, appended by any
            changes in the function.
        """
        self.check_and_set_custom_mask(**kwargs)
        _newdata = self._ai.integrate1d(
            data, self.get_param_value("rad_npoint"), **self._ai_params
        )
        _dataset = Dataset(_newdata[1], axis_ranges=[_newdata[0]], **self._dataset_info)
        return _dataset, kwargs
