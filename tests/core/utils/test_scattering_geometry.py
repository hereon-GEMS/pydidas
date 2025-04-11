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

"""Unit tests for pydidas modules."""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"


import numpy as np
import pytest

import pydidas
from pydidas.core import UserConfigError
from pydidas.core.utils.scattering_geometry import (
    convert_d_spacing_to_2theta,
    convert_polar_to_d_spacing,
    convert_polar_value,
    q_to_2theta,
)


_EXP = pydidas.contexts.DiffractionExperimentContext()

_LAMBDA_in_A = 1.0
_DET_DIST_in_m = 0.421
_RANGE_2THETA_RAD = np.linspace(0.035, 0.733, 4)
_RANGES = {
    "2theta_deg": np.rad2deg(_RANGE_2THETA_RAD),
    "2theta_rad": _RANGE_2THETA_RAD,
    "d-spacing_nm": (0.1 * _LAMBDA_in_A) / (2 * np.sin(_RANGE_2THETA_RAD / 2)),
    "d-spacing_A": _LAMBDA_in_A / (2 * np.sin(_RANGE_2THETA_RAD / 2)),
    "Q_nm^-1": (4 * np.pi) / (0.1 * _LAMBDA_in_A) * np.sin(_RANGE_2THETA_RAD / 2),
    "Q_A^-1": (4 * np.pi) / _LAMBDA_in_A * (np.sin(_RANGE_2THETA_RAD / 2)),
    "r_mm": (_DET_DIST_in_m * 1000) * np.tan(_RANGE_2THETA_RAD),
}
_FORMATTED_ALLOWED_POLAR_TYPES = [
    "2theta / deg",
    "2theta_deg",
    "2theta / rad",
    "2theta_rad",
    "Q / nm^-1",
    "Q_nm^-1",
    "Q / A^-1",
    "Q_A^-1",
    "r / mm",
    "r_mm",
]


@pytest.fixture()
def prepare_exp():
    _EXP.restore_all_defaults(True)
    _EXP.set_param_value("xray_wavelength", _LAMBDA_in_A)
    _EXP.set_param_value("detector_dist", _DET_DIST_in_m)


@pytest.mark.parametrize("q", ["Q_A^-1", "Q_nm^-1", "Q / A^-1", "Q / nm^-1", None])
def test_q_to_2theta(prepare_exp, q):
    if q is None:
        _range = _RANGES["Q_A^-1"] * 1e10
    else:
        _range = _RANGES[q.replace(" / ", "_")]
    _2theta = q_to_2theta(_range, _EXP.xray_wavelength_in_m, q_unit=q)
    assert np.allclose(_2theta, _RANGE_2THETA_RAD, rtol=1e-5)


def test_q_to_2theta_invalid_unit(prepare_exp):
    with pytest.raises(UserConfigError):
        q_to_2theta(_RANGES["Q_A^-1"], _EXP.xray_wavelength_in_m, q_unit="invalid_unit")


@pytest.mark.parametrize("type_in", _FORMATTED_ALLOWED_POLAR_TYPES)
@pytest.mark.parametrize("type_out", _FORMATTED_ALLOWED_POLAR_TYPES)
def test_convert_radial_value(prepare_exp, type_in, type_out):
    _in_range = _RANGES[type_in.replace(" / ", "_")]
    _ref_range = _RANGES[type_out.replace(" / ", "_")]
    _out_range = convert_polar_value(
        _in_range, type_in, type_out, _EXP.xray_wavelength_in_m, _EXP.detector_dist_in_m
    )
    assert np.allclose(_out_range, _ref_range, rtol=1e-5)


def test_convert_radial_value_invalid_input_unit(prepare_exp):
    _in_range = _RANGES["Q_A^-1"]
    with pytest.raises(UserConfigError):
        convert_polar_value(
            _in_range,
            "invalid_unit",
            "Q_A^-1",
            _EXP.xray_wavelength_in_m,
            _EXP.detector_dist_in_m,
        )


def test_convert_radial_value_invalid_output_unit(prepare_exp):
    _in_range = _RANGES["Q_A^-1"]
    with pytest.raises(UserConfigError):
        convert_polar_value(
            _in_range,
            "Q_A^-1",
            "invalid_unit",
            _EXP.xray_wavelength_in_m,
            _EXP.detector_dist_in_m,
        )


@pytest.mark.parametrize("unit_in", ["nm", "A"])
@pytest.mark.parametrize("unit_out", ["deg", "rad"])
def test_convert_dspacing_to_2theta(prepare_exp, unit_in, unit_out):
    _in_range = _RANGES[f"d-spacing_{unit_in}"]
    _ref_range = _RANGES[f"2theta_{unit_out}"]
    _out_range = convert_d_spacing_to_2theta(
        _in_range, unit_in, unit_out, _EXP.xray_wavelength_in_m
    )
    assert np.allclose(_out_range, _ref_range, rtol=1e-5)


def test_convert_dspacing_to_2theta_invalid_input_unit(prepare_exp):
    _in_range = _RANGES["d-spacing_A"]
    with pytest.raises(UserConfigError):
        convert_d_spacing_to_2theta(
            _in_range, "invalid_unit", "deg", _EXP.xray_wavelength_in_m
        )


def test_convert_dspacing_to_2theta_invalid_output_unit(prepare_exp):
    _in_range = _RANGES["d-spacing_A"]
    with pytest.raises(UserConfigError):
        convert_d_spacing_to_2theta(
            _in_range, "A", "invalid_unit", _EXP.xray_wavelength_in_m
        )


@pytest.mark.parametrize("type_in", _FORMATTED_ALLOWED_POLAR_TYPES)
@pytest.mark.parametrize("unit_out", ["nm", "A"])
def test_convert_polar_to_dspacing(prepare_exp, type_in, unit_out):
    _in_range = _RANGES[type_in.replace(" / ", "_")]
    _ref_range = _RANGES[f"d-spacing_{unit_out}"]
    _out_range = convert_polar_to_d_spacing(
        _in_range, type_in, unit_out, _EXP.xray_wavelength_in_m, _EXP.detector_dist_in_m
    )
    assert np.allclose(_out_range, _ref_range, rtol=1e-5)


if __name__ == "__main__":
    pytest.main()
