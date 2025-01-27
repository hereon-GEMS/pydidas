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


import unittest

import numpy as np

from pydidas.core import UserConfigError
from pydidas.core.fitting import FitFuncMeta
from pydidas.core.fitting.fit_func_base import FitFuncBase
from pydidas.core.utils import flatten


FIT_CLASS = FitFuncBase


class TEST_FIT_CLASS(FitFuncBase):
    pass


class TestFitFuncBase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._x = np.arange(20)
        cls._y = np.random.random((cls._x.size))

    @classmethod
    def tearDownClass(cls):
        if "Test class" in FitFuncMeta.registry:
            del FitFuncMeta.registry["Test class"]

    def tearDown(self):
        TEST_FIT_CLASS.func = lambda c, x: x
        for _key in [
            "name",
            "param_bounds_low",
            "param_bounds_high",
            "param_labels",
            "num_peaks",
            "num_peak_params",
            "center_param_index",
            "amplitude_param_index",
        ]:
            setattr(TEST_FIT_CLASS, _key, getattr(FitFuncBase, _key))

    def test_class_params_okay(self):
        for _attribute in [
            "name",
            "param_bounds_low",
            "param_bounds_high",
            "param_labels",
        ]:
            self.assertTrue(hasattr(FIT_CLASS, _attribute))

    def test_func(self):
        _res = FIT_CLASS.func([], self._y)
        self.assertTrue(np.all(_res == self._y))
        self.assertIsInstance(_res, np.ndarray)

    def test_profile(self):
        TEST_FIT_CLASS.num_peak_params = 1
        for _num_peaks in [1, 2]:
            TEST_FIT_CLASS.num_peaks = _num_peaks
            _params = [42.1] if _num_peaks == 1 else [42.1, 12.3]
            for _bgparams, _expected_bg in [
                [[], 0],
                [[2], 2],
                [[2, 4], 2 + 4 * self._x],
            ]:
                with self.subTest(num_peaks=_num_peaks, bg_order=len(_bgparams)):
                    _result = TEST_FIT_CLASS.profile(_params + _bgparams, self._x)
                    self.assertTrue(
                        np.allclose(
                            _result, TEST_FIT_CLASS.num_peaks * self._x + _expected_bg
                        )
                    )
                    self.assertIsInstance(_result, np.ndarray)

    def test_calculate_background(self):
        TEST_FIT_CLASS.num_peak_params = 1
        for _num_peak_params in [1, 2, 3]:
            TEST_FIT_CLASS.num_peak_params = _num_peak_params
            for _num_peaks in [1, 2, 3]:
                TEST_FIT_CLASS.num_peaks = _num_peaks
                for _bg_params in [(), (2,), (2, 4)]:
                    _params = tuple(range(_num_peaks * _num_peak_params)) + _bg_params
                    with self.subTest(bg_order=len(_params)):
                        _bg = TEST_FIT_CLASS.calculate_background(_params, self._x)
                        self.assertIsInstance(_bg, np.ndarray)
                        self.assertTrue(
                            np.allclose(_bg, np.polyval(_bg_params[::-1], self._x))
                        )

    def test_calculate_background__unsupported_order(self):
        TEST_FIT_CLASS.num_peaks = 1
        TEST_FIT_CLASS.num_peak_params = 1
        with self.assertRaises(ValueError):
            TEST_FIT_CLASS.calculate_background([0, 1, 2, 3], self._x)

    def test_delta(self):
        TEST_FIT_CLASS.num_peak_params = 2
        for _num_peaks in [1, 2]:
            TEST_FIT_CLASS.num_peaks = _num_peaks
            for _bg_params in [(), (2,), (2, 4)]:
                _params = ((2, 5) if _num_peaks == 1 else (1.5, 3, 2, 4)) + _bg_params
                with self.subTest(num_peaks=_num_peaks):
                    _result = TEST_FIT_CLASS.delta(_params, self._x, self._y)
                    self.assertTrue(
                        np.allclose(
                            _result,
                            _num_peaks * self._x
                            + TEST_FIT_CLASS.calculate_background(_params, self._x)
                            - self._y,
                        )
                    )
                    self.assertIsInstance(_result, np.ndarray)

    def test_area(self):
        _full_params = np.array((0.85, 1.23, 2.01, 3.44, 4.52, 5.67, 6.78, 7.41, 8.93))
        for _num_peaks in [1, 2, 3]:
            TEST_FIT_CLASS.num_peaks = _num_peaks
            for _amplitude_param in [0, 1, 2]:
                TEST_FIT_CLASS.amplitude_param_index = _amplitude_param
                with self.subTest(
                    num_peaks=_num_peaks, amplitude_param_index=_amplitude_param
                ):
                    _params = tuple(_full_params[: _num_peaks * 3])
                    _area = TEST_FIT_CLASS.area(_params)
                    self.assertEqual(_area, _params[_amplitude_param::3])
                    self.assertIsInstance(_area, tuple)

    def test_fwhm(self):
        with self.assertRaises(NotImplementedError):
            FIT_CLASS.fwhm(())

    def test_center(self):
        _full_params = np.array((0.85, 1.23, 2.01, 3.44, 4.52, 5.67, 6.78, 7.41, 8.93))
        TEST_FIT_CLASS.num_peak_params = 3
        for _num_peaks in [1, 2, 3]:
            TEST_FIT_CLASS.num_peaks = _num_peaks
            for _num_peak_params in [1, 2, 3]:
                TEST_FIT_CLASS.num_peak_params = _num_peak_params
                for _center_pos in range(_num_peak_params):
                    TEST_FIT_CLASS.center_param_index = _center_pos
                    for _method_name in ["center", "position"]:
                        _method = getattr(TEST_FIT_CLASS, _method_name)
                        with self.subTest(
                            num_peaks=_num_peaks,
                            center_pos=_center_pos,
                            method_name=_method_name,
                        ):
                            _params = tuple(
                                _full_params[: _num_peaks * _num_peak_params]
                            )
                            _centers = _method(_params)
                            self.assertIsInstance(_centers, tuple)
                            self.assertTrue(
                                np.allclose(
                                    _centers, _params[_center_pos::_num_peak_params]
                                )
                            )

    def test_center_param_indices(self):
        _params = np.arange(12)
        for _num_peaks in [1, 2, 3]:
            TEST_FIT_CLASS.num_peaks = _num_peaks
            for _num_peak_params in [1, 2, 3]:
                TEST_FIT_CLASS.num_peak_params = _num_peak_params
                for _center_pos in range(_num_peak_params):
                    TEST_FIT_CLASS.center_param_index = _center_pos
                    with self.subTest(
                        num_peaks=_num_peaks,
                        num_peak_params=_num_peak_params,
                        center_pos=_center_pos,
                    ):
                        self.assertEqual(
                            TEST_FIT_CLASS._center_param_indices(),
                            list(
                                range(
                                    _center_pos,
                                    _num_peak_params * _num_peaks,
                                    _num_peak_params,
                                )
                            ),
                        )

    def test_center_param_indices__w_num_peaks_keyword(self):
        _params = np.arange(12)
        for _num_peaks in [1, 2, 3, 4]:
            TEST_FIT_CLASS.num_peaks = _num_peaks
            for _num_peak_params in [1, 2, 3]:
                TEST_FIT_CLASS.num_peak_params = _num_peak_params
                for _center_pos in range(_num_peak_params):
                    TEST_FIT_CLASS.center_param_index = _center_pos
                    for _used_num_peaks in range(1, _num_peaks + 1):
                        with self.subTest(
                            num_peaks=_num_peaks,
                            num_peak_params=_num_peak_params,
                            center_pos=_center_pos,
                            used_num_of_peaks=_used_num_peaks,
                        ):
                            self.assertEqual(
                                TEST_FIT_CLASS._center_param_indices(
                                    num_peaks=_used_num_peaks
                                ),
                                list(
                                    range(
                                        _center_pos,
                                        _num_peak_params * _used_num_peaks,
                                        _num_peak_params,
                                    )
                                ),
                            )

    def test_background_at_peak(self):
        _full_params = (1.0, 2.5, 4.25, 6.5, 8.2, 10.1, 12.3, 14.5, 16.7)
        for _bg_params in [(), (12,), (12, 25)]:
            for _num_peaks in [1, 2, 3]:
                TEST_FIT_CLASS.num_peaks = _num_peaks
                _params = _full_params[: _num_peaks * 3] + _bg_params
                for _center_pos in [0, 1, 2]:
                    TEST_FIT_CLASS.center_param_index = _center_pos
                    with self.subTest(
                        bg_order=len(_bg_params),
                        num_peaks=_num_peaks,
                        center_param_index=_center_pos,
                    ):
                        _bg = TEST_FIT_CLASS.background_at_peak(_params)
                        _peaks = _full_params[_center_pos : 3 * _num_peaks : 3]
                        _expected_bg = (
                            np.zeros(_num_peaks)
                            if not _bg_params
                            else np.polyval(_bg_params[::-1], _peaks)
                        )
                        self.assertIsInstance(_bg, tuple)
                        self.assertTrue(np.allclose(_bg, _expected_bg))

    def test_guess_fit_start_params(self):
        TEST_FIT_CLASS.center_param_index = 0
        for _bg_params in [(), (4.5,), (2.5, 2.0)]:
            _y = (
                0 * self._x
                if len(_bg_params) == 0
                else np.polyval(_bg_params[::-1], self._x)
            )
            _y_copy = _y.copy()
            _bg_order = None if len(_bg_params) == 0 else len(_bg_params) - 1
            for _num_peak_params in [1, 2, 3]:
                TEST_FIT_CLASS.num_peak_params = _num_peak_params
                for _num_peaks in [1, 2, 3]:
                    TEST_FIT_CLASS.num_peaks = _num_peaks
                    TEST_FIT_CLASS.param_labels = flatten(
                        [f"center{i}", f"amp{i}", f"sigma{i}"][:_num_peak_params]
                        for i in range(_num_peaks)
                    )
                    with self.subTest(bg_order=_bg_order, num_peaks=_num_peaks):
                        _params = TEST_FIT_CLASS.guess_fit_start_params(
                            self._x, _y, bg_order=_bg_order
                        )
                        self.assertIsInstance(_params, tuple)
                        self.assertEqual(
                            len(_params),
                            _num_peaks * _num_peak_params + len(_bg_params),
                        )
                        self.assertTrue(np.allclose(_y, _y_copy))

    def test_estimate_background_params(self):
        _x = np.arange(20)
        _y = np.sin(_x / 3) + 2 + 0.1 * _x
        for _bg_order in [None, 0, 1]:
            with self.subTest(bg_order=_bg_order):
                _y_new, _bg_params = TEST_FIT_CLASS.estimate_background_params(
                    _x, _y, _bg_order
                )
                self.assertIsInstance(_bg_params, tuple)
                if _bg_order is None:
                    self.assertEqual(_bg_params, ())
                    self.assertTrue(np.allclose(_y_new, _y))
                else:
                    self.assertEqual(len(_bg_params), _bg_order + 1)
                    _bg = np.polyval(_bg_params[::-1], _x)
                    self.assertTrue(np.allclose(_y_new, _y - _bg))

    def test_estimate_background_params__wrong_bg_order(self):
        _x = np.arange(20)
        _y = np.sin(_x / 3)
        with self.assertRaises(ValueError):
            FIT_CLASS.estimate_background_params(_x, _y, 4)

    def test_guess_peak_start_params(self):
        for _num_peaks in [1, 2, 3]:
            TEST_FIT_CLASS.num_peaks = _num_peaks
            for _num_peak_params in [1, 2, 3]:
                TEST_FIT_CLASS.param_labels = flatten(
                    ["center{i}", "amp{i}", "sigma{i}"][:_num_peak_params]
                    for i in range(_num_peaks)
                )
                TEST_FIT_CLASS.num_peak_params = _num_peak_params
                with self.subTest(num_peaks=_num_peaks):
                    _params = TEST_FIT_CLASS.guess_peak_start_params(
                        self._x, self._y, _num_peaks
                    )
                    self.assertIsInstance(_params, tuple)
                    self.assertEqual(len(_params), _num_peak_params)

    def test_get_y_value(self):
        _delta_x = np.diff(self._x).mean()
        for _x, _y in [
            (self._x[0], self._y[0]),
            (self._x[1], self._y[1]),
            (self._x[2] + 0.25 * _delta_x, self._y[2] * 0.75 + 0.25 * self._y[3]),
            (self._x[2] + 0.5 * _delta_x, 0.5 * (self._y[3] + self._y[2])),
        ]:
            with self.subTest(x=_x):
                self.assertAlmostEqual(
                    TEST_FIT_CLASS.get_y_value(_x, self._x, self._y), _y
                )

    def test_get_y_value__outside_bounds(self):
        for _x in [self._x[0] - 1, self._x[-1] + 1]:
            with self.subTest(x=_x):
                with self.assertRaises(UserConfigError):
                    self.assertEqual(TEST_FIT_CLASS.get_y_value(_x, self._x, self._y))

    def test_get_fwhm_indices__single_range_x_in(self):
        _x = np.linspace(-0.5 * np.pi, 1.5 * np.pi, num=41)
        _y = np.sin(_x)
        _x0 = (_x[19] + _x[20]) / 2
        _y0 = np.sin(_x0)
        _range = FIT_CLASS.get_fwhm_indices(_x0, _y0, _x, _y)
        self.assertTrue(np.all(np.where(_y >= 0.5 * _y0)[0] == _range))

    def test_get_fwhm_indices__empty_range(self):
        _x = 0.4 * np.arange(30) + 2
        _y = np.ones(_x.size)
        _range = FIT_CLASS.get_fwhm_indices(_x[15], 3, _x, _y)
        self.assertTrue(np.all(np.array([]) == _range))

    def test_get_fwhm_indices__adjacent_jumps(self):
        _x = 0.4 * np.arange(30) + 2
        _y = np.zeros(_x.size)
        _y[2:5] = 1
        _y[9] = 1
        _y[15:18] = 1
        _range = FIT_CLASS.get_fwhm_indices(_x[3], 1, _x, _y)
        self.assertTrue(np.all(np.arange(2, 5) == _range))

    def test_get_fwhm_indices__double_range_x_in(self):
        _x = np.linspace(-0.5 * np.pi, 3.5 * np.pi, num=61)
        _y = np.sin(_x)
        _x0 = (_x[15] + _x[14]) / 2
        _y0 = np.sin(_x0)
        _range = FIT_CLASS.get_fwhm_indices(_x0, _y0, _x, _y)
        self.assertTrue(np.all(np.where(_y[:31] >= 0.5 * _y0)[0] == _range))

    def test_get_fwhm_indices__double_range_x_out(self):
        _x = np.linspace(-0.5 * np.pi, 3.5 * np.pi, num=61)
        _y = np.sin(_x)
        _x0 = np.pi
        _y0 = 1
        _range = FIT_CLASS.get_fwhm_indices(_x0, _y0, _x, _y)
        self.assertTrue(np.all(np.array([]) == _range))

    def test_sort_fitted_peaks_by_position(self):
        _raw_peak_params = (4, 5, 6, 1, 2, 3, 10, 11, 12, 7, 8, 9)
        for _num_peaks in [1, 2, 3, 4]:
            TEST_FIT_CLASS.num_peaks = _num_peaks
            for _used_num_peaks in range(1, _num_peaks + 1):
                for _num_peak_params in [1, 2, 3]:
                    TEST_FIT_CLASS.num_peak_params = _num_peak_params
                    _peak_params = tuple(
                        p
                        for i, p in enumerate(_raw_peak_params[: 3 * _num_peaks])
                        if i % 3 < _num_peak_params
                    )
                    for _center_param_index in range(_num_peak_params):
                        TEST_FIT_CLASS.center_param_index = _center_param_index
                        for _bg_params in [(), (4,), (4, 5)]:
                            _params = _peak_params + _bg_params
                            with self.subTest(
                                num_peaks=_num_peaks,
                                used_num_peaks=_used_num_peaks,
                                num_peak_params=_num_peak_params,
                                bg_order=len(_bg_params),
                            ):
                                _index_where_sorted = _used_num_peaks * _num_peak_params
                                _sorted_params = (
                                    TEST_FIT_CLASS.sort_fitted_peaks_by_position(
                                        _params, num_peaks=_used_num_peaks
                                    )
                                )
                                self.assertIsInstance(_sorted_params, tuple)
                                self.assertEqual(
                                    len(_sorted_params),
                                    _num_peaks * _num_peak_params + len(_bg_params),
                                )
                                self.assertEqual(
                                    _sorted_params,
                                    tuple(sorted(_peak_params[:_index_where_sorted]))
                                    + _params[_index_where_sorted:],
                                )


if __name__ == "__main__":
    unittest.main()
