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
from pydidas.core.fitting import FitFuncMeta
from pydidas.core.fitting.fit_func_base import FitFuncBase
from pydidas.core.utils import flatten


x = np.arange(20)
y = np.random.rand(x.size)


@pytest.fixture(autouse=True)
def TestClass():
    class TestClass(FitFuncBase):
        name = "Test class"

    yield TestClass
    if "Test class" in FitFuncMeta.registry:
        del FitFuncMeta.registry["Test class"]


def test_class_params_okay(TestClass):
    for _attribute in [
        "name",
        "param_bounds_low",
        "param_bounds_high",
        "param_labels",
    ]:
        assert hasattr(TestClass, _attribute)


def test_func(TestClass):
    _res = TestClass.func([], y)
    assert np.all(_res == y)
    assert isinstance(_res, np.ndarray)


@pytest.mark.parametrize("num_peaks", [1, 2, 3])
@pytest.mark.parametrize("bg_params", [(), (2,), (2, 4)])
def test_profile(TestClass, num_peaks, bg_params):
    TestClass.num_peak_params = 1
    TestClass.num_peaks = num_peaks
    _expected_bg = np.polyval(bg_params[::-1], x)
    _params = (42.1, 12.3, 68.1)[:num_peaks]
    _result = TestClass.profile(_params + bg_params, x)
    assert np.allclose(_result, TestClass.num_peaks * x + _expected_bg)
    assert isinstance(_result, np.ndarray)


@pytest.mark.parametrize("num_peaks", [1, 2, 3])
@pytest.mark.parametrize("num_peak_params", [1, 2, 3])
@pytest.mark.parametrize("bg_params", [(), (2,), (2, 4)])
def test_calculate_background(TestClass, num_peaks, num_peak_params, bg_params):
    TestClass.num_peak_params = num_peak_params
    TestClass.num_peaks = num_peaks
    _params = tuple(range(num_peaks * num_peak_params)) + bg_params
    _bg = TestClass.calculate_background(_params, x)
    assert isinstance(_bg, np.ndarray)
    assert np.allclose(_bg, np.polyval(bg_params[::-1], x))


def test_calculate_background__unsupported_order(TestClass):
    TestClass.num_peaks = 1
    TestClass.num_peak_params = 1
    with pytest.raises(ValueError):
        TestClass.calculate_background([0, 1, 2, 3], x)


@pytest.mark.parametrize("num_peaks", [1, 2])
@pytest.mark.parametrize("bg_params", [(), (2,), (2, 4)])
def test_delta(TestClass, num_peaks, bg_params):
    TestClass.num_peak_params = 2
    TestClass.num_peaks = num_peaks
    _params = ((2, 5) if num_peaks == 1 else (1.5, 3, 2, 4)) + bg_params
    _result = TestClass.delta(_params, x, y)
    assert np.allclose(
        _result,
        num_peaks * x + TestClass.calculate_background(_params, x) - y,
    )
    assert isinstance(_result, np.ndarray)


@pytest.mark.parametrize("num_peaks", [1, 2, 3])
@pytest.mark.parametrize("amplitude_param", [0, 1, 2])
def test_area(TestClass, num_peaks, amplitude_param):
    _full_params = np.array((0.85, 1.23, 2.01, 3.44, 4.52, 5.67, 6.78, 7.41, 8.93))
    TestClass.num_peaks = num_peaks
    TestClass.amplitude_param_index = amplitude_param
    _params = tuple(_full_params[: num_peaks * 3])
    _area = TestClass.area(_params)
    assert _area == _params[amplitude_param::3]
    assert isinstance(_area, tuple)


def test_fwhm(TestClass):
    with pytest.raises(NotImplementedError):
        TestClass.fwhm(())


@pytest.mark.parametrize("num_peaks", [1, 2, 3])
@pytest.mark.parametrize("num_peak_params", [1, 2, 3])
@pytest.mark.parametrize("method_name", ["center", "position"])
def test_center(TestClass, num_peaks, num_peak_params, method_name):
    _full_params = np.array((0.85, 1.23, 2.01, 3.44, 4.52, 5.67, 6.78, 7.41, 8.93))
    TestClass.num_peaks = num_peaks
    TestClass.num_peak_params = num_peak_params
    for _center_pos in range(num_peak_params):
        TestClass.center_param_index = _center_pos
        _method = getattr(TestClass, method_name)
        _params = tuple(_full_params[: num_peaks * num_peak_params])
        _centers = _method(_params)
        assert isinstance(_centers, tuple)
        assert np.allclose(_centers, _params[_center_pos::num_peak_params])


