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
Module with the CenterOfMass1dData Plugin which can be used to sum over 1D data.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["CenterOfMass1dData"]


import numpy as np

from pydidas.core import Dataset, get_generic_param_collection
from pydidas.plugins import ProcPlugin


class CenterOfMass1dData(ProcPlugin):
    """
    Calculate the center of mass along the specified data dimension.

    The mathematical formulation is:

    COM = sum(x * data) / sum(data)
    """

    plugin_name = "Calculate center of mass"

    default_params = get_generic_param_collection("process_data_dim")

    input_data_dim = -1
    output_data_dim = -1
    output_data_label = "Center of mass"
    output_data_unit = "a.u."
    new_dataset = True

    def __init__(self, *args: tuple, **kwargs: dict):
        super().__init__(*args, **kwargs)
        self._config["slicer"] = None

    def pre_execute(self):
        """
        Pre-execute method to set up the plugin before execution.
        """
        self._config["slicer"] = None

    def execute(self, data: Dataset, **kwargs: dict) -> tuple[Dataset, dict]:
        """
        Calculate the center of mass for the input data along a single dimension.

        Parameters
        ----------
        data : pydidas.core.Dataset
            The input Dataset
        **kwargs : dict
            Any calling keyword arguments.

        Returns
        -------
        center_of_mass : Dataset
            The center of mass calculated along the specified dimension.
        kwargs : dict
            Any calling kwargs, appended by any changes in the function.
        """
        _dim = np.mod(self.get_param_value("process_data_dim"), data.ndim)
        if self._config["slicer"] is None:
            self._calculate_slicer(data)
        _x = data.axis_ranges[_dim][*self._config["slicer"]]
        center_of_mass = np.sum(_x * data, axis=_dim) / np.sum(data, axis=_dim)
        center_of_mass.data_label = "Center of mass of " + data.axis_labels[_dim]
        center_of_mass.data_unit = data.axis_units[_dim]
        return center_of_mass, kwargs

    def _calculate_slicer(self, data: Dataset):
        """
        Calculate the slices for the x-axis range.

        Parameters
        ----------
        data : Dataset
            The input Dataset.
        """
        _dim_to_process = np.mod(self.get_param_value("process_data_dim"), data.ndim)
        self._config["slicer"] = (
            [np.newaxis] * _dim_to_process
            + [slice(None)]
            + max((data.ndim - _dim_to_process - 1), 0) * [np.newaxis]
        )
        self.output_data_label = (
            "Center of mass of " + data.axis_labels[_dim_to_process]
        )
        self.output_data_unit = data.axis_units[_dim_to_process]
