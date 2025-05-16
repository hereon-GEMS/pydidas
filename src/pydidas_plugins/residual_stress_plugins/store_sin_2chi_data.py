# This file is part of pydidas.
#
# Copyright 2025, Helmholtz-Zentrum Hereon
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
The StoreSinTwoChiData plugin allows to store the results from the sin(2*chi) grouping.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Deployment"
__all__ = ["StoreSinTwoChiData"]

from typing import Any

import numpy as np
from numpy.polynomial.polynomial import Polynomial

from pydidas.core import (
    Dataset,
)
from pydidas.core.constants import (
    PROC_PLUGIN,
    PROC_PLUGIN_STRESS_STRAIN,
)
from pydidas.plugins import ProcPlugin


class StoreSinTwoChiData(ProcPlugin):
    """
    Store the data grouped as sin(2*chi) from the sin^2(chi) analysis.

    This plugin must be used after the `sin^2(chi) analysis` plugin
    (class: SinSquareChiAnalysis). It only makes the raw grouping results
    available to the user.

    The output is a 2-dimensional dataset with the following axes:

    - Axis 0:
        The raw data pointsPositive branch (label: d+), negative branch (label: d-), mean of
        both branches (label: mean), corresponding fit values (label: fit).
    - Axis 1:
        The sin(2*chi) values corresponding to the datapoints.
    """

    plugin_name = "Store sin(2*chi) data"
    plugin_type = PROC_PLUGIN
    plugin_subtype = PROC_PLUGIN_STRESS_STRAIN
    input_data_dim = -1
    output_data_dim = 1
    new_dataset = True

    def execute(self, data: Dataset, **kwargs: Any) -> tuple[Dataset, dict]:
        """
        Execute the plugin.

        Parameters
        ----------
        data : Dataset
            The input data to be processed.
        **kwargs : Any
            Any calling keyword arguments.

        Returns
        -------
        tuple[Dataset, dict]
            The processed data and additional information.
        """
        if not (
            "sin_2chi_data" in kwargs
            and "sin_square_chi_analysis_fits" in kwargs
            and "sin_square_chi_data" in kwargs
        ):
            self.raise_UserConfigError(
                "The plugin did not receive the required input data. "
                "Please check the plugin order in the workflow and assure that "
                "the `sin^2(chi) analysis` plugin is executed before this plugin."
            )
        # take only the differential data vs sin(2*chi)
        _sin_2chi_data = kwargs.get("sin_2chi_data")[2]
        _sin_2chi_data = _sin_2chi_data[_sin_2chi_data.axis_ranges[0].argsort()]
        _data_label = kwargs.get("sin_square_chi_data").data_label
        _fit_coeffs = kwargs.get("sin_square_chi_analysis_fits")
        _p_fit = Polynomial((0, _fit_coeffs[4]))
        _fitted_values = _p_fit(_sin_2chi_data.axis_ranges[0])
        _results = Dataset(
            np.append(_sin_2chi_data, _fitted_values).reshape(2, -1),
            data_label=f"difference between branches ({_data_label})",
            data_unit=_sin_2chi_data.data_unit,
            axis_labels=["0: data; 1: fit", "sin(2*chi)"],
            axis_ranges=[np.arange(2), _sin_2chi_data.axis_ranges[0]],
            axis_units=["", _sin_2chi_data.axis_units[0]],
        )
        self.output_data_label = f"sin(2*chi) results ({_sin_2chi_data.data_label})"
        self.output_data_unit = _sin_2chi_data.data_unit

        return _results, kwargs
