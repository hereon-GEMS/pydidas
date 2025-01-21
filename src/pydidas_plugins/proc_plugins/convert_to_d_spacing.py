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
Module with the PyFAI2dIntegration Plugin which allows to integrate diffraction
patterns into a 2D radial/azimuthal map.
"""

__author__ = "Nonni Heere"
__copyright__ = "Copyright 2024 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["ConvertToDSpacing"]


import numpy as np

from pydidas.contexts import DiffractionExperimentContext
from pydidas.core import (
    Dataset,
    UserConfigError,
    get_generic_param_collection,
    get_generic_parameter,
)
from pydidas.core.constants import PROC_PLUGIN_INTEGRATED
from pydidas.plugins import ProcPlugin


class ConvertToDSpacing(ProcPlugin):
    """
    Convert Q, r or 2θ data from an integration plugin to d-spacing.

    NOTE: this plugin must be used immediately after an integration plugin
    to assert that the input data is in the correct format.
    """

    plugin_name = "Convert to d-spacing"
    plugin_subtype = PROC_PLUGIN_INTEGRATED

    default_params = get_generic_param_collection("d_spacing_unit")

    def __init__(self, *args, **kwargs):
        self._EXP = kwargs.pop("diffraction_exp", DiffractionExperimentContext())
        super().__init__(*args, **kwargs)

    def pre_execute(self):
        self._lambda = self._EXP.get_param_value("xray_wavelength")
        self._detector_dist = self._EXP.get_param_value("detector_dist")
        self._allowed_ax_choices = get_generic_parameter("rad_unit").choices
        self._config["ax_index"] = None
        self._config["new_range"] = None
        self._config["ax_indices"] = None
        self._config["unit"] = (
            "nm" if self.get_param_value("d_spacing_unit") == "nm" else "A"
        )

    def execute(self, data: Dataset, **kwargs: dict) -> tuple[Dataset, dict]:
        """
        Convert Q, r, or 2θ data from an integration plugin to d-spacing.

        Parameters:
            data : pydidas.core.Dataset
                The image / frame data.
            **kwargs : dict
                Any calling keyword arguments.

        Returns:
            data : pydidas.core.Dataset
                The converted data.
            kwargs : dict
                Any calling kwargs, appended by any changes in the function.
        """
        _new_data = data.copy()
        if self._config["ax_index"] is None:
            self._set_ax_index(data)
        if self._config["new_range"] is None:
            self._calculate_new_range(_new_data)
        _axis = self._config["ax_index"]
        _new_data.update_axis_unit(_axis, self._config["unit"])
        _new_data = _new_data[self._slicer]
        _new_data.update_axis_range(_axis, self._config["new_range"])
        _new_data.update_axis_label(_axis, "d-spacing")
        return _new_data, kwargs

    def _set_ax_index(self, data: Dataset):
        for axis, label in data.axis_labels.items():
            if f"{label} / {data.axis_units[axis]}" in self._allowed_ax_choices:
                self._config["ax_index"] = axis
                self._slicer = tuple(slice(None) for _ in range(axis))
                return
        raise UserConfigError(
            "Could not find a suitable axis to convert to d-spacing. "
            "Please check the input data.\n\n"
            "This plugin must be used immediately after an integration plugin "
            "to assert that the input data is in the correct format."
        )

    def _calculate_new_range(self, data: Dataset):
        """
        Calculate the new range for the d-spacing axis.

        Parameters
        ----------
        data : Dataset
            The input data.
        """
        _axis = self._config["ax_index"]
        _slicer = [slice(None)] * data.ndim
        _range = data.axis_ranges[_axis]
        match data.axis_labels[_axis]:
            case "Q":
                if data.axis_units[_axis] == "nm^-1":
                    _range = _range / 10
                _range = (2 * np.pi) / _range
            case "r":
                _range = self._lambda / (
                    2 * np.sin(np.arctan(_range / (self._detector_dist * 1e3)) / 2)
                )
            case "2theta":
                if data.axis_units[_axis] == "deg":
                    _range = np.radians(_range)
                _range = self._lambda / (2 * np.sin(_range / 2))
        if self.get_param_value("d_spacing_unit") == "nm":
            _range /= 10
        _valid = np.isfinite(_range)
        if not np.all(_valid):
            _range = _range[_valid]
        _slicer[_axis] = np.where(_valid)[0][::-1]
        self._config["new_range"] = _range[::-1]
        self._slicer = tuple(_slicer)
