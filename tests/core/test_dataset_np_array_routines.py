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

"""Unit tests for pydidas modules."""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2025 - 2026, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"


from numbers import Real

import numpy as np
import pytest

from pydidas.core import Dataset, UserConfigError


_np_random_generator = np.random.default_rng()

_AXIS_SLICES = [0, 3, -1, -3, (0,), (2,), (0, 1), (1, 3), (2, 0), (1, 2, 3), (0, 2, 3)]
_IMPLEMENTED_METHODS = ["mean", "sum", "max", "min"]
_METHOD_TAKES_INT_ONLY = ["cumsum"]
_METHOD_REQUIRES_INITIAL = ["max", "min"]
_METHOD_TAKES_NO_DTYPE = ["max", "min"]

_AX_UNITS = ["m", "rad", "um", "nm^-1", "deg"]
_AX_RANGES = [
    10 - np.arange(10),
    0.1 + 0.2 * np.arange(10) ** 2,
    3 * np.arange(10),
    42 + 2 * np.arange(10),
    1 - 2.4 * np.arange(10),
]


@pytest.fixture
def test_dataset(request):
    ndim = int(request.param)
    return Dataset(
        np.random.random([10] * ndim),
        axis_labels=[f"axis{n}" for n in range(ndim)],
        axis_ranges=_AX_RANGES[:ndim],
        axis_units=_AX_UNITS[:ndim],
    )


@pytest.fixture
def random_dataset(request):
    ndim = int(request.param)
    shape = np.arange(ndim) + 6
    return Dataset(
        _np_random_generator.random(shape),
        axis_labels=[str(i) for i in range(ndim)],
        axis_units=[chr(97 + i) for i in range(ndim)],
        axis_ranges=[
            _np_random_generator.integers(-10, 10)
            + (0.1 + _np_random_generator.random()) * np.arange(shape[_dim])
            for _dim in range(ndim)
        ],
    )


@pytest.mark.parametrize("test_dataset", [2, 3, 4], indirect=True)
def test_roll__no_axis(test_dataset):
    with pytest.warns(UserWarning):
        _new = np.roll(test_dataset, 3)
    assert _new.shape == test_dataset.shape


@pytest.mark.parametrize("test_dataset", [1], indirect=True)
@pytest.mark.parametrize("shift", [-1, 0, 1, 3])
def test_roll__1d_no_axis(test_dataset, shift):
    _new = test_dataset.roll(shift)
    assert _new.shape == test_dataset.shape
    assert _new.axis_labels == test_dataset.axis_labels
    assert np.allclose(_new.axis_ranges[0], np.roll(test_dataset.axis_ranges[0], shift))
    assert _new.axis_units == test_dataset.axis_units


@pytest.mark.parametrize("test_dataset", [3, 4, 5], indirect=True)
@pytest.mark.parametrize("shift", [-1, 0, 1, 3])
@pytest.mark.parametrize("axis", [0, 1, 2])
def test_roll__w_axis(test_dataset, shift, axis):
    _new = test_dataset.roll(shift, axis=axis)
    assert _new.shape == test_dataset.shape
    assert _new.axis_labels == test_dataset.axis_labels
    assert np.allclose(
        _new.axis_ranges[axis], np.roll(test_dataset.axis_ranges[axis], shift)
    )
    assert _new.axis_units == test_dataset.axis_units


def test_T(large_dataset):
    _new = large_dataset.T
    assert _new.shape == tuple(reversed(large_dataset.shape))
    for _dim, _new_range in _new.axis_ranges.items():
        assert np.allclose(
            _new_range, large_dataset.axis_ranges[large_dataset.ndim - 1 - _dim]
        )


def test_flatten(large_dataset):
    _new = large_dataset.flatten()
    assert _new.shape == (large_dataset.size,)
    assert _new.axis_labels == {0: "Flattened"}
    assert _new.axis_units == {0: ""}
    assert np.equal(_new.axis_ranges[0], np.arange(_new.size)).all()