@pytest.mark.parametrize("num_peaks", [1, 2, 3])
@pytest.mark.parametrize("num_peak_params", [1, 2, 3])
def test_center_param_indices(TestClass, num_peaks, num_peak_params):
    _params = np.arange(12)
    TestClass.num_peaks = num_peaks
    TestClass.num_peak_params = num_peak_params
    for _center_pos in range(num_peak_params):
        TestClass.center_param_index = _center_pos
        assert TestClass._center_param_indices() == list(
            range(
                _center_pos,
                num_peak_params * num_peaks,
                num_peak_params,
            )
        )


@pytest.mark.parametrize("num_peaks", [1, 2, 3, 4])
@pytest.mark.parametrize("num_peak_params", [1, 2, 3])
@pytest.mark.parametrize("center_pos", [0, 1, 2])
@pytest.mark.parametrize("used_num_peaks", [1, 2, 3, 4])
def test_center_param_indices__w_num_peaks_keyword(
    TestClass, num_peaks, num_peak_params, center_pos, used_num_peaks
):
    TestClass.num_peaks = num_peaks
    TestClass.num_peak_params = num_peak_params
    if center_pos >= num_peak_params:
        return
    TestClass.center_param_index = center_pos
    if num_peaks < used_num_peaks:
        with pytest.raises(ValueError):
            TestClass._center_param_indices(num_peaks=used_num_peaks)
        return
    _params = np.arange(12)
    _center_indices = TestClass._center_param_indices(num_peaks=used_num_peaks)
    assert _center_indices == list(
        range(
            center_pos,
            num_peak_params * used_num_peaks,
            num_peak_params,
        )
    )


@pytest.mark.parametrize("num_peaks", [1, 2, 3])
@pytest.mark.parametrize("center_pos", [0, 1, 2])
@pytest.mark.parametrize("bg_params", [(), (12,), (12, 25)])
def test_background_at_peak(TestClass, num_peaks, center_pos, bg_params):
    TestClass.num_peaks = num_peaks
    TestClass.center_param_index = center_pos
    _full_params = (1.0, 2.5, 4.25, 6.5, 8.2, 10.1, 12.3, 14.5, 16.7)
    _params = _full_params[: num_peaks * 3] + bg_params
    _bg = TestClass.background_at_peak(_params)
    _peaks = _full_params[center_pos : 3 * num_peaks : 3]
    assert isinstance(_bg, tuple)
    assert np.allclose(_bg, np.polyval(bg_params[::-1], _peaks))


@pytest.mark.parametrize("num_peaks", [1, 2, 3])
@pytest.mark.parametrize("num_peak_params", [1, 2, 3])
@pytest.mark.parametrize("bg_params", [(), (4.5,), (2.5, 3.1)])
def test_guess_fit_start_params(TestClass, num_peaks, num_peak_params, bg_params):
    TestClass.center_param_index = 0
    TestClass.num_peaks = num_peaks
    TestClass.num_peak_params = num_peak_params
    _y = np.polyval(bg_params[::-1], x)
    _y_copy = _y.copy()
    _bg_order = None if len(bg_params) == 0 else len(bg_params) - 1
    TestClass.param_labels = flatten(
        [f"center{i}", f"amp{i}", f"sigma{i}"][:num_peak_params]
        for i in range(num_peaks)
    )
    _params = TestClass.guess_fit_start_params(x, _y, bg_order=_bg_order)
    assert isinstance(_params, tuple)
    assert len(_params) == num_peaks * num_peak_params + len(bg_params)
    assert np.allclose(_y, _y_copy)


@pytest.mark.parametrize("bg_order", [None, 0, 1])
def test_estimate_background_params(TestClass, bg_order):
    _x = np.arange(20)
    _y = np.sin(_x / 3) + 2 + 0.1 * _x
    _y_new, _bg_params = TestClass.estimate_background_params(_x, _y, bg_order)
    assert isinstance(_bg_params, tuple)
    if bg_order is None:
        assert _bg_params == ()
        assert np.allclose(_y_new, _y)
    else:
        assert len(_bg_params) == bg_order + 1
        _bg = np.polyval(_bg_params[::-1], _x)
        assert np.allclose(_y_new, _y - _bg)


def test_estimate_background_params__wrong_bg_order(TestClass):
    with pytest.raises(ValueError):
        TestClass.estimate_background_params(x, y, 4)


