# This file is part of pydidas.
#
# Copyright 2024 - 2025, Helmholtz-Zentrum Hereon
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
A module for calculating the difference in d_spacing of the branches d(+) and d(-).

This plugin expects the output from the SinSquareChiGrouping plugin as input.
"""

__author__ = "Gudrun Lotze"
__copyright__ = "Copyright 2024 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Gudrun Lotze"
__status__ = "Development"
__all__ = ["Sin_2chiGrouping"]

from typing import Any

import numpy as np

from pydidas.core import Dataset
from pydidas.core.constants import (
    INTEGRATION_RESULT_UNITS,
    PROC_PLUGIN,
    PROC_PLUGIN_STRESS_STRAIN,
)
from pydidas.plugins import ProcPlugin


LABELS_SIN_2CHI = "sin(2*chi)"
LABELS_SIN2CHI = "sin^2(chi)"
LABELS_DIM0 = "0: d-, 1: d+, 2: d_mean"
UNITS_NANOMETER = "nm"
UNITS_ANGSTROM = "A"

PARAMETER_KEEP_RESULTS = "keep_results"


class Sin_2chiGrouping(ProcPlugin):
    """
    This plugin calculates the difference between both d-spacing branches of the
    psi-splitting method and the corresponding sin(2*chi) values.

    chi is the azimuthal angle of one diffraction image.

    The difference in d-spacing is given by d(+) - d(-). sin(2*chi) is calculated
    directly from sin^2(chi).

    PLEASE NOTE: Using chi instead of psi for the sin^2(psi) method is an
    approximation in the high-energy X-ray regime. Psi is the angle between the
    scattering vector q and the sample normal. The geometry of the experiment
    requires that the sample normal is parallel to the z-axis, i.e. the incoming
    beam is parallel to the sample surface.

    This plugin expects position (d-spacing) in [nm, A]. The expected input data
    is the result of the SinSquareChiGrouping plugin.

    Input must be provided in the format as given by the SinSquareChiGrouping plugin:

    - The input dataset should have three rows corresponding to d(-), d(+), and d_mean.
    - The d-spacing units should be either nanometers (nm) or angstroms (A).

    Output:
    - Difference of d-spacing branches (d(+), d(-))
    - Both d-spacing branches (d(-), d(+)) vs. sin^2(chi)
    """

    plugin_name = "Grouping of results vs sin(2*chi)"
    plugin_type = PROC_PLUGIN
    plugin_subtype = PROC_PLUGIN_STRESS_STRAIN
    input_data_dim = 2
    output_data_dim = 2

    output_data_label = (
        "0: position_neg; 1: position_pos; "
        "2: Difference of (position_pos, position_neg)"
    )
    new_dataset = True

    # modification of the keep_results parameter to ensure results are always stored
    _generics = ProcPlugin.generic_params.copy()
    _generics[PARAMETER_KEEP_RESULTS].value = True
    _generics[PARAMETER_KEEP_RESULTS].choices = [True]
    generic_params = _generics

    def execute(self, ds: Dataset, **kwargs: dict[str, Any]) -> tuple[Dataset, dict]:
        d_output_sin_2chi_method = self._calculate_diff_d_spacing_vs_sin_2chi(ds)

        return d_output_sin_2chi_method, kwargs

    def _ensure_axis_labels(self, ds: Dataset) -> None:
        """
        Ensure the axis labels for dimension 0 and 1 are as expected.

        Parameters
        ----------
        ds : Dataset
            The input to check.

        Raises
        ------
        UserConfigError
            If the axis labels are not as expected.
        """
        if ds.axis_labels[0] != LABELS_DIM0:
            self.raise_UserConfigError(
                f"Expected axis label `{LABELS_DIM0}`, but got `{ds.axis_labels[0]}`"
            )

        if ds.axis_labels[1] != LABELS_SIN2CHI:
            self.raise_UserConfigError(
                f"Expected axis label `{LABELS_SIN2CHI}`, but got `{ds.axis_labels[1]}`"
            )

    def _calculate_diff_d_spacing_vs_sin_2chi(self, ds: Dataset) -> Dataset:
        """
        Calculate the difference between d-spacing branches (d(+) - d(-)).

        This method processes the input dataset to compute the difference between
        the d-spacing branches (d(+) - d(-)) and updates the dataset with the
        calculated values. The input dataset is expected to have three rows
        corresponding to d(-), d(+), and d_mean, and the units should be either
        nanometers (nm) or angstroms (A). The method ensures the input dataset is
        correctly formatted and labeled.

        Parameters
        ----------
        ds : Dataset
            The input dataset containing d-spacing values and corresponding
            sin^2(chi) values.

        Returns
        -------
        Dataset:
            A new dataset with the d-spacing for the two branches as well as
            the calculated difference between d-spacing branches and the
            corresponding sin(2*chi) values as axis range.

        Raises
        ------
        UserConfigError
            If the input dataset is not correctly formatted, labeled, or if the
            units are not in nanometers (nm) or angstroms (A).
        """
        if not isinstance(ds, Dataset):
            self.raise_UserConfigError("Input must be an instance of Dataset.")
        self._ensure_axis_labels(ds)
        if ds.shape[0] != 3:
            self.raise_UserConfigError(
                f"Incoming dataset expected to have 3 rows, {LABELS_DIM0}. "
                "Please verify your Dataset."
            )

        if ds.data_unit not in INTEGRATION_RESULT_UNITS:
            self.raise_UserConfigError(
                "Incoming dataset does not have the expected units. Only the "
                "following units are allowed: "
                + ", ".join(INTEGRATION_RESULT_UNITS)
                + ". Please verify that the Plugin is situated correctly in the "
                + "workflow."
            )
        _results = Dataset(ds.array.copy(), **ds.property_dict)
        _results[2, :] = np.diff(ds[:2, :], axis=0)
        _results.data_label = "Difference between pos. and neg. branch"
        _results.axis_labels: dict[int, str] = {
            0: "0: neg. branch, 1: pos. branch, 2: difference",
            1: LABELS_SIN_2CHI,
        }
        _results.update_axis_range(
            1, self._calculate_sin_2chi_values(ds.axis_ranges[1])
        )
        return _results

    def _calculate_sin_2chi_values(self, s2c_values: np.ndarray) -> np.ndarray:
        """
        Calculate the sin(2*chi) value directly s from the sin^2(chi) values.

        Parameters
        ----------
        s2c_values : np.ndarray
            The sin^2(chi) values.

        Returns
        -------
        np.ndarray :
            The sin(2*chi) values.
        """
        if not isinstance(s2c_values, np.ndarray):
            self.raise_UserConfigError("Input must be an instance of np.ndarray.")

        if np.any(s2c_values < 0) or np.any(s2c_values > 1):
            self.raise_UserConfigError(
                "Values in s2c_values must be between 0 and 1 inclusive."
            )

        return np.sin(2 * np.arcsin(np.sqrt(s2c_values)))


Sin_2chiGrouping.register_as_base_class()
