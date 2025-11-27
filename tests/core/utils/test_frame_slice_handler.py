# This file is part of pydidas.
#
# Copyright 2025, Helmholtz-Zentrum Hereon
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

"""
Module with the FrameSliceHandler class which allows to manage slicing data in 1 axis.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"


import numpy as np
import pytest

from pydidas.core import UserConfigError
from pydidas.core.utils._frame_slice_handler import FrameSliceHandler


def test_init__w_defaults():
    handler = FrameSliceHandler()
    assert handler.axis is None
    assert handler.frame == 0
    assert handler.shape == ()


@pytest.mark.parametrize(
    "kwargs",
    [
        {"axis": 2},
        {"frame": None},
        {"shape": (2, 4), "axis": 2},
        {"shape": (3, 4), "axis": 1, "frame": 42},
    ],
)
def test_init__w_invalid_values(kwargs):
    with pytest.raises(UserConfigError):
        FrameSliceHandler(**kwargs)


@pytest.mark.parametrize(
    "kwargs",
    [
        {"shape": (3, 4, 5), "axis": 2},
        {"shape": (3, 4, 5), "frame": 2, "axis": 1},
        {"shape": (10, 20)},
    ],
)
def test_init__w_valid_values(kwargs):
    handler = FrameSliceHandler(**kwargs)
    for _key, _value in kwargs.items():
        assert getattr(handler, _key) == _value


@pytest.mark.parametrize("axis", [1, None, np.uint8(0), np.int32(1)])
def test_axis_setter__valid(axis):
    handler = FrameSliceHandler(shape=(3, 4), frame=2)
    handler.axis = axis
    if axis is None:
        assert handler.axis is None
    else:
        assert handler.axis == int(axis)
        assert isinstance(handler.axis, int)
    assert handler.frame == 2


@pytest.mark.parametrize("axis", [-1, 3])
def test_axis_setter__out_of_bounds(axis):
    handler = FrameSliceHandler(shape=(3, 4))
    with pytest.raises(UserConfigError):
        handler.axis = axis


def test_axis_setter__w_frame_reset():
    handler = FrameSliceHandler(shape=(3, 4), frame=3, axis=1)
    with pytest.warns(UserWarning):
        handler.axis = 0
    assert handler.axis == 0
    assert handler.frame == 0


@pytest.mark.parametrize("frame", [0, 2, np.uint8(1), np.int32(1)])
def test_frame_setter__valid(frame):
    handler = FrameSliceHandler(shape=(3, 4), axis=1)
    handler.frame = frame
    assert handler.frame == int(frame)
    assert isinstance(handler.frame, int)


@pytest.mark.parametrize("frame", [-1, 4, 3.3])
def test_frame_setter__out_of_bounds(frame):
    handler = FrameSliceHandler(shape=(3, 4), axis=1)
    with pytest.raises(UserConfigError):
        handler.frame = frame


@pytest.mark.parametrize(
    "shape", [(5, 4), (np.uint8(5), 4), (np.uint64(5), np.int32(4))]
)
def test_shape_setter__valid(shape):
    handler = FrameSliceHandler()
    handler.shape = shape
    assert handler.shape == (5, 4)
    assert isinstance(handler.shape[0], int)
    assert isinstance(handler.shape[1], int)
    assert handler.ndim == 2


def test_shape_setter__with_preselected_axis():
    handler = FrameSliceHandler()
    handler.shape = (5, 4, 6)
    handler.axis = 2
    handler.shape = (2, 3)
    assert handler.shape == (2, 3)
    assert handler.ndim == 2
    assert handler.axis == 0


@pytest.mark.parametrize("shape", [[1, 21], {1, 2}, (5, 0), (3, -2), (4, 2.5)])
def test_shape_setter__invalid(shape):
    handler = FrameSliceHandler()
    with pytest.raises(UserConfigError):
        handler.shape = shape


def test_slice_property__no_axis():
    handler = FrameSliceHandler(shape=(3, 4))
    assert handler.slice == slice(None)


@pytest.mark.parametrize("axis", [0, 1, 2])
def test_slice_property__with_axis(axis):
    handler = FrameSliceHandler(shape=(3, 4, 5), axis=1, frame=2)
    handler.axis = axis
    assert handler.slice == (slice(None),) * axis + (2,)


def test_indices_property__no_axis():
    handler = FrameSliceHandler(shape=(3, 4))
    assert handler.indices is None


@pytest.mark.parametrize("axis", [0, 1, 2])
def test_indices_property__with_axis(axis):
    handler = FrameSliceHandler(shape=(3, 4, 5), axis=1, frame=2)
    handler.axis = axis
    assert handler.indices == (None,) * axis + (2,)


if __name__ == "__main__":
    pytest.main([])
