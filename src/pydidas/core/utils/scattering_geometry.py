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
The scattering_geometry module includes calculations required for conversions to/from Q.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = [
    "q_to_2theta",
    "convert_integration_result",
    "convert_d_spacing_to_2theta",
    "convert_polar_to_d_spacing",
]


from numbers import Real
from typing import Literal

import numpy as np

from pydidas.core.dataset import Dataset
from pydidas.core.exceptions import UserConfigError


ALLOWED_UNITS = Literal[
    "2theta / deg",
    "2theta / rad",
    "Q / A^-1",
    "Q / nm^-1",
    "r / mm",
    "d-spacing / nm",
    "d-spacing / A",
]


def q_to_2theta(
    q: Real | np.ndarray,
    lambda_xray: Real,
    q_unit: Literal["Q / A^-1", "Q_A^-1", "Q / nm^-1", "Q_nm^-1"] | None = None,
) -> Real | np.ndarray:
    """
    Convert a q value to 2theta.

    This function converts a q value (in inverse meters) to 2theta (in radian).
    Optionally, the input unit for q can be specified as either inverse Angstrom
    or inverse nanometers in the formats `Q / A^-1`, `Q_A^-1` or
    `Q / nm^-1`, `Q_nm^-1`, respectively.


    Parameters
    ----------
    q : Real | np.ndarray
        The q value(s) to be converted.
    lambda_xray : Real
        The X-ray wavelength in meters.
    q_unit : Literal["Q / A^-1", "Q_A^-1", "Q / nm^-1", "Q_nm^-1"], optional
        The unit of the q value. If not specified, the function assumes the
        input is in inverse meters.

    Returns
    -------
    Real | np.ndarray
        The converted 2theta value(s).
    """
    if q_unit is not None:
        q_unit = q_unit.replace(" ", "")
        if q_unit not in ["Q/A^-1", "Q_A^-1", "Q/nm^-1", "Q_nm^-1"]:
            raise UserConfigError(
                f"The q unit `{q_unit}` is not supported in the `q_to_2theta` function."
                "Only `Q / A^-1`, `Q_A^-1`, `Q / nm^-1`, and `Q_nm^-1` are allowed."
                "\n(spaces will be removed from the unit string automatically)"
            )
    if q_unit in ["Q/A^-1", "Q_A^-1"]:
        q = q * 1e10  # Convert to inverse meters: 1 A^-1 = 1e10 m^-1
    elif q_unit in ["Q/nm^-1", "Q_nm^-1"]:
        q = q * 1e9  # Convert to inverse meters: 1 nm^-1 = 1e9 m^-1
    return 2 * np.arcsin(lambda_xray * q / (4 * np.pi))


