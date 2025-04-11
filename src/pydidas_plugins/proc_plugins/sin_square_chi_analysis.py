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
The SinSquareChiAnalysis plugin combines all required tools for the analysis of
sin^2(chi) data.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Deployment"
__all__ = ["SinSquareChiAnalysis"]

from typing import Any, Callable

from pydidas_plugins.proc_plugins.sin_2chi_grouping import Sin_2chiGrouping
from pydidas_plugins.proc_plugins.sin_square_chi_grouping import SinSquareChiGrouping

from pydidas.contexts import DiffractionExperimentContext
from pydidas.core import (
    Dataset,
    Parameter,
    ParameterCollection,
    UserConfigError,
)
from pydidas.core.constants import PROC_PLUGIN, PROC_PLUGIN_STRESS_STRAIN
from pydidas.core.utils.scattering_geometry import convert_integration_result
from pydidas.plugins import OutputPlugin, ProcPlugin


_VALID_DATA_AXIS_1_LABELS = ("2theta", "d-spacing", "Q", "r")
_VALID_UNITS = ("nm", "A", "nm^-1", "A^-1", "deg", "rad", "mm")

OUTPUT_UNIT_PARAM = Parameter(
    "output_type",
    str,
    "Same as input",
    name="Output data type",
    choices=[
        "Same as input",
        "2theta / deg",
        "2theta / rad",
        "d-spacing / nm",
        "d-spacing / A",
        "Q / nm^-1",
        "Q / A^-1",
        "r / mm",
    ],
    tooltip=(
        "The unit of the output data. The default is `Same as input`, which "
        "means that the output data will have the same unit as the input data. "
        "Choosing a different unit will convert the data to the selected unit."
    ),
)
EXPORT_IMAGES_PARAM = Parameter(
    "export_images",
    bool,
    False,
    name="Export results as image for each data point",
    choices=[True, False],
    tooltip=(
        "If selected, the plugin will export images of the results for each "
        "data point. Please keep in mind that this will slow down processing "
        "and potentially create a large number of files."
    ),
)


class SinSquareChiAnalysis(ProcPlugin, OutputPlugin):
    """
    Analyses the d-spacing values of a dataset using the sin^2(chi) method.

    This plugin is designed to work with datasets containing d-spacing values
    (or 2 theta values) and chi values. It performs the following steps:

    1. (only if required) convert 2theta to d-spacing values
    2. Group the values for chi positions with similar sin^2(chi) values
    3. Additionally, group the d-spacing values according to the slopes in sin(2*chi)
    4. Fit the grouped values with a linear function.

    Optionally, this plugin also allows to export images of the fits for
    each data point.

    NOTE: This plugin currently only allows chi to given in degrees.
    """

    plugin_name = "Sin^2(chi) analysis"
    basic_plugin = False
    plugin_type = PROC_PLUGIN
    plugin_subtype = PROC_PLUGIN_STRESS_STRAIN
    input_data_dim = -1
    output_data_dim = 2
    new_dataset = True
    generic_params = OutputPlugin.generic_params.copy()
    default_params = ParameterCollection(OUTPUT_UNIT_PARAM, EXPORT_IMAGES_PARAM)
    has_unique_parameter_config_widget = False  # TODO : implement custom widget

    def __init__(self, *args: tuple, **kwargs: dict) -> None:
        self._EXP = kwargs.pop("diffraction_exp", DiffractionExperimentContext())
        OutputPlugin.__init__(self, *args, **kwargs)
        self._plugin_group_in_sin_square_chi = SinSquareChiGrouping()
        self._plugin_group_in_sin_2_chi = Sin_2chiGrouping()
        self._converter: Callable | None = None

    def pre_execute(self):
        """
        Prepare the plugin for execution.
        """
        OutputPlugin.pre_execute(self)
        self._config["flag_conversion_set_up"] = False
        self._config["flag_input_data_check"] = False
        self._converter = None

    def execute(self, data: Dataset, **kwargs: dict[str, Any]) -> tuple[Dataset, dict]:
        """
        Execute the plugin.

        Parameters
        ----------
        data : Dataset
            The input data to be processed.
        **kwargs : dict
            Any calling keyword arguments.

        Returns
        -------
        tuple[Dataset, dict]
            The processed data and additional information.
        """
        if not self._config["flag_input_data_check"]:
            self._check_input_data(data)
        _sin_square_chi_data, _sin_2chi_data = self._regroup_data_w_sin_chi(data)

    def _regroup_data_w_sin_chi(self, data: Dataset) -> tuple[Dataset, Dataset]:
        """
        Regroup the data with sin^2(chi) and sin(2*chi).
        """
        _sin_square_chi_data, _ = self._plugin_group_in_sin_square_chi.execute(data)
        if not self._config["flag_conversion_set_up"]:
            self._set_up_converter(_sin_square_chi_data)
        _sin_square_chi_data = self._converter(
            _sin_square_chi_data,
            *self._config["converter_args"],
        )
        _sin_2chi_data = self._plugin_group_in_sin_2_chi.execute(_sin_square_chi_data)
        return _sin_square_chi_data, _sin_2chi_data

    def _check_input_data(self, data: Dataset):
        """
        Run basic checks on the input data.

        This method checks the dimensionality and whether the input data
        can be understood as fitted data.

        Parameters
        ----------
        data : Dataset
            The input data to be checked.
        """
        if data.ndim != 2:
            raise UserConfigError(
                f"Configuration in `{self.plugin_name}` (node ID {self.node_id}) "
                "is invalid:\n"
                "The input data must be two-dimensional array "
                "(from a FitSinglePeak plugin)."
            )
        if data.axis_labels[0] != "chi" or "position" not in data.data_label:
            raise UserConfigError(
                f"Configuration in `{self.plugin_name}` (node ID {self.node_id}) "
                "is invalid:\n"
                "The data does not appear to be a valid 2D integration result. "
                "The first axis must be `chi` and the second axis must be either of "
                + ", ".join(f"`{_item}`" for _item in _VALID_DATA_AXIS_1_LABELS)
                + "."
            )
        self._config["flag_input_data_check"] = True

    def _set_up_converter(self, input_data: Dataset):
        """
        Set up the conversion method based on the input data.
        """
        if self.get_param_value("output_type") == "Same as input":
            self._converter = self._converter_identity
            self._config["converter_args"] = ()
        else:
            _input_type = input_data.data_label + " / " + input_data.data_unit
            self._converter = convert_integration_result
            self._config["converter_args"] = (
                _input_type,
                self.get_param_value("output_type"),
                self._EXP.xray_wavelength_in_m,
                self._EXP.detector_dist_in_m,
            )
        self._config["flag_conversion_set_up"] = True

    def _converter_identity(self, data: Dataset, *args: tuple) -> Dataset:
        """Identity conversion function."""
        return data
