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
Module with the InputPlugin base class.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["Input1dXRangeMixin"]


from typing import Any

import numpy as np

from pydidas.core import Dataset, Parameter, get_generic_parameter


class Input1dXRangeMixin:
    """
    A mixin class for input plugins that provides functionality for handling
    x-range calculations and custom x-scale settings.
    """

    base_output_data_dim = 1
    has_unique_parameter_config_widget = True

    def __init__(self, *args: Parameter, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self.add_params(
            get_generic_parameter("use_custom_xscale"),
            get_generic_parameter("x0_offset"),
            get_generic_parameter("x_delta"),
            get_generic_parameter("x_label"),
            get_generic_parameter("x_unit"),
        )

    def pre_execute(self):
        """
        Run generic pre-execution routines.
        """
        self._config["xrange"] = None
        super().pre_execute()

    def execute(self, ordinal: int, **kwargs: Any) -> tuple[Dataset, dict]:
        """
        Import the data and pass it on after (optionally) handling image multiplicity.

        Parameters
        ----------
        ordinal : int
            The ordinal index of the scan point.
        **kwargs : Any
            Keyword arguments passed to the execute method.

        Returns
        -------
        Dataset
            The image data frame.
        kwargs : Any
            The updated kwargs.
        """
        _data, kwargs = super().execute(ordinal, **kwargs)
        if self.params.get_value("use_custom_xscale"):
            if self._config["xrange"] is None:
                self.calculate_xrange(_data.shape[-1])
            _data.update_axis_range(-1, self._config["xrange"])
            _data.update_axis_unit(-1, self._config["axis_unit"])
            _data.update_axis_label(-1, self._config["axis_label"])
        return _data, kwargs

    def calculate_xrange(self, n_points: int):
        """
        Calculate the x-range for the data.
        """
        self._config["axis_unit"] = self.params.get_value("x_unit")
        self._config["axis_label"] = self.params.get_value("x_label")
        self._config["xrange"] = np.arange(n_points) * self.params.get_value(
            "x_delta"
        ) + self.params.get_value("x0_offset")

    def get_parameter_config_widget(self):
        """Get the parameter config widget for the plugin."""
        from pydidas.widgets.plugin_config_widgets import (
            PluginConfigWidgetWithCustomXscale,
        )

        return PluginConfigWidgetWithCustomXscale
