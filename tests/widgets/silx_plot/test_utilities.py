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
from pydidas.unittest_objects import SignalSpy, create_dataset
from pydidas.widgets.silx_plot.utilities import (
    axis_is_columns,
    check_data_dimensions,
    get_column_labels,
)


_MALFORMED_LABELS = [
    # Missing separators / punctuation
    "0 item_A; 1: item_B; 2: item_C",
    "0: item_A 1: item_B; 2: item_C",
    "0: item_A; 1 item_B; 2: item_C",
    "0 item_A; 1: item_B 2: item_C",
    # Missing semicolons
    "0: item_A 1: item_B 2: item_C",
    "0: item_A; 1: item_B; 2 item_C",
    # Missing fields
    "0: item_A; 1: item_B",
    "0: item_A; 3: item_D",
    "1: item_B; 2: item_C",
    # Extra tokens
    "0: item_A; 1: item_B; 2: item_C; extra",
    "0: item_A; 1: item_B; something; 2: item_C; 3: item_D",
    "0: item_A; 1: item_B; 2: item_C; 3: unknown",
]
_FORMATTED_LABELS = [
    "0: test0; 1: test1; 2: test2",
    "0: test0; 1: test1: A; 2: test1: B",
    "0: test0 / unitA; 1: test1; 2: test2 / unitC",
    "0: test0 / unitA; 1: test1 / unitA; 2: test2 / unitA",
    "0: test0 / unitC; 1: test0 / unitA; 2: test2 / unitA",
]


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
    _data = create_dataset(2, shape=(3, 3))
    _data.axis_units = {0: "", 1: ""}
    return _data


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


@pytest.mark.parametrize("label", _FORMATTED_LABELS)
def test_axis_is_columns__w_columns(data, label):
    data.update_axis_label(0, label)
    assert axis_is_columns(0, data)


@pytest.mark.parametrize("label", _MALFORMED_LABELS)
def test_axis_is_columns__malformed_columns(data, label):
    data.update_axis_label(0, label)
    assert not axis_is_columns(0, data)


@pytest.mark.parametrize("label", _FORMATTED_LABELS)
def test_get_column_labels(data, label):
    _expectation = [_l.split(":", 1)[1].strip() for _l in label.split(";")]
    data.update_axis_label(0, label)
    data.update_axis_unit(0, "")
    assert get_column_labels(0, data) == _expectation


@pytest.mark.parametrize("label", _MALFORMED_LABELS)
def test_get_column_labels__wrong_formats(qapp, data, label):
    _spy = SignalSpy(qapp.sig_status_message)
    data.update_axis_label(0, label)
    assert _spy.n == 0
    _labels = get_column_labels(0, data)
    assert _spy.n == 1
    assert len(_labels) == data.shape[0]
    assert _labels == [f"column #{index}" for index in range(data.shape[1])]


if __name__ == "__main__":
    pytest.main([__file__])
