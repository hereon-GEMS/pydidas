# This file is part of pydidas.
#
# Copyright 2023, Helmholtz-Zentrum Hereon
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
__copyright__ = "Copyright 2023, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"


import unittest

import numpy as np

from pydidas.core import UserConfigError
from pydidas.core.utils import (
    fit_circle_from_points,
    fit_detector_center_and_tilt_from_points,
    fit_ellipse_from_points,
)


class TestMathUtils(unittest.TestCase):
    def setUp(self):
        ...

    def tearDown(self):
        ...

    def create_ellipse(self, x, x0, y0, a, b, c):
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

    def get_ellipsis_axes_lengths(self, params):
        a, b, c, d, f, g = params
        _axes = (
            2
            * (a * f**2 + c * d**2 + g * b**2 - 2 * b * d * f - a * c * g)
            / (b**2 - a * c)
            / (np.array((1, -1)) * ((a - c) ** 2 + 4 * b**2) ** 0.5 - (a + c))
        ) ** 0.5
        return np.amin(_axes), np.amax(_axes)

    def test_fit_ellipse_from_points__perfect_circle(self):
        x0 = 450
        y0 = 657.5
        r = 300
        phi = np.arange(0, 2 * np.pi, 0.1)
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
            self.assertAlmostEqual(_fit, _target, 2)

    def test_fit_ellipse_from_points__perfect_circle_few_points(self):
        x0 = 450
        y0 = 657.5
        r = 300
        phi = np.array((0, 2, 4, 5, 5.5))
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
            self.assertAlmostEqual(_fit, _target, 2)

    def test_fit_ellipse_from_points__simple_ellipse(self):
        x0 = 450
        y0 = 657.5
        x = np.linspace(-2000, 3000, num=401)
        _xpoints, _ypoints, _params = self.create_ellipse(x, x0, y0, 1e-3, 2e-4, 4e-3)
        _coeffs = fit_ellipse_from_points(_xpoints, _ypoints)
        _coeffs /= _coeffs[0]
        for _fit, _target in zip(_coeffs, _params):
            self.assertAlmostEqual(_fit, _target, 2)

    def test_fit_ellipse_from_points__simple_ellipse_few_points(self):
        x0 = 450
        y0 = 657.5
        x = np.linspace(300, 600, num=3)
        _xpoints, _ypoints, _params = self.create_ellipse(x, x0, y0, 1e-3, 2e-4, 4e-3)
        _coeffs = fit_ellipse_from_points(_xpoints, _ypoints)
        _coeffs /= _coeffs[0]
        for _fit, _target in zip(_coeffs, _params):
            self.assertAlmostEqual(_fit, _target, 2)

    def test_fit_detector_center_and_tilt_from_points__a_smaller_c(self):
        x0 = 450
        y0 = 657.5
        x = np.linspace(300, 600, num=3)
        _xpoints, _ypoints, _params = self.create_ellipse(x, x0, y0, 1e-3, 2e-4, 4e-3)
        _axes = self.get_ellipsis_axes_lengths(_params)
        _target_tilt = np.arccos(_axes[0] / _axes[1])
        _target_tiltplane = 0.5 * np.arctan(2 * _params[1] / (_params[0] - _params[2]))
        cx, cy, tilt, tp, _ = fit_detector_center_and_tilt_from_points(
            _xpoints, _ypoints
        )
        self.assertAlmostEqual(cx, x0, 3)
        self.assertAlmostEqual(cy, y0, 3)
        self.assertAlmostEqual(_target_tilt, tilt, 3)
        self.assertAlmostEqual(_target_tiltplane, tp, 3)

    def test_fit_detector_center_and_tilt_from_points__too_few_points(self):
        x0 = 450
        y0 = 657.5
        x = np.linspace(300, 600, num=2)
        _xpoints, _ypoints, _params = self.create_ellipse(x, x0, y0, 1e-3, 2e-4, 4e-3)
        with self.assertRaises(UserConfigError):
            _, _, _, _, _ = fit_detector_center_and_tilt_from_points(_xpoints, _ypoints)

    def test_fit_detector_center_and_tilt_from_points__a_greater_c(self):
        x0 = 450
        y0 = 657.5
        x = np.linspace(300, 600, num=3)
        _xpoints, _ypoints, _params = self.create_ellipse(x, x0, y0, 5e-3, -2e-4, 3e-3)
        _axes = self.get_ellipsis_axes_lengths(_params)
        _target_tilt = np.arccos(_axes[0] / _axes[1])
        _target_tiltplane = np.pi / 2 + 0.5 * np.arctan(
            2 * _params[1] / (_params[0] - _params[2])
        )
        cx, cy, tilt, tp, _ = fit_detector_center_and_tilt_from_points(
            _xpoints, _ypoints
        )
        self.assertAlmostEqual(cx, x0, 3)
        self.assertAlmostEqual(cy, y0, 3)
        self.assertAlmostEqual(_target_tilt, tilt, 3)
        self.assertAlmostEqual(_target_tiltplane, tp, 3)

    def test_fit_circle_from_points(self):
        x0 = 450
        y0 = 657.5
        r = 326.4
        phi = np.r_[[0, 3, 4.5]]
        x = r * np.cos(phi) + x0
        y = np.r_[
            [y0 + (1 if _phi <= np.pi else -1) * r * np.sin(_phi) for _phi in phi]
        ]
        cx, cy, rfit = fit_circle_from_points(x, y)
        self.assertAlmostEqual(x0, cx, 3)
        self.assertAlmostEqual(y0, cy, 3)
        self.assertAlmostEqual(r, rfit, 3)


if __name__ == "__main__":
    unittest.main()
