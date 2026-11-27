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
from scipy.special import voigt_profile

from pydidas.core import Dataset
from pydidas.core.fitting import FitFuncMeta
from pydidas.core.fitting.voigt import Voigt


@pytest.fixture
def x() -> np.ndarray:
    return np.linspace(0, 10, num=2000)


@pytest.fixture
def params(x: np.ndarray) -> tuple[float, ...]:
    return (7.3, 0.35, 0.85, x[987])


@pytest.fixture
def data(x: np.ndarray, params: tuple[float, ...]) -> Dataset:
    _area, _sigma, _gamma, _center = params
    return Dataset(
        _area * voigt_profile(x - _center, _sigma, _gamma),
        data_unit="data unit",
        axis_units=["ax_unit"],
        axis_ranges=[x],
    )


@pytest.fixture
def voigt_class(n_peaks: int) -> Iterator[type[Voigt]]:
    class _TestVoigt(Voigt):
        name = f"TestVoigt_{n_peaks}"
        num_peaks: ClassVar[int] = n_peaks

    try:
        yield _TestVoigt
    finally:
        del FitFuncMeta.registry[_TestVoigt.name]


def test_guess_fit_start_params__narrow_peak() -> None:
    _data = Dataset(np.ones(150), data_unit="data unit", axis_units=["ax_unit"])
    _data[39:42] = 2
    _data[40] = 5
    _params = Voigt.guess_fit_start_params(_data.axis_ranges[0], _data)
    assert _params[1] > 0


def test_guess_fit_start_params__normal_peak(x: np.ndarray, data: Dataset) -> None:
    _params = Voigt.guess_fit_start_params(x, data)
    assert _params[1] > 0


@pytest.mark.parametrize("low, high", [(42, 50), (35, 38)])
def test_guess_fit_start_params__center_bounds(
    x: np.ndarray, data: Dataset, low: int, high: int
) -> None:
    _bounds = (Voigt.param_bounds_low[:], Voigt.param_bounds_high[:])
    _bounds[0][3], _bounds[1][3] = x[low], x[high]
    _params = Voigt.guess_fit_start_params(x, data, bounds=_bounds)
    assert x[low] <= _params[3] <= x[high]
    assert _params[1] > 0


def test_func__values(x: np.ndarray, data: Dataset, params: tuple[float, ...]) -> None:
    np.testing.assert_allclose(Voigt.func(params, x), data.array)


def test_amplitude(data: Dataset, params: tuple[float, ...]) -> None:
    assert Voigt.amplitude(params) == pytest.approx((float(np.max(data)),), abs=5e-5)


def test_fwhm(x: np.ndarray, data: Dataset, params: tuple[float, ...]) -> None:
    _indices = np.where(data >= 0.5 * np.max(data))[0]
    _fwhm = x[_indices[-1]] - x[_indices[0]]
    assert Voigt.fwhm(params) == pytest.approx((_fwhm,), abs=2 * (x[1] - x[0]))


@pytest.mark.parametrize("n_peaks", [1, 2, 3])
@pytest.mark.parametrize("bg_params", [(), (2.0,), (2.0, 0.5)])
@pytest.mark.parametrize(
    "widths",
    [
        ((0.0, 2.0), (2.0, 0.0), (1.0, 1.0)),
        ((1.0, 3.0), (3.0, 1.0), (2.0, 3.0)),
        ((10.0, 30.0), (30.0, 10.0), (20.0, 30.0)),
    ],
)
def test_relative_sigma__ratio_per_peak(
    voigt_class: type[Voigt],
    n_peaks: int,
    bg_params: tuple[float, ...],
    widths: tuple[tuple[float, float], ...],
) -> None:
    _widths = widths[:n_peaks]
    _params = tuple(
        _value
        for _i, (_sigma, _gamma) in enumerate(_widths)
        for _value in (10.0 + _i, _sigma, _gamma, 5.0 + 10 * _i)
    )
    _expected = tuple(_sigma / (_sigma + _gamma) for _sigma, _gamma in _widths)
    _result = voigt_class.relative_sigma(_params + bg_params)
    assert isinstance(_result, tuple)
    assert len(_result) == n_peaks
    assert _result == pytest.approx(_expected)


if __name__ == "__main__":
    pytest.main([__file__])
