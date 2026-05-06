# This file is part of pydidas.
#
# Copyright 2026, Helmholtz-Zentrum Hereon
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

"""Unit tests for silx_plot utility helpers."""

__author__ = "Malte Storm, Nonni Heere"
__copyright__ = "Copyright 2026, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"


import numpy as np
import pytest

from pydidas.core import PydidasQsettings, UserConfigError
from pydidas.unittest_objects import create_dataset
from pydidas.widgets.silx_plot.utilities import (
    axis_is_columns,
    check_data_dimensions,
    get_column_labels,
)


@pytest.fixture(scope="module", autouse=True)
def set_max_number_curves_to_five():
    """Set and restore the user-configured maximum number of displayed curves."""
    _settings = PydidasQsettings()  # type: ignore[arg-type]
    _original = _settings.value("user/max_number_curves", int)
    _settings.set_value("user/max_number_curves", 5)
    yield
    _settings.set_value("user/max_number_curves", _original)


@pytest.fixture
def data():
    return create_dataset(2, shape=(3, 3))


@pytest.mark.parametrize("target_dim", [1, 2, 3])
def test_check_data_dimensions__equal_target_dim(target_dim):
    _data = np.zeros((4,) * target_dim)
    assert check_data_dimensions(_data, target_dim) is None


@pytest.mark.parametrize("data_shape", [(4, 3), (4, 120), (120, 4), (42, 42)])
def test_check_data_dimensions__1d_target_with_2d_data(data_shape):
    _data = np.zeros(data_shape)
    if _data.shape[0] <= 5:
        assert check_data_dimensions(_data, 1) is None
    else:
        with pytest.raises(UserConfigError):
            check_data_dimensions(_data, 1)


@pytest.mark.parametrize("target_dim", [1, 2, 3])
def test_check_data_dimensions__data_too_many_dims(target_dim):
    _data = np.zeros((42,) * (target_dim + 1))
    with pytest.raises(UserConfigError):
        check_data_dimensions(_data, target_dim)


@pytest.mark.parametrize("target_dim", [2, 3])
def test_check_data_dimensions__data_too_few_dims(target_dim):
    _data = np.zeros((42,) * (target_dim - 1))
    with pytest.raises(UserConfigError):
        check_data_dimensions(_data, target_dim)


def test_axis_is_columns__continuous_data(data):
    data.axis_labels = {0: "axis1", 1: "axis2"}
    assert not axis_is_columns(0, data)
    assert not axis_is_columns(1, data)


def test_axis_is_columns__columns(data):
    data.axis_labels = {
        0: "0: test0; 1: test1; 2: test2",
        1: "0: test0; 1: test1; 2: test2",
    }
    assert axis_is_columns(0, data)
    assert axis_is_columns(1, data)


def test_axis_is_columns__malformed_columns(data):
    data.axis_labels = {
        0: "axis1; data: test",
        1: "0: test0; 1: test1",
    }
    assert not axis_is_columns(0, data)
    assert not axis_is_columns(1, data)


def test_get_column_labels(data):
    data.axis_labels = {
        0: "0: test0; 1: test1; 2: test2",
        1: "test3, test4",
    }
    data.axis_units = {0: "", 1: ""}
    assert get_column_labels(0, data) == ["test0", "test1", "test2"]
    assert get_column_labels(1, data) == ["test3, test4"]


if __name__ == "__main__":
    pytest.main([__file__])
#