def test_transpose__1d():
    obj = Dataset(np.random.random(12), axis_labels=["0"], axis_units=["a"])
    _new = obj.transpose()
    assert obj.axis_labels[0] == _new.axis_labels[0]
    assert obj.axis_units[0] == _new.axis_units[0]
    assert np.allclose(obj.axis_ranges[0], _new.axis_ranges[0])


def test_transpose__2d(get_random_dataset):
    obj = get_random_dataset(2)
    _new = obj.transpose()
    for _i1, _i2 in [[0, 1], [1, 0]]:
        assert obj.axis_labels[_i1] == _new.axis_labels[_i2]
        assert obj.axis_units[_i1] == _new.axis_units[_i2]
        assert np.allclose(obj.axis_ranges[_i1], _new.axis_ranges[_i2])
    assert np.allclose(obj[0], _new[:, 0])
    assert np.allclose(obj[:, 0], _new[0])


def test_transpose__3d(get_random_dataset):
    obj = get_random_dataset(3)
    _new = obj.transpose()
    for _i1, _i2 in [[0, 2], [2, 0], [1, 1]]:
        assert obj.axis_labels[_i1] == _new.axis_labels[_i2]
        assert obj.axis_units[_i1] == _new.axis_units[_i2]
        assert np.allclose(obj.axis_ranges[_i1], _new.axis_ranges[_i2])
    assert np.allclose(obj[0, 0], _new[:, 0, 0])
    assert np.allclose(obj[:, 0, 0], _new[0, 0])
    assert np.allclose(obj[0, :, 0], _new[0, :, 0])


def test_transpose__4d(get_random_dataset):
    obj = get_random_dataset(4)
    _new = obj.transpose()
    for _i1, _i2 in [[0, 3], [3, 0], [1, 2], [2, 1]]:
        assert obj.axis_labels[_i1] == _new.axis_labels[_i2]
        assert obj.axis_units[_i1] == _new.axis_units[_i2]
        assert np.allclose(obj.axis_ranges[_i1], _new.axis_ranges[_i2])
    assert np.allclose(obj[0, 0, 0], _new[:, 0, 0, 0])
    assert np.allclose(obj[:, 0, 0, 0], _new[0, 0, 0])
    assert np.allclose(obj[0, :, 0, 0], _new[0, 0, :, 0])


@pytest.mark.parametrize("axes_as_tuple", [True, False])
def test_transpose__4d_with_axes(axes_as_tuple, get_random_dataset):
    obj = get_random_dataset(4)
    _new = obj.transpose((2, 1, 0, 3)) if axes_as_tuple else obj.transpose(2, 1, 0, 3)
    for _i1, _i2 in [[0, 2], [2, 0]]:
        assert obj.axis_labels[_i1] == _new.axis_labels[_i2]
        assert obj.axis_units[_i1] == _new.axis_units[_i2]
        assert np.allclose(obj.axis_ranges[_i1], _new.axis_ranges[_i2])
    assert np.allclose(obj[0, 0, :, 0], _new[:, 0, 0, 0])
    assert np.allclose(obj[:, 0, 0, 0], _new[0, 0, :, 0])
    assert np.allclose(obj[0, :, 0, 0], _new[0, :, 0, 0])


def test_squeeze__single_dim(get_random_dataset):
    obj = get_random_dataset(4)
    obj = obj[:, :, 0:1]
    _new = np.squeeze(obj)
    for _i1, _i2 in [[0, 0], [1, 1], [3, 2]]:
        assert obj.axis_labels[_i1] == _new.axis_labels[_i2]
        assert obj.axis_units[_i1] == _new.axis_units[_i2]
        assert np.allclose(obj.axis_ranges[_i1], _new.axis_ranges[_i2])
    assert np.allclose(obj[0, 0, 0], _new[0, 0])
    assert obj.metadata == _new.metadata
    assert obj.data_unit == _new.data_unit


