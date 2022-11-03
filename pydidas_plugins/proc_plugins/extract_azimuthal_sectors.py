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
Module with the ExtractSectors Plugin which can be used to extract a subset of sectors
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ["ExtractAzimuthalSectors"]


import numpy as np

from pydidas.core.constants import PROC_PLUGIN, PROC_PLUGIN_INTEGRATED, FLOAT_REGEX
from pydidas.core import Dataset, Parameter, ParameterCollection, UserConfigError
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
    Parameter(
        "mode",
        str,
        "Average",
        name="Operation type",
        choices=["Sum", "Average"],
        tooltip=(
            "The operation to create the new datasets. If 'Sum', the contributions "
            "from all points in the sector will be added. If 'Average', all data "
            "points will be averaged."
        ),
    ),
)


class ExtractAzimuthalSectors(ProcPlugin):
    """
    Extract a subset of sectors from a PyFAI 2d integration.
    """

    plugin_name = "Extract azimuthal sectors"
    basic_plugin = False
    plugin_type = PROC_PLUGIN
    plugin_subtype = PROC_PLUGIN_INTEGRATED
    default_params = _EAS_PARAMS.get_copy()
    input_data_dim = 2
    output_data_dim = 2
    new_dataset = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._data = None
        self._config = self._config | {"settings_updated_from_data": False}

    def pre_execute(self):
        """
        Set up the required functions and fit variable labels.
        """
        self._config["centers"] = np.round(self._get_sector_values(), 10)

    def _get_sector_values(self):
        """
        Test

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

    def execute(self, data, **kwargs):
        """
        Fit a peak to the data.

        Note that the results includes the original data, the fitted data and
        the residual and that the fit Parameters are included in the kwarg
        metadata.

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
        self._data = data
        self._update_settings_from_data()
        _res = np.zeros((self._config["centers"].size, self._data.shape[1]))
        for _index, _slices in self._config["slices"].items():
            _res[_index] = np.sum(data[_slices, :], axis=0)
            if self.get_param_value("mode") == "Average":
                _res[_index] /= len(_slices)
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
        if self._config["settings_updated_from_data"]:
            return
        _sector_width = self.get_param_value("width")
        _n_data_sectors = self._data.shape[0]
        _factor = 1 if self._data.axis_units[0] == "deg" else np.pi / 180
        _data_centers = np.round(
            np.concatenate(
                (
                    self._data.axis_ranges[0] - 360 * _factor,
                    self._data.axis_ranges[0],
                    self._data.axis_ranges[0] + 360 * _factor,
                )
            ),
            10,
        )
        _data_width = _factor * 360 / _n_data_sectors
        self._config["slices"] = {}
        for _index, _center in enumerate(self._config["centers"]):
            _indices = (
                np.where(
                    (
                        abs(_data_centers - _data_width / 2 - _center)
                        <= _sector_width / 2 + 1e-9
                    )
                    & (
                        abs(_data_centers + _data_width / 2 - _center)
                        <= _sector_width / 2 + 1e-9
                    )
                )[0]
                - _n_data_sectors
            )
            _indices = np.mod(_indices, _n_data_sectors)
            if _indices.size < 1:
                raise UserConfigError(
                    "The width of the sectors is too small for the data: No data point "
                    "fits into the selected sector width."
                )
            self._config["slices"][_index] = _indices
        self._config["settings_updated_from_data"] = True

    def calculate_result_shape(self):
        """
        Calculate the shape of the Plugin results.
        """
        _sectors = self.get_param_value("centers")
        _n_out = len(_sectors.split(";"))
        _n_data = self.input_shape[1]
        self._config["result_shape"] = (_n_out, _n_data)
