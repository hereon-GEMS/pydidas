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

"""Unit tests for pydidas modules."""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"


import numpy as np
import pytest

from pydidas.core import UserConfigError
from pydidas.core.math.ellipse import (
    axes_from_coeffs,
    fit_circle_from_points,
    fit_detector_center_and_tilt_from_points,
    fit_ellipse_from_points,
)


def create_ellipse(x, x0, y0, a, b, c):
    # using the formulas from https://mathworld.wolfram.com/Ellipse.html
    # d and f can be set to get the matching x0 and y0:
    d = -(a * x0 + b * y0)
    f = -(b * x0 + c * y0)
    g = 1
    _arg = (2 * f + 2 * b * x) ** 2 - 4 * c * (g + 2 * d * x + a * x**2)
    x = x[_arg >= 0]
    _arg = _arg[_arg >= 0]
    _y1 = (-2 * f - 2 * b * x - _arg**0.5) / (2 * c)
    _y2 = (-2 * f - 2 * b * x + _arg**0.5) / (2 * c)
    _xpoints = np.concatenate((x, x))
    _ypoints = np.concatenate((_y1, _y2))
    _params = np.r_[[a, b, c, d, f, g]] / a
    return _xpoints, _ypoints, _params


def get_ellipsis_axes_lengths(params):
    _axes = axes_from_coeffs(params)
    return np.amin(_axes), np.amax(_axes)


@pytest.mark.parametrize(
    "phi", [np.arange(0, 2 * np.pi, 0.1), np.array((0, 2, 4, 5, 5.5))]
)
def test_fit_ellipse_from_points__perfect_circle(phi):
    x0 = 450
    y0 = 657.5
    r = 300
    _xpoints = x0 + r * np.cos(phi)
    _ypoints = np.r_[
        [
            y0 + (1 if _phi <= np.pi else -1) * (r**2 - (_x - x0) ** 2) ** 0.5
            for _x, _phi in zip(_xpoints, phi)
        ]
    ]
    _target_coeffs = [1, 0, 1, -x0, -y0, x0**2 + y0**2 - r**2]
    _coeffs = fit_ellipse_from_points(_xpoints, _ypoints)
    _coeffs /= _coeffs[0]
    for _fit, _target in zip(_coeffs, _target_coeffs):
        assert _fit == pytest.approx(_target, 2)


@pytest.mark.parametrize(
    "x", [np.linspace(-2000, 3000, num=401), np.linspace(300, 600, num=3)]
)
def test_fit_ellipse_from_points__simple_ellipse(x):
    x0 = 450
    y0 = 657.5
    _xpoints, _ypoints, _params = create_ellipse(x, x0, y0, 1e-3, 2e-4, 4e-3)
    _coeffs = fit_ellipse_from_points(_xpoints, _ypoints)
    _coeffs /= _coeffs[0]
    for _fit, _target in zip(_coeffs, _params):
        assert _fit == pytest.approx(_target, 2)


@pytest.mark.parametrize("a, b, c", [(1e-3, 2e-4, 4e-3), (5e-3, -2e-4, 3e-3)])
def test_fit_detector_center_and_tilt_from_points__a_smaller_c(a, b, c):
    x0 = 450
    y0 = 657.5
    x = np.linspace(300, 600, num=3)
    _xpoints, _ypoints, _params = create_ellipse(x, x0, y0, a, b, c)
    _axes = get_ellipsis_axes_lengths(_params)
    _target_tilt = np.arccos(_axes[0] / _axes[1])
    _target_tilt_plane = 0.5 * np.arctan(2 * _params[1] / (_params[0] - _params[2]))
    cx, cy, tilt, tp, _ = fit_detector_center_and_tilt_from_points(_xpoints, _ypoints)
    assert cx == pytest.approx(x0, 3)
    assert cy == pytest.approx(y0, 3)
    assert _target_tilt == pytest.approx(tilt, 3)
    assert _target_tilt_plane == pytest.approx(tp, 3)


def test_fit_detector_center_and_tilt_from_points__too_few_points():
    x0 = 450
    y0 = 657.5
    x = np.linspace(300, 600, num=2)
    _xpoints, _ypoints, _params = create_ellipse(x, x0, y0, 1e-3, 2e-4, 4e-3)
    with pytest.raises(UserConfigError):
        _, _, _, _, _ = fit_detector_center_and_tilt_from_points(_xpoints, _ypoints)


def test_fit_circle_from_points():
    x0 = 450
    y0 = 657.5
    r = 326.4
    phi = np.r_[[0, 3, 4.5]]
    x = r * np.cos(phi) + x0
    y = np.r_[[y0 + (1 if _phi <= np.pi else -1) * r * np.sin(_phi) for _phi in phi]]
    cx, cy, rfit = fit_circle_from_points(x, y)
    assert x0 == pytest.approx(cx, 3)
    assert y0 == pytest.approx(cy, 3)
    assert r == pytest.approx(rfit, 3)


if __name__ == "__main__":
    pytest.main()