def test_squeeze__multi_dim(get_random_dataset):
    obj = get_random_dataset(5, (6, 1, 7, 1, 9))
    _new = np.squeeze(obj)
    for _i1, _i2 in [[0, 0], [2, 1], [4, 2]]:
        assert obj.axis_labels[_i1] == _new.axis_labels[_i2]
        assert obj.axis_units[_i1] == _new.axis_units[_i2]
        assert np.allclose(obj.axis_ranges[_i1], _new.axis_ranges[_i2])
    assert np.allclose(obj[0, 0, 0, 0], _new[0, 0])


def test_squeeze__multi_dims_of_len_1(get_random_dataset):
    obj = get_random_dataset(5, (1, 1, 7, 1, 1))
    _new = np.squeeze(obj)
    assert obj.axis_labels[2] == _new.axis_labels[0]
    assert obj.axis_units[2] == _new.axis_units[0]
    assert np.allclose(obj.axis_ranges[2], _new.axis_ranges[0])
    assert np.allclose(obj[0, 0, :, 0, 0], _new)


def test_squeeze__multi_dim_size_1():
    obj = Dataset([[[[42]]]])
    _new = np.squeeze(obj)
    assert _new[0] == 42


def test_squeeze__multi_dim_with_None_range(get_random_dataset):
    obj = get_random_dataset(5, (6, 1, 7, 1, 9))
    obj.update_axis_range(4, None)
    _new = obj.squeeze()
    for _i1, _i2 in [[0, 0], [2, 1], [4, 2]]:
        assert obj.axis_labels[_i1] == _new.axis_labels[_i2]
        assert obj.axis_units[_i1] == _new.axis_units[_i2]
        assert np.allclose(obj.axis_ranges[_i1], _new.axis_ranges[_i2])
    assert np.allclose(obj[0, 0, 0, 0], _new[0, 0])


def test_squeeze__no_dim(get_random_dataset):
    obj = get_random_dataset(5, (6, 4, 7, 2, 9))
    _new = np.squeeze(obj)
    for _dim in range(5):
        assert obj.axis_labels[_dim] == _new.axis_labels[_dim]
        assert obj.axis_units[_dim] == _new.axis_units[_dim]
        assert np.allclose(obj.axis_ranges[_dim], _new.axis_ranges[_dim])
    assert np.allclose(obj, _new)


def test_squeeze__with_slicing(get_random_dataset):
    obj = get_random_dataset(5, (6, 4, 7, 1, 9))
    _new = np.squeeze(obj[0:3])
    assert np.allclose(obj.axis_ranges[0][:3], _new.axis_ranges[0])
    for _i1, _i2 in [[1, 1], [2, 2], [4, 3]]:
        assert obj.axis_labels[_i1] == _new.axis_labels[_i2]
        assert obj.axis_units[_i1] == _new.axis_units[_i2]
        assert np.allclose(obj.axis_ranges[_i1], _new.axis_ranges[_i2])
    assert np.allclose(obj[:3, :, :, 0], _new)


def test_take__full_dim_from_3d(get_random_dataset):
    obj = get_random_dataset(3, (6, 4, 7))
    _new = np.take(obj, 1, 1)
    assert np.allclose(obj[:, 1], _new)
    assert obj.axis_labels[0] == _new.axis_labels[0]
    assert obj.axis_labels[2] == _new.axis_labels[1]
    assert obj.axis_units[0] == _new.axis_units[0]
    assert obj.axis_units[2] == _new.axis_units[1]
    assert np.allclose(obj.axis_ranges[0], _new.axis_ranges[0])
    assert np.allclose(obj.axis_ranges[2], _new.axis_ranges[1])


def test_take__dim_subset_from_3d(get_random_dataset):
    obj = get_random_dataset(3, (6, 5, 7))
    _new = np.take(obj, (1, 2, 3), 1)
    assert np.allclose(obj[:, slice(1, 4)], _new)
    for _dim in range(3):
        assert obj.axis_labels[_dim] == _new.axis_labels[_dim]
        assert obj.axis_units[_dim] == _new.axis_units[_dim]
        _slice = slice(1, 4) if _dim == 1 else slice(None, None)
        assert np.allclose(obj.axis_ranges[_dim][_slice], _new.axis_ranges[_dim])


