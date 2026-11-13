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
Module with the PyFAIazimuthalSectorIntegration Plugin which allows to integrate over
several azimuthal sectors at once.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2026, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["PyFAIazimuthalSectorIntegration"]


from typing import Any

import numpy as np

from pydidas.core import (
    Dataset,
    Parameter,
    UserConfigError,
    get_generic_param_collection,
)
from pydidas.core.lazy_imports.pyFAI import AzimuthalIntegrator
from pydidas.plugins import pyFAIintegrationBase


SECTOR_CENTER_PARAM = Parameter(
    "azi_sector_centers",
    str,
    "0; 90; 180; 270",
    name="Azimuthal sector centers",
    unit="",
    tooltip=(
        "The centers of the azimuthal sectors to be integrated (in azimuthal "
        "units). Separate multiple sectors by semicolons."
    ),
)
SECTOR_WIDTH_PARAM = Parameter(
    "azi_sector_width",
    float,
    20,
    name="Azimuthal sector width",
    unit="",
    tooltip="The width of each azimuthal sector (in azimuthal units).",
)

_SECTOR_INT_PLUGIN_PARAMS = pyFAIintegrationBase.default_params.copy()
_SECTOR_INT_PLUGIN_PARAMS.pop("azi_use_range")
_SECTOR_INT_PLUGIN_PARAMS.pop("azi_range_lower")
_SECTOR_INT_PLUGIN_PARAMS.pop("azi_range_upper")
_SECTOR_INT_PLUGIN_PARAMS.pop("azi_npoint")
_SECTOR_INT_PLUGIN_PARAMS.update(
    get_generic_param_collection(
        "azi_sector_centers",
        "azi_sector_width",
    )
)


class PyFAIazimuthalSectorIntegration(pyFAIintegrationBase):
    """
    Integrate images azimuthally to get radial profiles for multiple sectors.

    Note: This plugin is intended for arbitrary, asymmetric integration
    ranges. For repetitive ranges (e.g. 0, 90, 180, 270 degree), it is
    faster to use the pyFAI2dIntegration and the ExtractAzimuthalSectors
    plugin.

    Sector centers, widths and output azimuthal coordinates use the selected
    azi_unit. Integration bounds passed to pyFAI are converted to degrees.

    For a full documentation of the Plugin, please refer to the pyFAI
    documentation.
    """

    plugin_name = "pyFAI azimuthal sector integration"

    default_params = _SECTOR_INT_PLUGIN_PARAMS
    output_data_dim = 2

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._ais = []
        self._dataset_info = {}

    def pre_execute(self) -> None:
        """Pre-execute the plugin and set up the AzimuthalIntegrator."""
        self._eval_sectors()
        if self._exp_hash != hash(self._exp) or len(self._ais) != len(
            self.config["sector_centers"]
        ):
            _lambda_in_A = self._exp.get_param_value("xray_wavelength")
            self._ais = [
                AzimuthalIntegrator(
                    dist=self._exp.get_param_value("detector_dist"),
                    poni1=self._exp.get_param_value("detector_poni1"),
                    poni2=self._exp.get_param_value("detector_poni2"),
                    rot1=self._exp.get_param_value("detector_rot1"),
                    rot2=self._exp.get_param_value("detector_rot2"),
                    rot3=self._exp.get_param_value("detector_rot3"),
                    detector=self._exp.get_detector(),
                    wavelength=1e-10 * _lambda_in_A,
                )
                for _ in self.config["sector_centers"]
            ]
            self._ai = self._ais[0]
            self._store_intrinsic_masks()
            self._exp_hash = hash(self._exp)
        self.load_and_set_mask()
        self._restore_default_masks()
        self._prepare_pyfai_method()
        self._ai_params = {
            "unit": self.get_pyFAI_unit_from_param("rad_unit"),
            "radial_range": self.get_radial_range(),
            "polarization_factor": self.get_param_value("polarization_factor"),
            "correctSolidAngle": self.get_param_value("correct_solid_angle"),
            "method": self.config["method"],
        }
        _label, _unit = self.params["rad_unit"].value.split("/")
        _azi_unit = self.params["azi_unit"].value.split("/")[1]
        self._dataset_info = {
            "axis_labels": ["chi", _label.strip()],
            "axis_units": [_azi_unit.strip(), _unit.strip()],
            "data_label": "integrated intensity",
            "data_unit": "counts",
        }

    def _eval_sectors(self) -> None:
        """
        Evaluate the user input for the sectors.

        Raises
        ------
        UserConfigError
            When the sector entries could not be converted correctly.
        """
        _delta = self.get_param_value("azi_sector_width") / 2
        _sector_entries = self.get_param_value("azi_sector_centers")
        try:
            _sectors = [float(_entry) for _entry in _sector_entries.split(";")]
        except ValueError:
            raise UserConfigError(
                "Could not convert the azimuthal sectors to numbers: \n"
                + _sector_entries
            )
        self.config["sector_centers"] = tuple(_sectors)
        _centers = np.array(self.config["sector_centers"])
        _ranges = np.column_stack((_centers - _delta, _centers + _delta))
        if "rad" in self.get_param_value("azi_unit"):
            # PyFAI expects azimuthal ranges in degrees, so convert to
            # degrees if radian unit is used:
            _ranges = np.rad2deg(_ranges)
        self.config["sector_ranges"] = tuple(tuple(_range) for _range in _ranges)

    def execute(
        self, data: Dataset | np.ndarray, **kwargs: Any
    ) -> tuple[Dataset, dict[str, Any]]:
        """
        Run the azimuthal integration on the input data.

        Parameters
        ----------
        data : Dataset or np.ndarray
            The input image / frame data.
        **kwargs : Any
            The input kwargs used for processing.

        Returns
        -------
        dataset : Dataset
            The integrated data.
        kwargs : dict[str, Any]
            The input kwargs used for processing,
            appended by any changes in the function.
        """
        self.check_and_set_custom_mask(**kwargs)
        _image = data.array if isinstance(data, Dataset) else data
        _results = [
            _ai.integrate1d(
                _image,
                self.get_param_value("rad_npoint"),
                azimuth_range=self.config["sector_ranges"][_index],
                **self._ai_params,
            )
            for _index, _ai in enumerate(self._ais)
        ]
        _new_data = np.asarray([_res.intensity for _res in _results])
        _axranges = [self.config["sector_centers"], _results[0].radial]
        _dataset = Dataset(_new_data, axis_ranges=_axranges, **self._dataset_info)
        return _dataset, kwargs
