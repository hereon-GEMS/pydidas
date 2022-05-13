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
Module with the RemoveOutliers Plugin which can be used to remove outliers of
a defined width.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ["RemoveOutliers"]

import warnings

import numpy as np

from pydidas.core.constants import PROC_PLUGIN
from pydidas.core import ParameterCollection, Parameter
from pydidas.plugins import ProcPlugin


class RemoveOutliers(ProcPlugin):
    """
    Remove outlier points from a 1D dataset.
    """

    plugin_name = "Remove Outliers"
    basic_plugin = False
    plugin_type = PROC_PLUGIN
    default_params = ParameterCollection(
        Parameter(
            "kernel_width",
            int,
            2,
            name="Kernel width",
            tooltip=(
                "The width of the search kernel (i.e. the maximum "
                "width of outliers which can be detected."
            ),
        ),
        Parameter(
            "outlier_threshold",
            float,
            1,
            name="Relative outlier threshold",
            tooltip=(
                "The threshold for outliers. Any points which "
                "differ more than the threshold from the background"
                " will be removed."
            ),
        ),
    )
    input_data_dim = 1
    output_data_dim = 1

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._data = None

    def pre_execute(self):
        """
        Set up the required functions and fit variable labels.
        """

    def execute(self, data, **kwargs):
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
        _width = self.get_param_value("kernel_width")
        _threshold = self.get_param_value("outlier_threshold")
        _data_p = np.roll(data, _width)
        _data_m = np.roll(data, -_width)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            _data_low1 = ((data - _data_p) / data)[_width:-_width]
            _data_low2 = ((data - _data_m) / data)[_width:-_width]
            _low_outliers = np.where(
                (_data_low1 <= -_threshold) & (_data_low2 <= -_threshold)
            )[0]

            _data_high1 = ((data - _data_p) / _data_p)[_width:-_width]
            _data_high2 = ((data - _data_m) / _data_m)[_width:-_width]
            _high_outliers = np.where(
                (_data_high1 >= _threshold) & (_data_high2 >= _threshold)
            )[0]
        _outliers = np.concatenate((_low_outliers, _high_outliers)) + _width
        data[_outliers] = (_data_p[_outliers] + _data_m[_outliers]) / 2
        return data, kwargs