def test_take__full_dim_from_2d(get_random_dataset):
    obj = get_random_dataset(2)
    _new = np.take(obj, 1, 0)
    assert np.allclose(obj[1], _new)
    assert obj.axis_labels[1] == _new.axis_labels[0]
    assert obj.axis_units[1] == _new.axis_units[0]
    assert np.allclose(obj.axis_ranges[1], _new.axis_ranges[0])


def test_take__dim_subset_from_2d(get_random_dataset):
    obj = get_random_dataset(2)
    _new = np.take(obj, (1, 2, 3), 1)
    assert np.allclose(obj[:, slice(1, 4)], _new)
    for _dim in range(2):
        assert obj.axis_labels[_dim] == _new.axis_labels[_dim]
        assert obj.axis_units[_dim] == _new.axis_units[_dim]
    assert np.allclose(obj.axis_ranges[1][slice(1, 4)], _new.axis_ranges[1])
    assert np.allclose(obj.axis_ranges[0], _new.axis_ranges[0])


def test_take__with_single_iterable_value(get_random_dataset):
    obj = get_random_dataset(2)
    _new = np.take(obj, [2], 0)
    assert np.allclose(obj[2], _new[0])
    for _dim in range(2):
        assert obj.axis_labels[_dim] == _new.axis_labels[_dim]
        assert obj.axis_units[_dim] == _new.axis_units[_dim]
    assert np.allclose(obj.axis_ranges[0][2], _new.axis_ranges[0])
    assert np.allclose(obj.axis_ranges[1], _new.axis_ranges[1])


def test_take__single_number(get_random_dataset):
    obj = get_random_dataset(1)
    _new = np.take(obj, 2, 0)
    assert not isinstance(_new, Dataset)
    assert _new == obj[2]


def test_take__1d_array_wo_axis(get_random_dataset):
    obj = get_random_dataset(1)
    indices = [i for i in range(obj.size) if i != 1]
    _new = np.take(obj, indices)
    assert isinstance(_new, Dataset)
    assert np.allclose(_new, np.append(obj[0], obj[2:]))
    assert _new.axis_ranges[0].size == _new.size


def test_take__2d_array_wo_axis(get_random_dataset):
    obj = get_random_dataset(2)
    indices = [i for i in range(obj.size) if i != 1]
    with pytest.warns(UserWarning, match="does not match the number of dimensions"):
        _new = np.take(obj, indices)
    assert isinstance(_new, Dataset)
    assert _new.size == obj.size - 1
    assert _new.ndim == 1
    with pytest.warns(UserWarning, match="Resetting the axis_ranges"):
        assert _new.axis_ranges[0].size == _new.size


def test_np_amax__simple():
    obj = Dataset(np.random.random((10, 10, 10)))
    assert isinstance(np.amax(obj), Real)


def test_np_amax__with_metadata():
    obj = Dataset(np.random.random((10, 10, 10)))
    obj.metadata = {"test": "something"}
    assert isinstance(np.amax(obj), Real)


def test_np_amax__with_axis_with_metadata():
    obj = Dataset(np.random.random((10, 10, 10)))
    obj.metadata = {"test": "something"}
    _max = np.amax(obj, axis=0)
    assert isinstance(_max, Dataset)
    assert _max.shape == obj.shape[1:]


@pytest.mark.parametrize("axis", _AXIS_SLICES)
@pytest.mark.parametrize("use_np_function", [True, False])
def test_mean__simple(
    large_dataset, axis, use_np_function, assert_new_metadata_correct, ax_tuple
):
    _mean = (
        np.mean(large_dataset, axis=axis)
        if use_np_function
        else large_dataset.mean(axis=axis)
    )
    assert np.allclose(_mean, large_dataset.array.mean(axis=axis))
    assert_new_metadata_correct(_mean, ax_tuple(large_dataset, axis), "mean")