def convert_integration_result(  # noqa: C901
    value: Real | np.ndarray,
    in_type: ALLOWED_UNITS,
    out_type: ALLOWED_UNITS,
    lambda_xray: Real,
    det_dist: Real,
) -> Real | np.ndarray:
    """
    Convert an integration result from one type and/or unit to another.

    This function supports conversion between the following types:

    - 2theta / deg
    - 2theta / rad
    - Q / A^-1
    - Q / nm^-1
    - r / mm
    - d-spacing / nm
    - d-spacing / A

    Parameters
    ----------
    value : Real
        The value to be converted.
    in_type : Literal["2theta / deg", "2theta / rad", "Q / A^-1", "Q / nm^-1", "r / mm", "d-spacing / nm", "d-spacing / A"]
        The type of input, including the unit.
    out_type : Literal["2theta / deg", "2theta / rad", "Q / A^-1", "Q / nm^-1", "r / mm", "d-spacing / nm", "d-spacing / A"]
        The type of output, including the unit.
    lambda_xray : Real
        The X-ray wavelength in meters.
    det_dist : Real
        The detector distance in meters.

    Returns
    -------
    Real | np.ndarray
        The converted value(s) in the same type as the input value.
    """
    _in_type = in_type.replace(" ", "").replace("_", "/")
    _out_type = out_type.replace(" ", "").replace("_", "/")

    if _in_type == _out_type:
        return value

    match _in_type:
        case "2theta/deg":
            value_in_2theta_rad = np.deg2rad(value)
        case "2theta/rad":
            value_in_2theta_rad = value
        case "Q/A^-1":
            value_in_2theta_rad = 2 * np.arcsin(
                lambda_xray * (value * 1e10) / (4 * np.pi)
            )
        case "Q/nm^-1":
            value_in_2theta_rad = 2 * np.arcsin(
                lambda_xray * (value * 1e9) / (4 * np.pi)
            )
        case "r/mm":
            value_in_2theta_rad = np.arctan(value * 1e-3 / det_dist)
        case "d-spacing/nm":
            value_in_2theta_rad = 2 * np.arcsin(lambda_xray / (2 * value * 1e-9))
        case "d-spacing/A":
            value_in_2theta_rad = 2 * np.arcsin(lambda_xray / (2 * value * 1e-10))
        case _:
            raise UserConfigError(
                f"The input type `{in_type}` is not supported in the "
                "`convert_polar_value` function."
            )
    if isinstance(value_in_2theta_rad, Dataset):
        value_in_2theta_rad.data_label = _out_type.split("/")[0]
        value_in_2theta_rad.data_unit = _out_type.split("/")[1]

    match _out_type:
        case "2theta/deg":
            return np.rad2deg(value_in_2theta_rad)
        case "2theta/rad":
            return value_in_2theta_rad
        case "Q/A^-1":
            return 4 * np.pi * np.sin(value_in_2theta_rad / 2) / lambda_xray * 1e-10
        case "Q/nm^-1":
            return 4 * np.pi * np.sin(value_in_2theta_rad / 2) / lambda_xray * 1e-9
        case "r/mm":
            return det_dist * np.tan(value_in_2theta_rad) * 1e3
        case "d-spacing/nm":
            return lambda_xray / (2 * np.sin(value_in_2theta_rad / 2)) * 1e9
        case "d-spacing/A":
            return lambda_xray / (2 * np.sin(value_in_2theta_rad / 2)) * 1e10
        case _:
            raise UserConfigError(
                f"The output type `{out_type}` is not supported in the "
                "`convert_polar_value` function."
            )


def convert_d_spacing_to_q(
    d_spacing: Real | np.ndarray,
    d_spacing_unit: Literal["nm", "A"],
    output_unit: Literal["nm^-1", "A^-1"],
) -> Real | np.ndarray:
    """
    Convert a d-spacing value to reciprocal space.

    Parameters
    ----------
    d_spacing : Real | np.ndarray
        The d-spacing value.
    d_spacing_unit : Literal["nm", "A"]
        The unit of the d-spacing value.
    output_unit : Literal["nm^-1", "A^-1"]
        The unit to convert the d-spacing value to.

    Returns
    -------
    Real | np.ndarray
        The converted reciprocal space value in inverse meters.
    """
    if d_spacing_unit not in ["nm", "A"]:
        raise UserConfigError(
            f"The d-spacing unit `{d_spacing_unit}` is not supported. Only `nm` "
            "and `A` are allowed."
        )
    if output_unit not in ["nm^-1", "A^-1"]:
        raise UserConfigError(
            f"The output unit `{output_unit}` is not supported. Only `nm^-1` "
            "and `A^-1` are allowed."
        )
    _factor = 1e-10 if d_spacing_unit == "A" else 1e-9
    _q_in_m = 2 * np.pi / (d_spacing * _factor)
    if output_unit == "nm^-1":
        return _q_in_m * 1e9
    return _q_in_m * 1e10


