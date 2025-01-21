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
Module with the AverageOppositeSectors Plugin which allows to average sectors in the
integration which are opposite one another (i.e. rotated by 180°).
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["AverageOppositeSectors"]


import numpy as np

from pydidas.core import Dataset, UserConfigError
from pydidas.core.constants import PROC_PLUGIN_INTEGRATED
from pydidas.plugins import ProcPlugin


class AverageOppositeSectors(ProcPlugin):
    """
    Average opposite sectors in the integration data.

    This plugin checks the input data and combines sectors opposite one another
    (with respect to the beamcenter) by averaging their intensity to improve
    statistics.
    """

    plugin_name = "Average opposite sectors"
    plugin_subtype = PROC_PLUGIN_INTEGRATED

    input_data_dim = 2
    output_data_dim = 2
    output_data_label = "Integrated data"
    output_data_unit = "a.u."
    new_dataset = True

    def pre_execute(self):
        """
        Run the pre-execution hook and set the execute method based on the settings.
        """
        self._config["symmetry_check"] = False

    def execute(self, data: Dataset, **kwargs: dict) -> tuple[Dataset, dict]:
        """
        Crop 1D data.

        Parameters
        ----------
        data : pydidas.core.Dataset
            The input Dataset
        **kwargs : dict
            Any calling keyword arguments.

        Returns
        -------
        _new_data : pydidas.core.Dataset
            The image data.
        kwargs : dict
            Any calling kwargs, appended by any changes in the function.
        """
        if not self._config["symmetry_check"]:
            self._check_input_symmetry(data)
        _i = data.shape[0] // 2
        _new_data = (data[:_i] + data[_i:]) / 2.0
        _new_data.update_axis_range(
            0,
            np.mod(
                _new_data.axis_ranges[0], 180 if "deg" in data.axis_units[0] else np.pi
            ),
        )
        return _new_data, kwargs

    def _check_input_symmetry(self, data: Dataset):
        """
        Check the input symmetry for rotational symmetry.

        Parameters
        ----------
        data : Dataset
            The input dataset.

        Raises
        ------
        UserConfigError
            If the number of datapoints or data range does not match the symmetry.
        """
        _sym_number = 2
        _chi = data.axis_ranges[0]
        _half_rot = 180 if "deg" in data.axis_units[0] else np.pi
        _chi_mod = np.round(np.mod(_chi, _half_rot), 5).reshape(
            _sym_number, data.shape[0] // _sym_number
        )
        _chi_mod.shape = (_sym_number, data.shape[0] // _sym_number)
        _delta = np.std(_chi_mod, axis=0)
        if not np.allclose(_delta, np.zeros(_chi_mod.shape), atol=1e-1):
            raise UserConfigError(
                "[Average opposite sectors]: The input ranges for the plugin are not "
                "symmetric and cannot be processed. Please check the input data range "
                "for chi."
            )
        self._config["symmetry_check"] = True
