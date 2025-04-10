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


from pydidas_plugins.proc_plugins.sin_square_chi_grouping import SinSquareChiGrouping
from pydidas_plugins.proc_plugins.sin_2chi import DspacingSin_2chi

from pydidas.core import Dataset, UserConfigError, get_generic_param_collection
from pydidas.core.constants import PROC_PLUGIN, PROC_PLUGIN_STRESS_STRAIN
from pydidas.plugins import OutputPlugin, ProcPlugin


_VALID_DATA_AXIS_1_LABELS = ("2theta", "d-spacing", "Q", "r")


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

    plugin_name = "Sin^2 chi analysis"
    basic_plugin = False
    plugin_type = PROC_PLUGIN
    plugin_subtype = PROC_PLUGIN_STRESS_STRAIN
    input_data_dim = -1
    output_data_dim = 2
    new_dataset = True
    generic_params = OutputPlugin.generic_params.copy()
    default_params = get_generic_param_collection(
        "d_spacing_unit",
    )

    def __init__(self, *args: tuple, **kwargs: dict) -> None:
        OutputPlugin.__init__(self, *args, **kwargs)
        self._group_in_sin_square_chi = SinSquareChiGrouping()
        self._group_in_sin_2_chi = DspacingSin_2chi()
        self._config["flag_convert_to_d_spacing"] = None

    def pre_execute(self):
        """
        Prepare the plugin for execution.
        """
        OutputPlugin.pre_execute(self)

    def execute(self, data: Dataset, **kwargs: dict):
        """
        Execute the plugin.

        Parameters
        ----------
        data : Dataset
            The input data to be processed.

        Returns
        -------
        tuple
            The processed data and additional information.
        """
        data = self._prepare_data(data)
        new_data = self._group_in_sin_square_chi.execute(data)
        return new_data, kwargs

    def _prepare_data(self, data: Dataset) -> Dataset:
        """
        Prepare the input data for processing.

        Parameters
        ----------
        data : Dataset
            The input data to be processed.

        Returns
        -------
        Dataset
            The processed data.
        """
        if self._config["flag_convert_to_d_spacing"] is None:
            self._check_input_data(data)
        # if self._config["flag_convert_to_d_spacing"]:
        #     data, _ = self._convert_to_d_spacing.execute(data)
        return data

    def _check_input_data(self, data: Dataset):
        """
        Run basic checks on the input data.

        This method checks the dimensionality and whether the input data must
        be converted to d-spacing values.

        Parameters
        ----------
        data : Dataset
            The input data to be checked.
        """
        if data.ndim != 2:
            raise UserConfigError(
                f"Configuration in `{self.plugin_name}` (node ID {self.node_id}) "
                "is invalid:\n"
                "The input data must be 2D integration result."
            )
        if (
            data.axis_labels[0] != "chi"
            #            or data.axis_labels[1] not in _VALID_DATA_AXIS_1_LABELS
        ):
            raise UserConfigError(
                f"Configuration in `{self.plugin_name}` (node ID {self.node_id}) "
                "is invalid:\n"
                "The data does not appear to be a valid 2D integration result. "
                "The first axis must be `chi` and the second axis must be either of "
                + ", ".join(f"`{_item}`" for _item in _VALID_DATA_AXIS_1_LABELS)
                + "."
            )
        self._config["flag_convert_to_d_spacing"] = data.axis_labels[1] != "d-spacing"
