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
__all__ = ["q_to_2theta", "convert_radial_value"]


from numbers import Real
from typing import Literal

import numpy as np

from pydidas.core.exceptions import UserConfigError


def q_to_2theta(q: Real | np.ndarray, lambda_x: Real) -> Real | np.ndarray:
    """
    Convert a q value to 2theta.

    This function converts a q value (in inverse meters) to 2theta (in radian)

    Parameters
    ----------
    q : Real | np.ndarray
        The q value(s) to be converted.
    lambda_x : Real
        The X-ray wavelength in meters.

    Returns
    -------
    Real | np.ndarray
        The converted 2theta value(s).
    """
    return 2 * np.arcsin(lambda_x * q / (4 * np.pi))


def convert_radial_value(
    value: Real,
    in_unit: Literal["2theta / deg", "2theta / rad", "Q / A^-1", "Q / nm^-1", "r / mm"],
    out_unit: Literal[
        "2theta / deg", "2theta / rad", "Q / A^-1", "Q / nm^-1", "r / mm"
    ],
    lambda_xray: Real,
    det_dist: Real,
) -> Real:
    """
    Convert a value from one unit to another.

    Parameters
    ----------
    value : Real
        The value to be converted.
    in_unit : Literal["2theta / deg", "2theta / rad", "Q / A^-1", "Q / nm^-1", "r / mm"]
        The unit of the input value.
    out_unit : Literal["2theta / deg", "2theta / rad", "Q / A^-1", "Q / nm^-1", "r / mm"]
        The unit to convert the value to.
    lambda_xray : Real
        The X-ray wavelength in meters.
    det_dist : Real
        The detector distance in meters.
    """
    if in_unit == out_unit:
        return value

    if in_unit == "2theta / deg":
        value_in_2theta_rad = np.deg2rad(value)
    elif in_unit == "2theta / rad":
        value_in_2theta_rad = value
    elif in_unit == "Q / A^-1":
        value_in_2theta_rad = q_to_2theta(value * 1e10, lambda_xray)
    elif in_unit == "Q / nm^-1":
        value_in_2theta_rad = q_to_2theta(value * 1e9, lambda_xray)
    elif in_unit == "r / mm":
        value_in_2theta_rad = np.arctan(value * 1e-3 / det_dist)
    else:
        raise UserConfigError(f"The input unit `{in_unit}` is not supported.")
    if out_unit == "2theta / deg":
        return np.rad2deg(value_in_2theta_rad)
    elif out_unit == "2theta / rad":
        return value_in_2theta_rad
    elif out_unit == "Q / A^-1":
        return 4 * np.pi * np.sin(value_in_2theta_rad / 2) / lambda_xray * 1e-10
    elif out_unit == "Q / nm^-1":
        return 4 * np.pi * np.sin(value_in_2theta_rad / 2) / lambda_xray * 1e-9
    elif out_unit == "r / mm":
        return det_dist * np.tan(value_in_2theta_rad) * 1e3
    raise UserConfigError(f"The output unit `{out_unit}` is not supported.")
