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
Module with the ExtractSectors Plugin which can be used to extract a subset of sectors
from full azimuthal integration data.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["ExtractAzimuthalSectors"]


import numpy as np

from pydidas.core import Dataset, Parameter, ParameterCollection, UserConfigError
from pydidas.core.constants import FLOAT_REGEX, PROC_PLUGIN_INTEGRATED
from pydidas.plugins import ProcPlugin


_EAS_PARAMS = ParameterCollection(
    Parameter(
        "centers",
        str,
        "",
        name="Sector centers",
        tooltip=(
            "The center positions of the different sectors to be processed. pydidas "
            "will handle the integration discontinuity and combine data over the "
            "discontinuity. Multiple sectors can be selected by separating them with a "
            "semicolon character."
        ),
    ),
    Parameter(
        "width",
        float,
        10,
        name="Full sector width",
        tooltip=(
            "The full sector width defines which azimuthal bins are included in each "
            "sector. All bins which fall fully into the width around the sector centers"
            " are included. Note that the sector width must be given in the azimuthal "
            "unit (i.e. it can be either degree or rad)."
        ),
    ),
)


class ExtractAzimuthalSectors(ProcPlugin):
    """
    Extract a subset of sectors from a PyFAI 2d integration.
    """

    plugin_name = "Extract azimuthal sectors"
    plugin_subtype = PROC_PLUGIN_INTEGRATED

    default_params = _EAS_PARAMS.copy()

    input_data_dim = 2
    output_data_dim = 2
    new_dataset = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._data = None
        self._config = self._config | {
            "settings_updated_from_data": False,
            "x_pos_hash": -1,
        }
        self._factors = {}

    def pre_execute(self):
        """
        Set up the required functions and fit variable labels.
        """
        self._config["centers"] = tuple(np.round(self._get_sector_values(), 10))

    def _get_sector_values(self) -> list[float, ...]:
        """
        Get the sector center positions.

        Raises
        ------
        UserConfigError
            If the list of azimuthal sectors is empty.
        UserConfigError
            If the input does not match the regular expressions for a float number.

        Returns
        -------
        sectors : list
            The list with the floating point positions for the sector centers.
        """
        _sectors_str_list = self.get_param_value("centers").split(";")
        if _sectors_str_list == [""]:
            raise UserConfigError(
                "No sectors have been selected. Please check the "
                "ExtractAzimuthalSectors Plugin configuration."
            )
        _faulty = []
        for _str in _sectors_str_list:
            if FLOAT_REGEX.fullmatch(_str):
                continue
            _faulty.append(_str)
        if len(_faulty) > 0:
            raise UserConfigError(
                "The entries for the following sectors cannot be converted to floating "
                "point numbers: \n\n - " + "\n - ".join(_faulty)
            )
        return [float(_s) for _s in _sectors_str_list]

    def execute(self, data: Dataset, **kwargs: dict) -> tuple[Dataset, dict]:
        """
        Extract the specified azimuthal sectors from a polar dataset.

        Parameters
        ----------
        data : pydidas.core.Dataset
            The input Dataset
        **kwargs : dict
            Any calling keyword arguments.

        Returns
        -------
        _results : pydidas.core.Dataset
            The image data.
        kwargs : dict
            Any calling kwargs, appended by any changes in the function.
        """
        self._data = data
        self._update_settings_from_data()
        _res = np.zeros((len(self._config["centers"]), self._data.shape[1]))
        for _index, _factors in self._factors.items():
            _f = np.broadcast_to(_factors, data.shape[::-1]).T
            _res[_index] = np.sum(data * _f, axis=0) / np.sum(_factors)
        _results = Dataset(
            _res,
            axis_labels=data.axis_labels,
            axis_units=data.axis_units,
            axis_ranges=[self._config["centers"], data.axis_ranges[1]],
            data_label=data.data_label,
            data_unit=data.data_unit,
            metadata=data.metadata,
        )
        return _results, kwargs

    def _update_settings_from_data(self):
        """
        Output Plugin settings which depend on the input data.
        """
        _xhash = hash(self._data.axis_ranges[0].tobytes())
        if (
            self._config["settings_updated_from_data"]
            and _xhash == self._config["x_pos_hash"]
        ):
            return
        _factor = 1 if self._data.axis_units[0] == "deg" else np.pi / 180
        self._config["x_pos_hash"] = _xhash
        _x = self._data.axis_ranges[0]
        if _x.size < 3:
            raise UserConfigError(
                "The x-range of the data is too small to extract sectors with a total "
                "of less than 4 datapoints. Please check the input data."
            )
        _data_centers = np.round(
            np.concatenate([_x + i * 360 * _factor for i in [-1, 0, 1]]),
            decimals=8,
        )
        _low_bounds = _data_centers - np.insert(
            np.diff(_data_centers) / 2,
            0,
            ((_data_centers[1] - _data_centers[0]) / 2),
        )
        _high_bounds = _data_centers + np.append(
            np.diff(_data_centers) / 2,
            ((_data_centers[-1] - _data_centers[-2]) / 2),
        )
        _delta = self.get_param_value("width") / 2
        _data_width = np.diff(self._data.axis_ranges[0]).mean()
        self._config["factors"] = {}
        for _index, _center in enumerate(self._config["centers"]):
            _indices = np.where(abs(_center - _data_centers) <= _delta)[0]
            _factors = np.zeros(_x.size)
            for _ii in _indices:
                _ifactor = np.mod(_ii, _x.size)
                _factors[_ifactor] = (
                    min(_center + _delta, _high_bounds[_ii])
                    - max(_center - _delta, _low_bounds[_ii])
                ) / _data_width
            if _indices.size < 1:
                raise UserConfigError(
                    "The width of the sectors is too small for the data: No data point "
                    "fits into the selected sector width."
                )
            self._factors[_index] = _factors
        self._config["settings_updated_from_data"] = True