@pytest.mark.parametrize("axis", _AXIS_SLICES)
@pytest.mark.parametrize("use_np_function", [True, False])
def test_sum__simple(
    large_dataset, axis, use_np_function, assert_new_metadata_correct, ax_tuple
):
    _sum = (
        np.sum(large_dataset, axis=axis)
        if use_np_function
        else large_dataset.sum(axis=axis)
    )
    assert np.allclose(_sum, large_dataset.array.sum(axis=axis))
    assert_new_metadata_correct(_sum, ax_tuple(large_dataset, axis), "sum")


@pytest.mark.parametrize("axis", _AXIS_SLICES)
def test_nanmean(large_dataset, axis, assert_new_metadata_correct, ax_tuple):
    large_dataset[0, 0, :, 0] = np.nan
    _result = np.nanmean(large_dataset, axis=axis)
    assert_new_metadata_correct(_result, ax_tuple(large_dataset, axis), "sum")


@pytest.mark.parametrize("shape_as_tuple", [True, False])
def test_reshape__syntax(large_dataset, shape_as_tuple):
    _shape = (5, 2, 6, 2, 14, 16)
    _new = (
        large_dataset.reshape(_shape)
        if shape_as_tuple
        else large_dataset.reshape(*_shape)
    )
    assert _new.shape == _shape


def test_shape__setter(large_dataset):
    _shape = (5, 2, 6, 2, 14, 16)
    large_dataset.shape = _shape
    assert large_dataset.shape == _shape


def test_reshape__syntax_flat(large_dataset):
    _new = large_dataset.reshape(large_dataset.size)
    assert _new.shape == (large_dataset.size,)


@pytest.mark.parametrize("axes", [(0, 1), (1, 2), (2, 3)])
def test_reshape__simple(large_dataset, axes, assert_reshape_metadata_correct):
    i0, i1 = axes
    _new_shape = tuple(
        (n if i not in [i0, i1] else n * large_dataset.shape[i1])
        for i, n in enumerate(large_dataset.shape)
        if i != i1
    )
    large_dataset.shape = _new_shape
    assert large_dataset.shape == _new_shape
    assert_reshape_metadata_correct(large_dataset)


def test_reshape__shape_inversion(large_dataset, assert_reshape_metadata_correct):
    _new_shape = large_dataset.shape[::-1]
    large_dataset.shape = _new_shape
    assert large_dataset.shape == _new_shape
    assert_reshape_metadata_correct(large_dataset)


def test_reshape_0d():
    obj = Dataset(0)
    assert obj.reshape(1).shape == (1,)


@pytest.mark.parametrize(
    "new_shape",
    [
        (5, 2, 6, 2, 14, 16),
        (2, 5, 6, 2, 7, 2, 4, 4),
        (10, 7, 12, 2, 16),
        (10, 12, 7, 16, 2),
    ],
)
def test_reshape__complex(large_dataset, new_shape, assert_reshape_metadata_correct):
    large_dataset.shape = new_shape
    assert large_dataset.shape == new_shape
    assert_reshape_metadata_correct(large_dataset)


@pytest.mark.parametrize("dim", [0, 1, 2, 3])
def test_reshape_w_neg_index(
    large_dataset, dim, assert_reshape_metadata_correct, large_dataset_reference
):
    _new_shape = list(large_dataset.shape)
    _new_shape[dim] = -1
    large_dataset.shape = _new_shape
    assert large_dataset.shape == large_dataset_reference["shape"]
    assert_reshape_metadata_correct(large_dataset)


@pytest.mark.parametrize(
    "new_shape",
    [
        (5, 2, 6, 2, 14, -1),
        (5, 2, 6, -1, 14, 16),
        (2, 5, 6, 2, -1, 2, 4, 4),
        (10, 7, -1, 2, 16),
        (-1, 12, 7, 16, 2),
    ],
)
def test_reshape_w_neg_index__and_reshape(
    large_dataset, new_shape, assert_reshape_metadata_correct
):
    _size = large_dataset.size
    large_dataset.shape = new_shape
    _missing_dim = _size // np.prod([n for n in new_shape if n != -1])
    assert large_dataset.shape == tuple(
        (n if n != -1 else _missing_dim) for n in new_shape
    )
    assert_reshape_metadata_correct(large_dataset)


