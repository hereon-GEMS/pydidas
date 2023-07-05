# This file is part of pydidas.
#
# Copyright 2023, Helmholtz-Zentrum Hereon
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
__copyright__ = "Copyright 2023, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["AverageOppositeSectors"]

from typing import Tuple

import numpy as np

from pydidas.core.constants import PROC_PLUGIN, PROC_PLUGIN_INTEGRATED
from pydidas.core import (
    Dataset,
    # Parameter,
    # ParameterCollection,
    UserConfigError,
)
from pydidas.plugins import ProcPlugin


_symmetry = "180\u00B0 rotational symmetry around center"
_full_symmetry = (
    "180\u00B0 rotational symmetry and mirror symmetry around \u03C7=90\u00B0"
)


class AverageOppositeSectors(ProcPlugin):
    """
    Average opposite sectors in the integration data.

    This plugin checks the input data and combines sectors opposite one another
    (with respect to the beamcenter) by averaging their intensity to improve
    statistics.
    """

    plugin_name = "Average opposite sectors"
    basic_plugin = False
    plugin_type = PROC_PLUGIN
    plugin_subtype = PROC_PLUGIN_INTEGRATED
    input_data_dim = 2
    output_data_dim = 2
    output_data_label = "Integrated data"
    output_data_unit = "a.u."
    new_dataset = True
    # default_params = ParameterCollection(
    #     Parameter(
    #         "symmetry",
    #         str,
    #         _symmetry,
    #         choices=[_symmetry, _full_symmetry],
    #         toolTip=(
    #             u"The assumed symmetry. For '180\u00B0 rotational symmetry around "
    #             "center', it is simply assumed that sectors which are rotated by "
    #             u"180\u00B0 around the beamcenter have the same signal and can be "
    #             f"averaged. For '{_full_symmetry}', an additional symmetry around the"
    #             " detector y-axis is asumed, i.e. a total of four sectors will be "
    #             "combined for each new sector."
    #         )
    #     )
    # )

    def pre_execute(self):
        """
        Run the pre-execution hook and set the execute method based on the settings.
        """
        self._config["symmetry_check"] = False

    def execute(self, data: Dataset, **kwargs: dict) -> Tuple[Dataset, dict]:
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
        _data : pydidas.core.Dataset
            The image data.
        kwargs : dict
            Any calling kwargs, appended by any changes in the function.
        """
        if not self._config["symmetry_check"]:
            self._check_input_symmetry(data)
        _i = data.shape[0] // 2
        _new_data = (data[:_i] + data[_i:]) / 2.0
        _new_data.update_axis_ranges(
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
        _sym_number = 2  # if self.get_param_value("symmetry") == _symmetry else 4
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

    # def _check_input_full_symmetry(self, data: Dataset):
    #     """
    #     Check the input symmetry for full rotational and mirror symmetry.

    #     Parameters
    #     ----------
    #     data : Dataset
    #         The input dataset.

    #     Raises
    #     ------
    #     UserConfigError
    #         If the number of datapoints or data range does not match the symmetry.
    #     """
    #     _sym_number = 2 if self.get_param_value("symmetry") == _symmetry else 4
    #     _chi = data.axis_ranges[0]
    #     _half_rot = np.round(180 if "deg" in data.axis_units[0] else np.pi, 5)
    #     _quarter_rot = np.round(_half_rot / 2, 5)
    #     _chi = np.round(np.mod(_chi, _half_rot), 5)
    #     _chi = np.where(_chi > _quarter_rot, _half_rot - _chi, _chi)
    #     if 0 in _chi:
    #         _i_zero = np.where(_chi ==0)[0]
    #         _chi = np.roll(np.insert(_chi, _i_zero, 0), -1)
    #     if _quarter_rot in _chi:
    #         _i_q = np.where(_chi ==_quarter_rot)[0]
    #         _chi = np.insert(_chi, _i_q, _quarter_rot)

    #     self._config["symmetry_check"] = True

    def calculate_result_shape(self):
        """Calculate the result's shape based on the input data shape."""
        _shape = self._config.get("input_shape", None)
        if _shape is None:
            raise UserConfigError(
                "Cannot calculate the output shape for the 'Average opposite sectors' "
                "plugin because the input shape is unknown."
            )
        if np.mod(_shape[0], 2) != 0:
            raise UserConfigError(
                "The input shape is invalid for the 'Average opposite sectors' "
                f"plugin. The number of input points {_shape[0]} is not divisible by 2."
            )
        self._config["result_shape"] = (_shape[0] // 2, _shape[1])
        # _sym = self.get_param_value("symmetry")
        # _sym_number = 2 if _sym == _symmetry else 4
        # if np.mod(_shape[0], _sym_number) != 0:
        #     raise UserConfigError(
        #         "The input shape is invalid for the 'Average opposite sectors' "
        #         f"plugin. The number of input points {_shape[0]} is not divisible by "
        #         f"{_sym_number} in the specified geometry ({_sym})."
        #     )
        # self._config["result_shape"] = (
        #     _shape[0] // _sym_number + (1 if _sym_number == 4 else 0), _shape[1]
        # )
