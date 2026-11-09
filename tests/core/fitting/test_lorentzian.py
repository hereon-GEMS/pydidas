# This file is part of pydidas.
#
# Copyright 2024 - 2026, Helmholtz-Zentrum Hereon
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
__copyright__ = "Copyright 2024 - 2026, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"


from collections.abc import Iterator
from typing import ClassVar

import numpy as np
import pytest

from pydidas.core import Dataset
from pydidas.core.fitting import FitFuncMeta
from pydidas.core.fitting.lorentzian import Lorentzian


@pytest.fixture
def x() -> np.ndarray:
    return np.linspace(0, 10, num=2000)


@pytest.fixture
def params(x: np.ndarray) -> tuple[float, ...]:
    return (7.3, 1.42, x[987])


@pytest.fixture
def data(x: np.ndarray, params: tuple[float, ...]) -> Dataset:
    _area, _gamma, _center = params
    return Dataset(
        _area * (_gamma / np.pi) / ((x - _center) ** 2 + _gamma**2),
        data_unit="data unit",
        axis_units=["ax_unit"],
        axis_ranges=[x],
    )


@pytest.fixture
def lorentzian_class(n_peaks: int) -> Iterator[type[Lorentzian]]:
    class _TestLorentzian(Lorentzian):
        name = f"TestLorentzian_{n_peaks}"
        num_peaks: ClassVar[int] = n_peaks

    try:
        yield _TestLorentzian
    finally:
        del FitFuncMeta.registry[_TestLorentzian.name]


def test_guess_fit_start_params__narrow_peak() -> None:
    _data = Dataset(np.ones(150), data_unit="data unit", axis_units=["ax_unit"])
    _data[39:42] = 2
    _data[40] = 5
    _params = Lorentzian.guess_fit_start_params(_data.axis_ranges[0], _data)
    assert _params[1] > 0


def test_guess_fit_start_params__normal_peak(x: np.ndarray, data: Dataset) -> None:
    _params = Lorentzian.guess_fit_start_params(x, data)
    assert _params[1] > 0


@pytest.mark.parametrize("low, high", [(42, 50), (35, 38)])
def test_guess_fit_start_params__center_bounds(
    x: np.ndarray, data: Dataset, low: int, high: int
) -> None:
    _bounds = (Lorentzian.param_bounds_low[:], Lorentzian.param_bounds_high[:])
    _bounds[0][2], _bounds[1][2] = x[low], x[high]
    _params = Lorentzian.guess_fit_start_params(x, data, bounds=_bounds)
    assert x[low] <= _params[2] <= x[high]
    assert _params[1] > 0


def test_func__values(x: np.ndarray, data: Dataset, params: tuple[float, ...]) -> None:
    np.testing.assert_allclose(Lorentzian.func(params, x), data.array)


def test_amplitude(data: Dataset, params: tuple[float, ...]) -> None:
    assert Lorentzian.amplitude(params) == pytest.approx((float(np.max(data)),))


def test_fwhm(x: np.ndarray, data: Dataset, params: tuple[float, ...]) -> None:
    _indices = np.where(data >= 0.5 * np.max(data))[0]
    _fwhm = x[_indices[-1]] - x[_indices[0]]
    assert Lorentzian.fwhm(params) == pytest.approx((_fwhm,), abs=2 * (x[1] - x[0]))


@pytest.mark.parametrize("n_peaks", [1, 2, 3, 4])
@pytest.mark.parametrize("bg_params", [(), (2.0,), (2.0, 0.5)])
def test_relative_sigma__always_zero(
    lorentzian_class: type[Lorentzian], n_peaks: int, bg_params: tuple[float, ...]
) -> None:
    _params = tuple(
        _value
        for _i in range(n_peaks)
        for _value in (10.0 + _i, 0.5 + _i, 5.0 + 10 * _i)
    )
    _result = lorentzian_class.relative_sigma(_params + bg_params)
    assert isinstance(_result, tuple)
    assert _result == (0.0,) * n_peaks


if __name__ == "__main__":
    pytest.main([__file__])
