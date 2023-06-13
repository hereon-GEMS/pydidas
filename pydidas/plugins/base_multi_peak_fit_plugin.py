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
Module with the FitMultiPeak base plugin which can be subclassed to fit a specific
number of peaks to data.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["FitMultiPeak"]


from ..core.utils import calculate_result_shape_for_multi_input_dims
from .base_fit_plugin import BaseFitPlugin


class FitMultiPeak(BaseFitPlugin):
    """
    Fit multiple peaks to the input data.

    This plugin allows to fit the input data with any function defined in the
    pydidas.core.fitting package.
    """

    plugin_name = "Base fit multiple peaks"

    def check_center_positions(self) -> bool:
        """
        Check the fitted center positions.

        Returns
        -------
        bool
            Flag whether all centers are in the input x range.
        """
        return set([True]) == set(
            self._data_x[0] <= self._fit_params[_key] <= self._data_x[-1]
            for _key in self._fit_params
            if _key.startswith("center")
        )

    @calculate_result_shape_for_multi_input_dims
    def calculate_result_shape(self):
        """
        Calculate the shape of the Plugin results.
        """
        _output = self.get_param_value("fit_output")
        self.output_data_label = _output
        _dim1 = len(_output.split(";"))
        self._config["result_shape"] = (
            (self.num_peaks, _dim1) if _dim1 > 1 else (self.num_peaks,)
        )
        self._config["single_result_shape"] = self._config["result_shape"]