def test_reshape__insert_dim(large_dataset, assert_reshape_metadata_correct):
    _new_shape = (large_dataset.shape[0], 1, 1, *large_dataset.shape[1:])
    large_dataset.shape = _new_shape
    assert large_dataset.shape == _new_shape
    assert_reshape_metadata_correct(large_dataset)


def test_reshape__1d_insert_dim(get_random_dataset):
    obj = get_random_dataset(1)
    _new = obj.reshape(-1, obj.size)
    assert _new.shape == (1, obj.size)


def test_reshape_1d(get_random_dataset):
    obj = get_random_dataset(1)
    _axlabel = obj.axis_labels[0]
    _axunit = obj.axis_units[0]
    _axrange = obj.axis_ranges[0]
    _new_shape = (1, obj.size)
    obj.shape = _new_shape
    assert obj.shape == _new_shape
    assert obj.axis_labels == {0: "", 1: _axlabel}
    assert obj.axis_units == {0: "", 1: _axunit}
    assert np.allclose(obj.axis_ranges[0], np.arange(1))
    assert np.allclose(obj.axis_ranges[1], _axrange)


@pytest.mark.parametrize("axis", [0, 1, 2, 3])
def test_repeat(axis, get_random_dataset):
    obj = get_random_dataset(4)
    _new = obj.repeat(repeats=3, axis=axis)
    for _dim in range(obj.ndim):
        _factor = 3 if _dim == axis else 1
        assert _new.shape[_dim] == obj.shape[_dim] * _factor
    assert _new.axis_labels == obj.axis_labels
    assert _new.axis_units == obj.axis_units


def test_repeat__axis_None(get_random_dataset):
    obj = get_random_dataset(4)
    _new = obj.repeat(repeats=3, axis=None)
    assert _new.shape == (obj.size * 3,)
    for _iter in [0, 1, 2]:
        assert np.allclose(obj.flatten(), _new.reshape(-1, 3)[:, _iter])


def test_np_tile(get_random_dataset):
    obj = get_random_dataset(2)
    assert isinstance(np.tile(obj, (1, 2, 3)), Dataset)


@pytest.mark.parametrize("ndim", [1, 2, 3, 4, 5])
def test_argsort(ndim, get_random_dataset):
    obj = get_random_dataset(ndim)
    _indices = obj.argsort()
    assert isinstance(_indices, np.ndarray)
    assert not isinstance(_indices, Dataset)
    assert _indices.shape == obj.shape


@pytest.mark.parametrize("axis_kwargs", [{}, {"axis": None}])
def test_sort__1d_np_sort(axis_kwargs, get_random_dataset):
    obj = get_random_dataset(1, shape=(50,))
    _indices = obj.argsort()
    _range = obj.axis_ranges[0]
    _new = np.sort(obj, **axis_kwargs)
    assert np.allclose(obj[_indices], _new)
    assert np.allclose(_new.axis_ranges[0], _range[_indices])


def test_sort__1d_self_sort(get_random_dataset):
    obj = get_random_dataset(1, shape=(50,))
    _range = obj.axis_ranges[0]
    _indices = obj.argsort()
    obj.sort()
    assert np.all(np.diff(obj) >= 0)
    assert np.allclose(obj.axis_ranges[0], _range[_indices])


@pytest.mark.parametrize("ndim", [2, 3, 4])
def test_sort__multidim(ndim, get_random_dataset):
    obj = get_random_dataset(ndim)
    with pytest.raises(UserConfigError):
        obj.sort()


@pytest.mark.parametrize("ndim", [2, 3, 4])
def test_sort__multidim_axis_None(ndim, get_random_dataset):
    obj = get_random_dataset(ndim)
    obj.sort(axis=None)
    assert np.all(np.diff(obj) >= 0)
    assert obj.shape == (obj.size,)


if __name__ == "__main__":
    pytest.main([__file__])
