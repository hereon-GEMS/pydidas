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
Module with the FioMcaLineScanSeriesLoader Plugin which can be used to load
MCA spectral data
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["ASCII1dProfileLoader"]


from typing import Any

import numpy as np

from pydidas.contexts import ScanContext
from pydidas.core import (
    Dataset,
    Parameter,
    get_generic_param_collection,
)
from pydidas.data_io import import_data
from pydidas.plugins import Input1dXRangeMixin, InputPlugin


SCAN = ScanContext()


class ASCII1dProfileLoader(Input1dXRangeMixin, InputPlugin):
    """
    Load a 1d profile from an ASCII file with a single dataset.

    This plugin allows to load 1d profiles and the corresponding x-scale from
    ASCII files.

    The metadata in the files is parsed automatically, where the file format allows.

    For files with multiple columns, the advanced settings allow to select
    which column to read for the x-scale and y data with the "x_column" and
    "y_column", respectively. The columns are numbered starting from 0.

    Supported files include .txt, .asc, .dat, .csv and .fio.

    Parameters
    ----------
    use_custom_xscale : bool, optional
        Keyword to toggle an absolute energy scale for the channels. If False,
        pydidas will simply use the channel number. The default is False.
    x0_offset : float, optional
        The offset for channel zero, if the absolute energy scale is used.
        This value must be given in eV. The default is 0.
    x_delta : float, optional
        The width of each energy channel. This value is given in units and only
        used when the absolute x-scale is enabled. The default is 1.
    x_label : str, optional
        The label for the x-axis of the plot. This is only used when the
        absolute x-scale is enabled. The default is "Energy".
    x_unit : str, optional
        The unit for the x-axis of the plot. This is only used when the
        absolute x-scale is enabled. The default is "eV".
    """

    plugin_name = "ASCII 1d profile loader"
    default_params = InputPlugin.default_params.copy()
    default_params.add_params(get_generic_param_collection("x_column", "y_column"))
    advanced_parameters = InputPlugin.advanced_parameters + ["x_column", "y_column"]
    base_output_data_dim = 1

    def __init__(self, *args: Parameter, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self._config.update({"header_lines": 0})
        self.__xscale_valid = False

    def pre_execute(self):
        """
        Prepare loading spectra from a file series.
        """
        super().pre_execute()
        self.__xscale_valid = False
        self._standard_kwargs = {"forced_dimension": 1, "roi": self._get_own_roi()}

    def get_frame(self, index: int, **kwargs: Any) -> tuple[Dataset, dict]:
        """
        Get the frame for the given index.

        Parameters
        ----------
        index : int
            The index of the scan point.
        **kwargs : Any
            Keyword arguments for loading frames.

        Returns
        -------
        dataset : Dataset
            The loaded dataset.
        kwargs : Any
            The updated kwargs.
        """
        _dataset = import_data(
            self.get_filename(index), **(self._standard_kwargs | kwargs)
        )
        if self.get_param_value("use_custom_xscale"):
            if not self.__xscale_valid:
                self.__create_x_scale(_dataset.size)
            _dataset.update_axis_label(0, self.get_param_value("x_label"))
            _dataset.update_axis_unit(0, self._config["axis_unit"])
            _dataset.update_axis_range(0, self._config["axis_range"])
        return _dataset, kwargs

    def __create_x_scale(self, n_points: int) -> None:
        """
        Create an energy scale for a spectrum file based on the energy parameters.

        Parameters
        ----------
        n_points : int
            The number of points in the energy scale.
        """
        _unit = self.get_param_value("x_unit")
        _scale = np.arange(n_points) * self.get_param_value("x_delta")
        _scale += self.get_param_value("x0_offset")
        self._config["axis_unit"] = _unit
        self._config["axis_range"] = _scale
        self.__xscale_valid = True
