# This file is part of pydidas.
#
# Copyright 2024 - 2025, Helmholtz-Zentrum Hereon
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
__copyright__ = "Copyright 2024 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"


import numpy as np
import pytest

from pydidas.core import PydidasQsettings, UserConfigError
from pydidas.core.utils import calculate_histogram_limits


@pytest.fixture(autouse=True)
def standard_qsettings():
    qsettings = PydidasQsettings()
    std_low = qsettings.value("user/histogram_outlier_fraction_low", dtype=float)
    std_high = qsettings.value("user/histogram_outlier_fraction_high", dtype=float)
    yield qsettings
    qsettings.set_value("user/histogram_outlier_fraction_low", std_low)
    qsettings.set_value("user/histogram_outlier_fraction_high", std_high)


def test_calculate_histogram_limits__wrong_limits(standard_qsettings):
    data = np.arange(100**2).reshape((100, 100))
    standard_qsettings.set_value("user/histogram_outlier_fraction_low", 0.6)
    standard_qsettings.set_value("user/histogram_outlier_fraction_high", 0.4)
    with pytest.raises(UserConfigError):
        calculate_histogram_limits(data)


@pytest.mark.parametrize("offset", [0, -500, -5e4, 12000, 120000])
@pytest.mark.parametrize("use_nans", [False, True])
@pytest.mark.parametrize("dtype", [np.float32, np.float64, np.int32, np.int64])
def test_calculate_histogram_limits__simple(
    standard_qsettings, offset, use_nans, dtype
):
    if use_nans and np.issubdtype(dtype, np.integer):
        return  # NaNs not possible in integer arrays
    raw_data = 1.0 * np.arange(100**2)
    standard_qsettings.set_value("user/histogram_outlier_fraction_low", 0.05)
    standard_qsettings.set_value("user/histogram_outlier_fraction_high", 0.05)
    data = (raw_data + offset).astype(dtype)
    if use_nans:
        data[500:550] = np.nan
    low, high = calculate_histogram_limits(data)
    assert abs(low - (500 + offset)) < 25
    assert abs(high - (9500 + offset)) < 25


def test_calculate_histogram_limits__all_outliers_cropped(standard_qsettings):
    data = np.arange(10000)
    data[4000:4498] = 1e8  # Add some outliers
    data[5000:5498] = 0
    standard_qsettings.set_value("user/histogram_outlier_fraction_low", 0.05)
    standard_qsettings.set_value("user/histogram_outlier_fraction_high", 0.05)
    low, high = calculate_histogram_limits(data)
    assert abs(low) < 5
    assert abs(high - 10000) < 5


def test_calculate_histogram_limits__too_many_outliers(standard_qsettings):
    data = np.arange(10000)
    data[4000:4510] = 1e8  # Add some outliers
    data[5000:5498] = 0
    standard_qsettings.set_value("user/histogram_outlier_fraction_low", 0.05)
    standard_qsettings.set_value("user/histogram_outlier_fraction_high", 0.05)
    low, high = calculate_histogram_limits(data)
    assert abs(low) < 5
    assert abs(high - 1e8) < 5


def test_calculate_histogram_limits__constant_outliers(standard_qsettings):
    data = np.linspace(0, 1, 10000)
    data[4000:4600] = 1e8
    data[5000:5498] = 0
    standard_qsettings.set_value("user/histogram_outlier_fraction_low", 0.05)
    standard_qsettings.set_value("user/histogram_outlier_fraction_high", 0.05)
    low, high = calculate_histogram_limits(data)
    assert abs(low) < 5
    assert abs(high - 1e8) < 5


def test_calculate_histogram_limits__high_outlier_fraction_very_small(
    standard_qsettings,
):
    data = np.linspace(0, 1, 10000)
    standard_qsettings.set_value("user/histogram_outlier_fraction_low", 0.05)
    standard_qsettings.set_value("user/histogram_outlier_fraction_high", 1e-7)
    low, high = calculate_histogram_limits(data)
    assert abs(low) < 0.1
    assert abs(high - 1) < 0.1


def test_calculate_histogram_limits__only_high_lim_very_low(standard_qsettings):
    raw_data = np.arange(1000**2)
    standard_qsettings.set_value("user/histogram_outlier_fraction_low", 0)
    standard_qsettings.set_value("user/histogram_outlier_fraction_high", 1 - 1e-6)
    low, high = calculate_histogram_limits(raw_data)
    assert low is None
    assert high < 500


@pytest.mark.parametrize("use_nans", [False, True])
def test_calculate_histogram_limits__constant_arr_values(standard_qsettings, use_nans):
    raw_data = 1.0 * np.ones(100**2)
    if use_nans:
        raw_data[50:60] = np.nan
    standard_qsettings.set_value("user/histogram_outlier_fraction_low", 0.05)
    standard_qsettings.set_value("user/histogram_outlier_fraction_high", 0.05)
    data = raw_data
    low, high = calculate_histogram_limits(data)
    assert abs(low - 1) < 1e-4
    assert abs(high - 1) < 1e-4


def test_calculate_histogram_limits__32bit_data_w_little_variations(standard_qsettings):
    standard_qsettings.set_value("user/histogram_outlier_fraction_low", 0.05)
    standard_qsettings.set_value("user/histogram_outlier_fraction_high", 0.05)

    rng = np.random.default_rng()
    data = rng.normal(5.5, 0.002, 2000).astype(np.float32)
    low, high = calculate_histogram_limits(data)
    assert 5.45 < low < 5.5
    assert 5.5 < high < 5.55


@pytest.mark.parametrize("offset", [0, -500, -5e4, 12000, 120000])
def test_calculate_histogram_limits__no_upper_limit(standard_qsettings, offset):
    raw_data = np.arange(100**2)
    standard_qsettings.set_value("user/histogram_outlier_fraction_low", 0.05)
    standard_qsettings.set_value("user/histogram_outlier_fraction_high", 0)
    data = raw_data + offset
    low, high = calculate_histogram_limits(data)
    assert abs(low - (500 + offset)) < 25
    assert high is None


@pytest.mark.parametrize("offset", [0, -500, -5e4, 12000, 120000])
def test_calculate_histogram_limits__no_lower_limit(standard_qsettings, offset):
    raw_data = np.arange(100**2)
    standard_qsettings.set_value("user/histogram_outlier_fraction_low", 0.0)
    standard_qsettings.set_value("user/histogram_outlier_fraction_high", 0.05)
    data = raw_data + offset
    low, high = calculate_histogram_limits(data)
    assert low is None
    assert abs(high - (9500 + offset)) < 25


@pytest.mark.parametrize("offset", [0, -500, -5e4, 12000, 120000])
def test_calculate_histogram_limits__big_low_outlier(standard_qsettings, offset):
    raw_data = 0.01 * np.arange(1000**2)
    raw_data[0] = -1e6
    standard_qsettings.set_value("user/histogram_outlier_fraction_low", 0.05)
    standard_qsettings.set_value("user/histogram_outlier_fraction_high", 0.05)
    _tolerance = 400 * (1 + abs(offset) / 1e5)
    data = raw_data + offset
    low, high = calculate_histogram_limits(data)
    assert abs(low - (500 + offset)) < _tolerance
    assert abs(high - (9500 + offset)) < _tolerance


if __name__ == "__main__":
    pytest.main()
