# This file is part of pydidas.
#
# pydidas is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
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
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ["pyFAIintegrationBase", "pyFAI_UNITS", "pyFAI_METHOD"]

import os
import pathlib
import multiprocessing as mp

import numpy as np
from pyFAI.azimuthalIntegrator import AzimuthalIntegrator
from silx.opencl.common import OpenCL

from ..core.constants import PROC_PLUGIN, GREEK_ASCII_TO_UNI, PROC_PLUGIN_IMAGE
from ..core import get_generic_param_collection, UserConfigError
from ..core.utils import pydidas_logger, rebin2d
from ..data_io import import_data
from ..contexts import DiffractionExperimentContext
from .base_proc_plugin import ProcPlugin


logger = pydidas_logger()

EXP = DiffractionExperimentContext()

pyFAI_UNITS = {
    "Q / nm^-1": "q_nm^-1",
    "Q / A^-1": "q_A^-1",
    "2theta / deg": "2th_deg",
    "2theta / rad": "2th_rad",
    "r / mm": "r_mm",
    "chi / deg": "chi_deg",
    "chi / rad": "chi_rad",
}

pyFAI_METHOD = {
    "CSR": ("bbox", "csr", "cython"),
    "CSR OpenCL": ("bbox", "csr", "opencl"),
    "CSR full": ("full", "csr", "cython"),
    "CSR full OpenCL": ("full", "csr", "opencl"),
    "LUT": ("bbox", "lut", "cython"),
    "LUT OpenCL": ("bbox", "lut", "opencl"),
    "LUT full": ("full", "lut", "cython"),
    "LUT full OpenCL": ("full", "lut", "opencl"),
}

OCL = OpenCL()

PI_STR = GREEK_ASCII_TO_UNI["pi"]