@pytest.mark.parametrize("num_peaks", [1, 2, 3])
@pytest.mark.parametrize("num_peak_params", [1, 2, 3])
def test_guess_peak_start_params(TestClass, num_peaks, num_peak_params):
    TestClass.num_peaks = num_peaks
    TestClass.num_peak_params = num_peak_params
    TestClass.param_labels = flatten(
        ["center{i}", "amp{i}", "sigma{i}"][:num_peak_params] for i in range(num_peaks)
    )
    _params = TestClass.guess_peak_start_params(x, y, num_peaks)
    assert isinstance(_params, tuple)
    assert len(_params) == num_peak_params


@pytest.mark.parametrize(
    "xy",
    [
        (x[0], y[0]),
        (x[1], y[1]),
        (0.75 * x[2] + 0.25 * x[3], y[2] * 0.75 + 0.25 * y[3]),
        (0.5 * x[2] + 0.5 * x[3], 0.5 * (y[3] + y[2])),
    ],
)
def test_get_y_value(TestClass, xy):
    _x, _y = xy
    assert np.allclose(TestClass.get_y_value(_x, x, y), _y)


@pytest.mark.parametrize("xpos", [x[0] - 1, x[-1] + 1])
def test_get_y_value__outside_bounds(TestClass, xpos):
    with pytest.raises(UserConfigError):
        TestClass.get_y_value(xpos, x, y)


def test_get_fwhm_indices__single_range_x_in(TestClass):
    _x = np.linspace(-0.5 * np.pi, 1.5 * np.pi, num=41)
    _y = np.sin(_x)
    _x0 = (_x[19] + _x[20]) / 2
    _y0 = np.sin(_x0)
    _range = TestClass.get_fwhm_indices(_x0, _y0, _x, _y)
    assert np.all(np.where(_y >= 0.5 * _y0)[0] == _range)


def test_get_fwhm_indices__empty_range(TestClass):
    _x = 0.4 * np.arange(30) + 2
    _y = np.ones(_x.size)
    _range = TestClass.get_fwhm_indices(_x[15], 3, _x, _y)
    assert np.all(np.array([]) == _range)


def test_get_fwhm_indices__adjacent_jumps(TestClass):
    _x = 0.4 * np.arange(30) + 2
    _y = np.zeros(_x.size)
    _y[2:5] = 1
    _y[9] = 1
    _y[15:18] = 1
    _range = TestClass.get_fwhm_indices(_x[3], 1, _x, _y)
    assert np.all(np.arange(2, 5) == _range)


def test_get_fwhm_indices__double_range_x_in(TestClass):
    _x = np.linspace(-0.5 * np.pi, 3.5 * np.pi, num=61)
    _y = np.sin(_x)
    _x0 = (_x[15] + _x[14]) / 2
    _y0 = np.sin(_x0)
    _range = TestClass.get_fwhm_indices(_x0, _y0, _x, _y)
    assert np.all(np.where(_y[:31] >= 0.5 * _y0)[0] == _range)


def test_get_fwhm_indices__double_range_x_out(TestClass):
    _x = np.linspace(-0.5 * np.pi, 3.5 * np.pi, num=61)
    _y = np.sin(_x)
    _x0 = np.pi
    _y0 = 1
    _range = TestClass.get_fwhm_indices(_x0, _y0, _x, _y)
    assert np.all(np.array([]) == _range)


@pytest.mark.parametrize("num_peaks", [1, 2, 3, 4])
@pytest.mark.parametrize("num_peak_params", [1, 2, 3])
@pytest.mark.parametrize("used_num_peaks", [1, 2, 3, 4])
@pytest.mark.parametrize("center_param_index", [0, 1, 2])
@pytest.mark.parametrize("bg_params", [(), (4,), (4, 5)])
def test_sort_fitted_peaks_by_position(
    TestClass, num_peaks, num_peak_params, used_num_peaks, center_param_index, bg_params
):
    _raw_peak_params = (4, 5, 6, 1, 2, 3, 10, 11, 12, 7, 8, 9)
    if num_peaks < used_num_peaks or center_param_index >= num_peak_params:
        return
    TestClass.num_peaks = num_peaks
    TestClass.num_peak_params = num_peak_params
    TestClass.center_param_index = center_param_index
    _peak_params = tuple(
        p
        for i, p in enumerate(_raw_peak_params[: 3 * num_peaks])
        if i % 3 < num_peak_params
    )
    _params = _peak_params + bg_params
    _index_where_sorted = used_num_peaks * num_peak_params
    _sorted_params = TestClass.sort_fitted_peaks_by_position(
        _params, num_peaks=used_num_peaks
    )
    assert isinstance(_sorted_params, tuple)
    assert len(_sorted_params) == num_peaks * num_peak_params + len(bg_params)
    assert _sorted_params == (
        tuple(sorted(_peak_params[:_index_where_sorted]))
        + _params[_index_where_sorted:]
    )
