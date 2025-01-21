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
Module with the PyFAIazimuthalSectorIntegration Plugin which allows to integrate over
several azimuthal sectors at once.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["PyFAIazimuthalSectorIntegration"]


import numpy as np
from pyFAI.azimuthalIntegrator import AzimuthalIntegrator

from pydidas.contexts import DiffractionExperimentContext
from pydidas.core import (
    Dataset,
    Parameter,
    UserConfigError,
    get_generic_param_collection,
)
from pydidas.plugins import pyFAIintegrationBase


EXP = DiffractionExperimentContext()

SECTOR_CENTER_PARAM = Parameter(
    "azi_sector_centers",
    str,
    "0; 90; 180; 270",
    name="Azimuthal sector centers",
    unit="deg",
    tooltip=(
        "The centers of the azimuthal sectors to be integrated (in degree). Separate "
        "multiple sectors by semicolons."
    ),
)
SECTOR_WIDTH_PARAM = Parameter(
    "azi_sector_width",
    float,
    20,
    name="Azimuthal sector width",
    unit="deg",
    tooltip="The width of each azimuthal sector (in degree).",
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
    Integrate images radially to get multiple azimuthal profiles using pyFAI.

    Note: This plugin is intended for arbitrary, asymmetric integration ranges. For
    repetitive ranges (e.g. 0, 90, 180, 270 degree), it is faster to use the
    pyFAI2dIntegration and the ExtractAzimuthalSectors plugin.

    For a full documentation of the Plugin, please refer to the pyFAI
    documentation.
    """

    plugin_name = "pyFAI azimuthal sector integration"

    default_params = _SECTOR_INT_PLUGIN_PARAMS
    output_data_dim = 2

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._ais = []
        self._dataset_info = {}

    def pre_execute(self):
        """
        Pre-execute the plugin and store the Parameters required for the execution.
        """
        self._eval_sectors()
        if self._exp_hash != hash(EXP):
            _lambda_in_A = EXP.get_param_value("xray_wavelength")
            self._ais = [
                AzimuthalIntegrator(
                    dist=EXP.get_param_value("detector_dist"),
                    poni1=EXP.get_param_value("detector_poni1"),
                    poni2=EXP.get_param_value("detector_poni2"),
                    rot1=EXP.get_param_value("detector_rot1"),
                    rot2=EXP.get_param_value("detector_rot2"),
                    rot3=EXP.get_param_value("detector_rot3"),
                    detector=EXP.get_detector(),
                    wavelength=1e-10 * _lambda_in_A,
                )
                for _, _ in enumerate(self._config["sector_centers"])
            ]
            self._ai = self._ais[0]
        self.load_and_set_mask()
        if self._mask is not None:
            for _ai in self._ais:
                _ai.set_mask(self._mask)
        self._prepare_pyfai_method()
        self._ai_params = {
            "unit": self.get_pyFAI_unit_from_param("rad_unit"),
            "radial_range": self.get_radial_range(),
            "polarization_factor": self.get_param_value("polarization_factor"),
            "correctSolidAngle": self.get_param_value("correct_solid_angle"),
            "method": self._config["method"],
        }
        _label, _unit = self.params["rad_unit"].value.split("/")
        _azi_unit = self.params["azi_unit"].value.split("/")[1]
        self._dataset_info = {
            "axis_labels": ["chi", _label.strip()],
            "axis_units": [_azi_unit.strip(), _unit.strip()],
            "data_label": "integrated intensity",
            "data_unit": "counts",
        }

    def _eval_sectors(self):
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
        self._config["sector_centers"] = tuple(_sectors)
        self._config["sector_ranges"] = tuple(
            zip(np.array(_sectors) - _delta, np.array(_sectors) + _delta)
        )

    def execute(self, data: Dataset, **kwargs: dict) -> tuple[Dataset, dict]:
        """
        Run the azimuthal integration on the input data.

        Parameters
        ----------
        data : Dataset
            The radial integration data for the given sectors.
        kwargs : dict
            The input kwargs used for processing.

        Returns
        -------
        _dataset : Dataset
            The integrated data.
        kwargs : dict
            The input kwargs used for processing,
            appended by any changes in the function.
        """
        self.check_and_set_custom_mask(**kwargs)
        _results = [
            _ai.integrate1d(
                data,
                self.get_param_value("rad_npoint"),
                azimuth_range=self._config["sector_ranges"][_index],
                **self._ai_params,
            )
            for _index, _ai in enumerate(self._ais)
        ]
        _newdata = np.asarray([_res[1] for _res in _results])
        _axranges = [self._config["sector_centers"], _results[0][0]]
        _dataset = Dataset(_newdata, axis_ranges=_axranges, **self._dataset_info)
        return _dataset, kwargs