class pyFAIintegrationBase(ProcPlugin):
    """
    Provide basic functionality for the concrete integration plugins.
    """

    plugin_name = "PyFAI integration base"
    basic_plugin = True
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
    )
    input_data_dim = 2
    output_data_label = "Integrated data"
    output_data_unit = "a.u."
    new_dataset = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._ai = None
        self._ai_params = {}
        self._exp_hash = -1
        self._mask = None

    def pre_execute(self):
        """
        Check and load the mask and set up the AzimuthalIntegrator.
        """
        self.load_and_set_mask()
        if self._exp_hash != hash(EXP):
            _lambda_in_A = EXP.get_param_value("xray_wavelength")
            self._ai = AzimuthalIntegrator(
                dist=EXP.get_param_value("detector_dist"),
                poni1=EXP.get_param_value("detector_poni1"),
                poni2=EXP.get_param_value("detector_poni2"),
                rot1=EXP.get_param_value("detector_rot1"),
                rot2=EXP.get_param_value("detector_rot2"),
                rot3=EXP.get_param_value("detector_rot3"),
                detector=EXP.get_detector(),
                wavelength=1e-10 * _lambda_in_A,
            )
        if self._mask is not None:
            self._ai.set_mask(self._mask)
        self._prepare_pyfai_method()

    def load_and_set_mask(self):
        """
        Load and store the mask.

        If defined (and the file exists), the locally defined detector mask
        Parameter will be used. If not, the global QSetting detector mask
        will be used.
        """
        self._mask = None
        _mask_file = EXP.get_param_value("detector_mask_file")
        if _mask_file != pathlib.Path():
            if os.path.isfile(_mask_file):
                self._mask = import_data(_mask_file)
            else:
                raise UserConfigError(
                    f"Cannot load detector mask: No file with the name \n{_mask_file}"
                    "\nexists."
                )
        if self._mask is not None and len(self._legacy_image_ops) > 0:
            _roi, _bin = self.get_single_ops_from_legacy()
            self._mask = np.where(rebin2d(self._mask[_roi], _bin) > 0, 1, 0)

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
        if "NVIDIA CUDA" in _platforms and _name.startswith("pydidas_worker-"):
            _index = int(_name.strip("pydidas_worker-"))
            _platform = OCL.get_platform("NVIDIA CUDA")
            _n_device = len(_platform.devices)
            _device = _index % _n_device
            _method = _method + ((_platform.id, _device),)
            self._config["method"] = _method

    def calculate_result_shape(self):
        """
        Get the shape of the integrated dataset to set up the CRS / LUT.

        Returns
        -------
        Union[int, tuple]
            The new shape. For 1-dimensional integration, a single integer is
            returned. For 2-dimensional integrations a tuple of two integers
            is returned.
        """
        raise NotImplementedError(
            "Must be implemented by the concrete pyFAI integration plugin"
        )

    def get_radial_range(self):
        """
        Get the radial range from the Parameters.

        If use_radial_range is True and both the lower and upper range limits
        are larger than zero, the  tuple with both values is returned.
        Otherwise, the return is None  which corresponds to pyFAI auto ranges.

        Returns
        -------
        Union[None, tuple]
            The radial range for the pyFAI integration.
        """
        if self.get_param_value("rad_use_range") == "Specify radial range":
            _lower = self.get_param_value("rad_range_lower")
            _upper = self.get_param_value("rad_range_upper")
            if 0 <= _lower < _upper:
                return (_lower, _upper)
            logger.warning(
                "Warning: Radial range was not correct and has been ignored."
            )
        return None

    def get_azimuthal_range_in_rad(self):
        """
        Get the azimuthal range from the Parameters in radians.

        If use_azimuthal_range is True and both the lower and upper range
        limits are larger than zero, the  tuple with both values is returned.
        Otherwise, the return is None  which corresponds to pyFAI auto ranges.

        Returns
        -------
        Union[None, tuple]
            The azimuthal range for the pyFAI integration.
        """
        _range = self.get_azimuthal_range_native()
        if _range is not None:
            if "deg" in self.get_param_value("azi_unit"):
                _range = (np.pi / 180 * _range[0], np.pi / 180 * _range[1])
            _range = self._modulate_range(_range)
            self._adjust_integration_discontinuity(self._ai, *_range)
        return _range

    def get_azimuthal_range_in_deg(self):
        """
        Get the azimuthal range from the Parameters in degree.

        If use_azimuthal_range is True and both the lower and upper range
        limits are larger than zero, the  tuple with both values is returned.
        Otherwise, the return is None  which corresponds to pyFAI auto ranges.

        Returns
        -------
        Union[None, tuple]
            The azimuthal range for the pyFAI integration.
        """
        _range = self.get_azimuthal_range_native()
        if _range is not None:
            if "rad" in self.get_param_value("azi_unit"):
                _range = (180 / np.pi * _range[0], 180 / np.pi * _range[1])
            _range = self._modulate_range(_range, np.pi / 180)
            self._adjust_integration_discontinuity(
                self._ai, np.pi / 180 * _range[0], np.pi / 180 * _range[1]
            )
        return _range

    def get_azimuthal_range_native(self):
        """
        Get the azimuthal range from the Parameters in native units.

        If use_azimuthal_range is True and both the lower and upper range
        limits are larger than zero, the  tuple with both values is returned.
        Otherwise, the return is None  which corresponds to pyFAI auto ranges.

        Returns
        -------
        Union[None, tuple]
            The azimuthal range for the pyFAI integration.
        """
        if self.get_param_value("azi_use_range") == "Specify azimuthal range":
            _lower = self.get_param_value("azi_range_lower")
            _upper = self.get_param_value("azi_range_upper")
            if _lower < _upper:
                return (_lower, _upper)
            if _lower > _upper:
                return (_upper, _lower)
        return None

    @staticmethod
    def _adjust_integration_discontinuity(ai, *azi_range):
        """
        Check the position of the integration discontinuity and adjust it according
        to the integration bounds.

        Parameters
        ----------
        ai : pyFAI.AzimuthalIntegrator
            The azimuthal integrator instance.
        azi_range : tuple
            The integration range in rad.
        """
        _low = azi_range[0]
        _high = azi_range[1]
        if _high - _low > 2 * np.pi:
            raise UserConfigError(
                "The integration range is larger than a full circle! "
                "Please adjust the boundaries and try again."
            )
        if _low >= 0:
            if ai.chiDiscAtPi:
                ai.reset()
            ai.setChiDiscAtZero()
        elif _low < 0 and _high <= np.pi:
            if not ai.chiDiscAtPi:
                ai.reset()
            ai.setChiDiscAtPi()
        else:
            _low = np.round(_low, 5)
            _high = np.round(_high, 5)
            raise UserConfigError(
                f"The chosen integration range ({_low}, {_high}) cannot be processed "
                "because it cannot be represented in pyFAI. The range must be either "
                f"in the interval [-{PI_STR}, {PI_STR}] or [0, 2*{PI_STR}]."
            )

    @staticmethod
    def _modulate_range(azi_range, scale_factor=1):
        """
        Modulate the range to the range [-180, 360] degree.

        Parameters
        ----------
        azi_range : tuple
            The azimuthal range.
        scale_factor : float, optional
            The scale factor to convert degrees to radians. Ranges in radians must use
            1, ranges in degrees must use pi/180. The default is 1.

        Returns
        -------
        azi_range : tuple
            The updated range.
        """
        _low = azi_range[0] * scale_factor
        _high = azi_range[1] * scale_factor
        if _high > 2 * np.pi:
            _low = np.mod(_low, 2 * np.pi)
            _high = np.mod(_high, 2 * np.pi)
            if _low > _high:
                _low -= 2 * np.pi
        if _low < -np.pi:
            _low = np.mod(_low + np.pi, 2 * np.pi) - np.pi
            _high = np.mod(_high + np.pi, 2 * np.pi) - np.pi
        return (np.round(_low / scale_factor, 6), np.round(_high / scale_factor, 6))

    def get_pyFAI_unit_from_param(self, param_name):
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

    def execute(self, data, **kwargs):
        """
        To be implemented by the concrete subclass.
        """
        raise NotImplementedError
