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
)
from pydidas.core.constants import PROC_PLUGIN_INTEGRATED
from pydidas.core.generic_params import GENERIC_PARAMS_METADATA
from pydidas.core.utils.scattering_geometry import convert_polar_to_d_spacing
from pydidas.plugins import ProcPlugin


_AX_CHOICES = ["d-spacing / nm", "d-spacing / A"] + GENERIC_PARAMS_METADATA["rad_unit"][
    "choices"
]


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
        self._allowed_ax_choices = _AX_CHOICES

    def pre_execute(self):
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

        This method calculates the new range for the d-spacing axis
        by converting it to Angstrom by default and then applying
        a factor if necessary.

        Parameters
        ----------
        data : Dataset
            The input data.
        """
        _axis = self._config["ax_index"]
        _slicer = [slice(None)] * data.ndim
        _range = data.axis_ranges[_axis].copy()
        _label_in = data.axis_labels[_axis]
        _unit_in = data.axis_units[_axis]
        _unit_out = self.get_param_value("d_spacing_unit")

        if _label_in == "d-spacing":
            if _unit_in == "nm" and _unit_out in ["A", "Angstrom"]:
                _range *= 10
            elif _unit_in == "A" and _unit_out == "nm":
                _range /= 10
            self._config["new_range"] = _range
        else:
            _range = convert_polar_to_d_spacing(
                _range,
                f"{_label_in} / {_unit_in}",
                _unit_out,
                self._EXP.xray_wavelength_in_m,
                self._EXP.detector_dist_in_m,
            )
            _valid = np.isfinite(_range)
            if not np.all(_valid):
                _range = _range[_valid]
            _slicer[_axis] = np.where(_valid)[0][::-1]
            self._config["new_range"] = _range[::-1]
        self._slicer = tuple(_slicer)
