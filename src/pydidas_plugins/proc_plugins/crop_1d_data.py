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
Module with the CropData Plugin which can be used to reduce the range of data.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["Crop1dData"]


import numpy as np

from pydidas.core import (
    Dataset,
    Parameter,
    ParameterCollection,
    UserConfigError,
    get_generic_param_collection,
)
from pydidas.plugins import ProcPlugin


CROP1D_PARAMS = ParameterCollection(
    get_generic_param_collection(
        "type_selection",
        "process_data_dim",
        "_process_data_dim",
    ),
    Parameter(
        "crop_low",
        float,
        None,
        name="Cropping lower boundary",
        allow_None=True,
        tooltip=(
            "The lower boundary for cropping. If None, no lower boundary will be "
            "applied."
        ),
    ),
    Parameter(
        "crop_high",
        float,
        None,
        name="Cropping upper boundary",
        allow_None=True,
        tooltip=(
            "The upper boundary for cropping. If None, no upper boundary will be "
            "applied"
        ),
    ),
)


class Crop1dData(ProcPlugin):
    """
    Crop a 1D dataset by specifying bounds, either indices or in the data range.

    Single bounds can be disabled by setting their value to None.

    Note: Setting both bounds to None will result in an error, as this
    would effectively disable the plugin, and it is assumed that is not
    intended by the user.
    """

    default_params = CROP1D_PARAMS
    plugin_name = "Crop 1D data"

    input_data_dim = -1
    output_data_dim = -1

    def __init__(self, *args: tuple, **kwargs: dict):
        super().__init__(*args, **kwargs)
        self._data = None
        self._config["slices"] = None

    def pre_execute(self):
        """
        Reset the slicing configuration.
        """
        self._data = None
        self._config["slices"] = None
        if (
            self.get_param_value("crop_low") is None
            and self.get_param_value("crop_high") is None
        ):
            raise UserConfigError(
                "Configuration error in Crop 1d Data plugin: Both cropping boundaries "
                "are None, i.e. disabled. At least one boundary must be set.\n"
                "If you do not need to crop the data, please remove the plugin from "
                "the processing tree."
            )

    def execute(self, data: Dataset, **kwargs: dict):
        """
        Crop 1D data.

        Parameters
        ----------
        data : Dataset
            The input Dataset
        **kwargs : dict
            Any calling keyword arguments.

        Returns
        -------
        new_data : Dataset
            The cropped input data
        kwargs : dict
            Any calling kwargs, appended by any changes in the function.
        """
        self._data = data
        _slices = self._get_slices()
        _new_data = data[_slices]
        return _new_data, kwargs

    def _get_slices(self) -> tuple[slice, ...]:
        """
        Get the slices for the selected data range.

        Returns
        -------
        tuple[slice, ...]
            The slices to select the range from the input data.
        """
        if self._config["slices"] is not None:
            return self._config["slices"]
        _n_dim_start = (
            self._data.ndim if self.get_param_value("process_data_dim") < 0 else 0
        )
        _i_dim = _n_dim_start + self.get_param_value("process_data_dim")
        if not 0 <= _i_dim < self._data.ndim:
            raise UserConfigError(
                "Invalid data dimension for cropping: "
                f"{self.get_param_value('process_data_dim')}. "
                f"Data has {_n_dim_start} dimensions. Please check the selected "
                "processing dimension."
            )
        self.set_param_value("_process_data_dim", _i_dim)
        _low = self.get_param_value("crop_low")
        _high = self.get_param_value("crop_high")
        if self.get_param_value("type_selection") == "Indices":
            _low = None if _low is None else int(_low)
            _high = None if _high is None else int(_high) + 1
            _slice = slice(_low, _high)
        else:
            _x = self._data.axis_ranges[_i_dim]
            if _low is None:
                _bounds = np.where(_x <= _high)[0]
            elif _high is None:
                _bounds = np.where(_x >= _low)[0]
            else:
                _bounds = np.where((_x >= _low) & (_x <= _high))[0]
            if np.unique(np.diff(_bounds)) not in (np.array([1]), np.array([])):
                raise UserConfigError(
                    "Cannot determine the cropping range from the data:\n"
                    "The selected data range is not continuous. Please check the "
                    "input data and the selected range."
                )
            if _bounds.size == 0:
                _slice = slice(0, 0)
            elif _bounds.size == 1:
                _slice = slice(_bounds[0], _bounds[0] + 1)
            else:
                _slice = slice(_bounds[0], _bounds[-1] + 1)
        self._config["slices"] = (slice(None, None),) * _i_dim + (_slice,)
        return self._config["slices"]
