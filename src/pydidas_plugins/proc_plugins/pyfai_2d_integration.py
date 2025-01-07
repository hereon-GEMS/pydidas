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
Module with the PyFAI2dIntegration Plugin which allows to integrate diffraction
patterns into a 2D radial/azimuthal map.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["PyFAI2dIntegration"]

from typing import Union

import numpy as np

from pydidas.core import Dataset
from pydidas.plugins import pyFAIintegrationBase


class PyFAI2dIntegration(pyFAIintegrationBase):
    """
    Integrate an image in 2D using pyFAI.

    The default setting for the azimuthal range in (-180, 180) degree. Using
    the azimuthal range setting, this can be changed to (0, 360) degree, if
    required.

    The output data dimensions are
        0: azimuthal angle (chi)
        1: radial 2theta angle / Q / r.

    For a full documentation of the Plugin, please refer to the pyFAI
    documentation.
    """

    plugin_name = "pyFAI 2D integration"

    output_data_dim = 2

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_param_value("rad_npoint", 1000)
        self.set_param_value("azi_npoint", 36)

    def pre_execute(self):
        """
        Pre-execute the plugin and store the Parameters required for the execution.
        """
        pyFAIintegrationBase.pre_execute(self)
        self._ai_params = {
            "npt_azim": self.get_param_value("azi_npoint"),
            "polarization_factor": self.get_param_value("polarization_factor"),
            "correctSolidAngle": self.get_param_value("correct_solid_angle"),
            "unit": self.get_pyFAI_unit_from_param("rad_unit"),
            "radial_range": self.get_radial_range(),
            "azimuth_range": self.get_azimuthal_range_in_deg(),
            "method": self._config["method"],
        }

        self.__range_factor = (
            np.pi / 180 if "rad" in self.get_param_value("azi_unit") else 1
        )
        _x_label, _x_unit = self.get_param_value("rad_unit").replace(" ", "").split("/")
        _y_label, _y_unit = self.get_param_value("azi_unit").replace(" ", "").split("/")
        self._dataset_info = {
            "axis_labels": [_y_label, _x_label],
            "axis_units": [_y_unit, _x_unit],
            "data_label": "integrated intensity",
            "data_unit": "counts",
        }

    def execute(
        self, data: Union[Dataset, np.ndarray], **kwargs: dict
    ) -> tuple[Dataset, dict]:
        """
        Perform a 2D integration of the input dataset.

        Parameters
        ----------
        data : Union[pydidas.core.Dataset, np.ndarray]
            The image / frame data .
        **kwargs : dict
            Any calling keyword arguments.

        Returns
        -------
        _dataset : pydidas.core.Dataset
            The integrated intensity data.
        kwargs : dict
            Any calling kwargs, appended by any changes in the function.
        """
        self.check_and_set_custom_mask(**kwargs)
        _newdata = self._ai.integrate2d(
            data, self.get_param_value("rad_npoint"), **self._ai_params
        )
        _dataset = Dataset(
            _newdata[0],
            axis_ranges=[_newdata[2] * self.__range_factor, _newdata[1]],
            **self._dataset_info,
        )
        return _dataset, kwargs
