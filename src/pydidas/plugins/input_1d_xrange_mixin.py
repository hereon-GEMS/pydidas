# This file is part of pydidas.
#
# Copyright 2023 - 2026, Helmholtz-Zentrum Hereon
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
Module with the Input1dXRangeMixin class which extends input plugins with
support for custom x-scales.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2026, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["Input1dXRangeMixin"]


from typing import TYPE_CHECKING, Any

import numpy as np

from pydidas.core import Dataset, Parameter, get_generic_parameter
from pydidas.core.lazy_imports.lazy_objects import LazyObject


if TYPE_CHECKING:
    from pydidas.core import ConfigDict, ParameterCollection
    from pydidas.widgets.plugin_config_widgets import GenericPluginConfigWidget

PluginConfigWidgetWithCustomXscale = LazyObject(
    "pydidas.widgets.plugin_config_widgets", "PluginConfigWidgetWithCustomXscale"
)


class Input1dXRangeMixin:
    """
    A mixin class for input plugins that provides functionality for handling
    x-range calculations and custom x-scale settings.

    Initialization arguments are passed to the parent class's constructor.
    The mixin only adds parameters for custom x-scale settings.
    """

    config: "ConfigDict"
    params: "ParameterCollection"

    base_output_data_dim = 1
    has_unique_parameter_config_widget = True

    def __init__(self, *args: Parameter, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)  # type: ignore[call-arg]
        self.add_params(  # type: ignore[attr-defined]
            get_generic_parameter("use_custom_xscale"),
            get_generic_parameter("x0_offset"),
            get_generic_parameter("x_delta"),
            get_generic_parameter("x_label"),
            get_generic_parameter("x_unit"),
        )

    def pre_execute(self) -> None:
        """Run generic pre-execution routines."""
        self.config["xrange"] = None
        super().pre_execute()  # type: ignore[misc]

    def execute(self, ordinal: int, **kwargs: Any) -> tuple[Dataset, dict]:
        """
        Import the data and (optionally) apply the custom x-scale.

        Parameters
        ----------
        ordinal : int
            The ordinal index of the scan point.
        **kwargs : Any
            Keyword arguments passed to the execute method.

        Returns
        -------
        Dataset
            The 1D data with the (optional) custom x-axis.
        kwargs : dict
            The updated kwargs.
        """
        _data, kwargs = super().execute(ordinal, **kwargs)  # type: ignore[misc]
        if self.params.get_value("use_custom_xscale"):
            if self.config["xrange"] is None:
                self.calculate_xrange(_data.shape[-1])
            _data.update_axis_range(-1, self.config["xrange"])
            _data.update_axis_unit(-1, self.config["axis_unit"])
            _data.update_axis_label(-1, self.config["axis_label"])
        return _data, kwargs

    def calculate_xrange(self, n_points: int) -> None:
        """
        Calculate the x-range for the data and store it in the config.

        Parameters
        ----------
        n_points : int
            The number of points in the data.
        """
        self.config["axis_unit"] = self.params.get_value("x_unit")
        self.config["axis_label"] = self.params.get_value("x_label")
        self.config["xrange"] = np.arange(n_points) * self.params.get_value(
            "x_delta"
        ) + self.params.get_value("x0_offset")

    @staticmethod
    def get_parameter_config_widget() -> type["GenericPluginConfigWidget"]:
        """
        Get the parameter config widget class for the plugin.

        Returns
        -------
        type[GenericPluginConfigWidget]
            The config widget class.
        """
        return PluginConfigWidgetWithCustomXscale.resolve()  # type: ignore[type]
