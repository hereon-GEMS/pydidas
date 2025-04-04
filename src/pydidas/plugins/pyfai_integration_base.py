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
Module with the pyFAIintegrationBase Plugin which is inherited by all
integration plugins using pyFAI.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["pyFAIintegrationBase"]


import multiprocessing as mp
import os
import pathlib
from typing import Literal

import numpy as np
from pyFAI.azimuthalIntegrator import AzimuthalIntegrator
from qtpy import QtWidgets
from silx.opencl.common import OpenCL

from pydidas.contexts import DiffractionExperimentContext
from pydidas.core import UserConfigError, get_generic_param_collection
from pydidas.core.constants import (
    ASCII_TO_UNI,
    PROC_PLUGIN,
    PROC_PLUGIN_IMAGE,
    pyFAI_METHOD,
    pyFAI_UNITS,
)
from pydidas.core.utils import pydidas_logger
from pydidas.core.utils.scattering_geometry import convert_radial_value
from pydidas.data_io import import_data
from pydidas.plugins.base_proc_plugin import ProcPlugin


logger = pydidas_logger()


OCL = OpenCL()

PI_STR = ASCII_TO_UNI["pi"]


class pyFAIintegrationBase(ProcPlugin):
    """
    Provide basic functionality for the concrete integration plugins.
    """

    plugin_name = "PyFAI integration base"
    plugin_type = PROC_PLUGIN
    plugin_subtype = PROC_PLUGIN_IMAGE
    default_params = get_generic_param_collection(
        "rad_npoint",
        "rad_unit",
        "rad_use_range",
        "rad_range_lower",
        "rad_range_upper",
        "azi_npoint",
        "azi_unit",
        "azi_use_range",
        "azi_range_lower",
        "azi_range_upper",
        "int_method",
        "correct_solid_angle",
        "polarization_factor",
    )
    input_data_dim = 2
    output_data_label = "Integrated data"
    output_data_unit = "a.u."
    new_dataset = True
    has_unique_parameter_config_widget = True
    advanced_parameters = ["correct_solid_angle", "polarization_factor"]

    def __init__(self, *args: tuple, **kwargs: dict):
        self._EXP = kwargs.pop("diffraction_exp", DiffractionExperimentContext())
        super().__init__(*args, **kwargs)
        self._ai = None
        self._ai_params = {}
        self._exp_hash = -1
        self._mask = None
        self._config["custom_mask"] = False

    def pre_execute(self):
        """
        Check and load the mask and set up the AzimuthalIntegrator.
        """
        if self._exp_hash != hash(self._EXP):
            _lambda_in_A = self._EXP.get_param_value("xray_wavelength")
            self._ai = AzimuthalIntegrator(
                dist=self._EXP.get_param_value("detector_dist"),
                poni1=self._EXP.get_param_value("detector_poni1"),
                poni2=self._EXP.get_param_value("detector_poni2"),
                rot1=self._EXP.get_param_value("detector_rot1"),
                rot2=self._EXP.get_param_value("detector_rot2"),
                rot3=self._EXP.get_param_value("detector_rot3"),
                detector=self._EXP.get_detector(),
                wavelength=1e-10 * _lambda_in_A,
            )
            self._exp_hash = hash(self._EXP)
        self.load_and_set_mask()
        if self._mask is not None:
            self._ai.set_mask(self._mask)
        self._adjust_integration_discontinuity()
        self._prepare_pyfai_method()

    def load_and_set_mask(self):
        """
        Load and store the mask.

        If defined (and the file exists), the locally defined detector mask
        Parameter will be used. If not, the global QSetting detector mask
        will be used.
        """
        self._mask = None
        _mask_file = self._EXP.get_param_value("detector_mask_file")
        if _mask_file != pathlib.Path():
            if os.path.isfile(_mask_file):
                self._mask = import_data(_mask_file)
            else:
                raise UserConfigError(
                    f"Cannot load detector mask: No file with the name \n{_mask_file}"
                    "\nexists."
                )
            self._check_mask_shape()

    def _prepare_pyfai_method(self):
        """
        Prepare the method name and select OpenCL device if multiple devices
        present.
        """
        _method = pyFAI_METHOD[self.get_param_value("int_method")]
        self._config["method"] = _method
        if _method[2] != "opencl":
            return
        _name = mp.current_process().name
        _platforms = [_platform.name for _platform in OCL.platforms]
        if "NVIDIA CUDA" in _platforms and _name.startswith("pydidas_"):
            _index = int(_name.split("-")[1])
            _platform = OCL.get_platform("NVIDIA CUDA")
            _n_device = len(_platform.devices)
            _device = _index % _n_device
            _method = _method + ((_platform.id, _device),)
            self._config["method"] = _method

    def get_azimuthal_range_in_rad(self) -> None | tuple[float, float]:
        """
        Get the azimuthal range from the Parameters in radians.

        If use_azimuthal_range is True and both the lower and upper range
        limits are larger than zero, the tuple with both values is returned.
        Otherwise, the return is None which corresponds to pyFAI auto ranges.

        Returns
        -------
        None | tuple[float, float]
            The azimuthal range for the pyFAI integration in radian.
        """
        _range = self.get_azimuthal_range_native()
        if _range is not None:
            if "deg" in self.get_param_value("azi_unit"):
                _range = (np.pi / 180 * _range[0], np.pi / 180 * _range[1])
        return _range

    def get_azimuthal_range_in_deg(self) -> None | tuple[float, float]:
        """
        Get the azimuthal range from the Parameters in degree.

        If use_azimuthal_range is True and both the lower and upper range
        limits are larger than zero, the tuple with both values is returned.
        Otherwise, the return is None which corresponds to pyFAI auto ranges.

        Returns
        -------
        None | tuple[float, float]
            The azimuthal range for the pyFAI integration in degrees.
        """
        _range = self.get_azimuthal_range_native()
        if _range is not None:
            if "rad" in self.get_param_value("azi_unit"):
                _range = (180 / np.pi * _range[0], 180 / np.pi * _range[1])
        return _range

    def get_azimuthal_range_native(self) -> tuple[float, float]:
        """
        Get the azimuthal range from the Parameters in native units.

        If use_azimuthal_range is True and both the lower and upper range
        limits are larger than zero, the tuple with both values is returned.
        Otherwise, the return is the full circle which encompasses (-180, 180)
        if the integration discontinuity is located at pi, and (0, 360) otherwise.

        Returns
        -------
        tuple[float, float]
            The azimuthal range for the pyFAI integration.
        """
        _value = np.pi if "rad" in self.get_param_value("azi_unit", "deg") else 180

        if self._ai is None:
            _default = (-_value, _value)
        else:
            _default = (-_value, _value) if self._ai.chiDiscAtPi else (0, 2 * _value)
        if self.get_param_value("azi_use_range", False) == "Specify azimuthal range":
            self.modulate_and_store_azi_range()
            _low = self.get_param_value("azi_range_lower")
            _high = self.get_param_value("azi_range_upper")
            if _low < _high:
                return (
                    self.get_param_value("azi_range_lower"),
                    self.get_param_value("azi_range_upper"),
                )
        return _default

    def _adjust_integration_discontinuity(self):
        """Check and adjust the position of the integration discontinuity."""
        _range = self.get_azimuthal_range_in_rad()
        if _range is None:
            return
        _low, _high = _range
        if _high - _low > 2 * np.pi:
            raise UserConfigError(
                "The integration range is larger than a full circle! "
                "Please adjust the boundaries and try again."
            )
        if _low >= 0:
            if self._ai.chiDiscAtPi:
                self._ai.reset()
            self._ai.setChiDiscAtZero()
        elif _low < 0 and _high <= np.pi:
            if not self._ai.chiDiscAtPi:
                self._ai.reset()
            self._ai.setChiDiscAtPi()
        else:
            self._raise_range_error(_low, _high)

    def modulate_and_store_azi_range(self):
        """Try to modulate the azimuthal range to be compatible with pyFAI."""
        _factor = 1 if "rad" in self.get_param_value("azi_unit") else np.pi / 180
        _lower = _factor * self.get_param_value("azi_range_lower")
        _upper = _factor * self.get_param_value("azi_range_upper")
        if _upper - _lower > 2 * np.pi:
            _lower += 2 * np.pi
        if _upper > 2 * np.pi:
            _lower = np.mod(_lower, 2 * np.pi)
            _upper = np.mod(_upper, 2 * np.pi)
        if _lower > _upper:
            _lower -= 2 * np.pi
        if _lower < -np.pi:
            _lower = np.mod(_lower + np.pi, 2 * np.pi) - np.pi
            _upper = np.mod(_upper + np.pi, 2 * np.pi) - np.pi
        if (
            (_lower < 0 and _upper >= np.pi)
            or _lower > _upper
            or (_upper - _lower > 2 * np.pi)
        ):
            self._raise_range_error(_lower, _upper)
        self.set_param_value("azi_range_lower", _lower / _factor)
        self.set_param_value("azi_range_upper", _upper / _factor)

    def _raise_range_error(self, low: float, high: float):
        """
        Raise a UserConfigError that the specified bounds are invalid.

        Parameters
        ----------
        low : float
            The lower bound.
        high : float
            The upper bound.
        """
        _intervals = (
            f"[-{PI_STR}, {PI_STR}] or [0, 2*{PI_STR}]"
            if "rad" in self.get_param_value("azi_unit")
            else "[-180\u00b0, 180\u00b0] or [0\u00b0, 360\u00b0]"
        )
        low = np.round(low, 5)
        high = np.round(high, 5)
        raise UserConfigError(
            f"The chosen integration range ({low}, {high}) cannot be processed "
            "because it cannot be represented in pyFAI. The range must be either "
            f"in the interval {_intervals}."
        )

    def is_range_valid(self) -> bool:
        """
        Check whether the plugin's range is valid.

        Parameters
        ----------
        azi_range : tuple
            The azimuthal range.

        Returns
        -------
        bool
            Flag whether the range is valid or not.
        """
        try:
            self.modulate_and_store_azi_range()
        except UserConfigError:
            return False
        _range = self.get_azimuthal_range_in_rad()
        if _range is None:
            return True
        _low, _high = _range
        if _low > _high:
            _low = np.mod(_low + np.pi, 2 * np.pi) - np.pi
            _high = np.mod(_high + np.pi, 2 * np.pi) - np.pi
        if -np.pi <= _low < 0:
            return _low < _high <= np.pi + 1e-7
        return 0 <= _low <= _high <= 2 * np.pi + 1e-7

    def get_pyFAI_unit_from_param(self, param_name: str) -> str:
        """
        Get the unit of the Parameter called param_name in pyFAI notation.

        Parameters
        ----------
        param_name : str
            The reference key of the Parameter with the unit.

        Returns
        -------
        str
            The unit in pyFAI notation.
        """
        return pyFAI_UNITS[self.get_param_value(param_name)]

    def check_and_set_custom_mask(self, **kwargs: dict):
        """
        Check the kwargs for a custom mask and set it, if available.

        Parameters
        ----------
        **kwargs : dict
            Any keyword arguments.
        """
        _mask = kwargs.get("custom_mask", None)
        if _mask is not None:
            self._config["custom_mask"] = True
        elif _mask is None and self._mask is not None and self._config["custom_mask"]:
            _mask = self._mask
            self._config["custom_mask"] = False
        else:
            return
        if hasattr(self, "_ai"):
            self._ai.set_mask(_mask)
        if hasattr(self, "_ais"):
            for _ai in self._ais:
                _ai.set_mask(_mask)

    def _check_mask_shape(self, mask: np.ndarray | None = None):
        """
        Compare the shape of the mask and the AzimuthalIntegrator's detector.

        Parameters
        ----------
        mask : ndarray, optional
            The custom mask to be checked. If None, the stored default mask is used.
        """
        if self._ai is None:
            return
        _mask_shape = mask.shape if mask is not None else self._mask.shape
        if _mask_shape != self._ai.detector.max_shape:
            raise UserConfigError(
                "The shape of the mask does not match the shape of the data.\n"
                f"Experimental geometry shape: {self._ai.detector.max_shape}\n"
                f"Mask shape: {_mask_shape}."
            )

    def execute(self, data: np.ndarray, **kwargs: dict):
        """To be implemented by the concrete subclass."""
        raise NotImplementedError

    def get_parameter_config_widget(self) -> QtWidgets.QWidget:
        """
        Get the unique configuration widget associated with this Plugin.

        Returns
        -------
        QtWidgets.QWidget
            The unique ParameterConfig widget
        """
        from pydidas.widgets.plugin_config_widgets import PyfaiIntegrationConfigWidget

        return PyfaiIntegrationConfigWidget

    def get_radial_range(self) -> None | tuple[float, float]:
        """
        Get the radial range from the Parameters.

        If use_radial_range is True and both the lower and upper range limits
        are larger than zero, the tuple with both values is returned.
        Otherwise, the return is None which corresponds to pyFAI auto ranges.

        Returns
        -------
        None | tuple[float, float]
            The radial range for the pyFAI integration.
        """
        if self.get_param_value("rad_use_range", False) == "Specify radial range":
            _lower = self.get_param_value("rad_range_lower")
            _upper = self.get_param_value("rad_range_upper")
            if 0 <= _lower < _upper:
                return (_lower, _upper)
            logger.warning(
                "Warning: Radial range was not correct and has been ignored."
            )
        return None

    def get_radial_range_in_units(self, unit: str) -> None | tuple[float, float]:
        """
        Get the radial range converted to the given unit.

        Parameters
        ----------
        unit : str
            The new unit of the range.
        """
        _range = self.get_radial_range()
        if _range is None:
            return None
        _range = convert_radial_value(
            np.asarray(_range),
            self.get_param_value("rad_unit"),
            unit,
            self._EXP.xray_wavelength_in_m,
            self._EXP.det_dist_in_m,
        )
        return tuple(_range)

    def convert_radial_range_values(
        self,
        from_unit: Literal[
            "2theta / deg", "2theta / rad", "Q / A^-1", "Q / nm^-1", "r / mm"
        ],
        to_unit: Literal[
            "2theta / deg", "2theta / rad", "Q / A^-1", "Q / nm^-1", "r / mm"
        ],
    ):
        """
        Convert and store the radial range values from the given unit to the given unit.

        Parameters
        ----------
        from_unit : Literal["2theta / deg", "2theta / rad", "Q / A^-1", "Q / nm^-1", "r / mm"]
            The previous unit.
        to_unit : Literal["2theta / deg", "2theta / rad", "Q / A^-1", "Q / nm^-1", "r / mm"]
            The new unit.
        """
        _range = self.get_radial_range()
        if from_unit == to_unit or _range is None:
            return
        _range = convert_radial_value(
            np.asarray(_range),
            from_unit,
            to_unit,
            self._EXP.xray_wavelength_in_m,
            self._EXP.det_dist_in_m,
        )
        self.set_param_value("rad_range_lower", _range[0])
        self.set_param_value("rad_range_upper", _range[1])


pyFAIintegrationBase.register_as_base_class()
