# This file is part of pydidas.
#
# Copyright 2025 - 2026, Helmholtz-Zentrum Hereon
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

"""Unit tests for column detection in Plot1d and Plot2d widgets."""

__author__ = "Nonni Heere"
__copyright__ = "Copyright 2026, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"


import pytest

from pydidas.unittest_objects import create_dataset
from pydidas.widgets.silx_plot.utilities import axis_is_columns, get_column_labels


@pytest.fixture
def data():
    return create_dataset(2, shape=(3, 3))


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
        1: "test",
    }
    data.axis_units = {0: "", 1: ""}
    assert get_column_labels(0, data) == ["test0", "test1", "test2"]
    with pytest.raises(ValueError):
        get_column_labels(1, data)