def convert_d_spacing_to_2theta(
    d_spacing: Real | np.ndarray,
    d_spacing_unit: Literal["nm", "A"],
    output_unit: Literal["deg", "rad"],
    lambda_xray: Real,
) -> Real | np.ndarray:
    """
    Convert a d-spacing value to 2theta.

    Parameters
    ----------
    d_spacing : Real | np.ndarray
        The d-spacing value.
    d_spacing_unit : Literal["nm", "A"]
        The unit of the d-spacing value.
    output_unit : Literal["deg", "rad"]
        The unit to convert the d-spacing value to.
    lambda_xray : Real
        The X-ray wavelength in meters.
    """
    if d_spacing_unit not in ["nm", "A"]:
        raise UserConfigError(
            f"The d-spacing unit `{d_spacing_unit}` is not supported. Only `nm` "
            "and `A` are allowed."
        )
    if output_unit not in ["deg", "rad"]:
        raise UserConfigError(
            f"The output unit `{output_unit}` is not supported. Only `deg` "
            "and `rad` are allowed."
        )
    _factor = 1e-10 if d_spacing_unit == "A" else 1e-9
    _two_theta_rad = 2 * np.arcsin(lambda_xray / (2 * d_spacing * _factor))
    if output_unit == "deg":
        return np.rad2deg(_two_theta_rad)
    return _two_theta_rad


def convert_polar_to_d_spacing(
    value: Real | np.ndarray,
    in_type: Literal[
        "2theta / deg",
        "2theta / rad",
        "Q / A^-1",
        "Q / nm^-1",
        "r / mm",
        "d-spacing / nm",
        "d-spacing / A",
    ],
    out_unit: Literal["nm", "A"],
    lambda_xray: Real,
    det_dist: Real,
) -> Real | np.ndarray:
    """
    Convert a polar coordinate value to d-spacing.

    Parameters
    ----------
    value : Real | np.ndarray
        The value to be converted.
    in_type :  Literal["2theta / deg", "2theta / rad", "Q / A^-1", "Q / nm^-1", "r / mm", "d-spacing / nm", "d-spacing / A"]
        The type of input, including the unit.
    out_unit : Literal["nm", "A", "Angstrom"]
        The unit to convert the value to.
    lambda_xray : Real
        The X-ray wavelength in meters.
    det_dist : Real
        The detector distance in meters.

    Returns
    -------
    Real | np.ndarray
        The converted d-spacing value.
    """
    _in_type = in_type.replace(" ", "").replace("_", "/")
    if _in_type not in [
        "2theta/deg",
        "2theta/rad",
        "Q/A^-1",
        "Q/nm^-1",
        "r/mm",
        "d-spacing/nm",
        "d-spacing/A",
    ]:
        raise UserConfigError(
            f"The input type `{in_type}` is not supported in the "
            "`convert_polar_to_d_spacing` function."
        )
    if out_unit not in ["nm", "A", "Angstrom"]:
        raise UserConfigError(
            f"The output unit `{out_unit}` is not supported in the "
            "`convert_polar_to_d_spacing` function."
        )
    _out_factor = 1e9 if out_unit == "nm" else 1e10
    match _in_type:
        case "Q/A^-1":
            _range = (2 * np.pi) / (value / 1e-10) * _out_factor
        case "Q/nm^-1":
            _range = (2 * np.pi) / (value / 1e-9) * _out_factor
        case "r/mm":
            _range = (
                lambda_xray
                / (2 * np.sin(np.arctan((value * 1e-3) / det_dist) / 2))
                * _out_factor
            )
        case "2theta/deg":
            _range = lambda_xray / (2 * np.sin(np.deg2rad(value) / 2)) * _out_factor
        case "2theta/rad":
            _range = lambda_xray / (2 * np.sin(value / 2)) * _out_factor
        case "d-spacing/nm":
            _range = value * 1e-9 * _out_factor
        case "d-spacing/A":
            _range = value * 1e-10 * _out_factor
    return _range
