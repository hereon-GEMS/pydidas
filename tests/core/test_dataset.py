# This file is part of pydidas.
#
# Copyright 2023 - 2026, Helmholtz-Zentrum Hereon
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
__copyright__ = "Copyright 2023 - 2026, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"


import copy
import pickle
import warnings
from numbers import Real
from typing import Any

import numpy as np
import pytest

from pydidas.core import Dataset, PydidasConfigError, UserConfigError
from pydidas.core.utils import rebin2d
from pydidas.core.utils.dataset_utils import get_corresponding_dims
from pydidas.unittest_objects import create_dataset


_np_random_generator = np.random.default_rng()

_AXIS_SLICES = [0, 3, -1, -3, (0,), (2,), (0, 1), (1, 3), (2, 0), (1, 2, 3), (0, 2, 3)]
_IMPLEMENTED_METHODS = ["mean", "sum", "max", "min"]
_METHOD_REQUIRES_INITIAL = ["max", "min"]
_METHOD_TAKES_NO_DTYPE = ["max", "min"]
_METHODS_WITH_DTYPE = [
    _method for _method in _IMPLEMENTED_METHODS if _method not in _METHOD_TAKES_NO_DTYPE
]
_SEPARATORS = ["/", "_", "(", "["]

_SIMPLE_DSET = {
    "labels": ["axis0", "axis1"],
    "ranges": [1, [5, 10]],
    "units": {0: "m", 1: "rad"},
}
_LARGE_DSET = {
    "shape": (10, 12, 14, 16),
    "labels": ["a", "b", "c", "d"],
    "ranges": [np.arange(10), np.arange(12), np.arange(14), np.arange(16)],
    "units": ["ua", "ub", "uc", "ud"],
    "data_label": "data label",
    "data_unit": "data unit",
}
_3X10_AXIS_RANGES = [np.arange(10), 10 - np.arange(10), 3 * np.arange(10)]


def create_simple_dataset() -> Dataset:
    """Create a 1x2 Dataset with simple metadata."""
    return Dataset(
        [[10, 10]],
        axis_labels=_SIMPLE_DSET["labels"],
        axis_ranges=_SIMPLE_DSET["ranges"],
        axis_units=_SIMPLE_DSET["units"],
        metadata={},
    )


def create_large_dataset() -> Dataset:
    """Create a 4-dimensional Dataset with full metadata."""
    return Dataset(
        np.random.random(_LARGE_DSET["shape"]),
        axis_labels=_LARGE_DSET["labels"],
        axis_ranges=_LARGE_DSET["ranges"],
        axis_units=_LARGE_DSET["units"],
        data_label=_LARGE_DSET["data_label"],
        data_unit=_LARGE_DSET["data_unit"],
        metadata={},
    )


def get_random_dataset(ndim: int, shape: tuple[int, ...] | None = None) -> Dataset:
    """Create a Dataset with random data and random axis ranges."""
    if shape is None:
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


def get_large_dset_prop(key: str, indices: tuple[int, ...]) -> list[Any]:
    """Get the selected entries of the large dataset reference property."""
    key = key.removeprefix("axis_")
    return [item for i, item in enumerate(_LARGE_DSET[key]) if i in indices]


def ax_tuple(obj: Dataset, axes: int | tuple[int, ...]) -> tuple[int, ...]:
    """Get the positive axis indices for the given axes."""
    return tuple(
        np.mod(_x, obj.ndim) for _x in (axes if isinstance(axes, tuple) else (axes,))
    )


def as_dict(item: dict | list) -> dict:
    """Convert an iterable of properties to a dict with the dimensions as keys."""
    if isinstance(item, dict):
        return item
    return dict(enumerate(item))


def assert_new_metadata_correct(
    new_array: Dataset, slicing_axes: tuple[int, ...] | list, function_name: str
):
    """Assert that the metadata of a reduced large dataset is correct."""
    assert new_array.data_label == (
        f"{function_name.capitalize()} of " + _LARGE_DSET["data_label"]
    )
    assert new_array.data_unit == _LARGE_DSET["data_unit"]
    for _key in ["axis_labels", "axis_units"]:
        _ref = [
            _item
            for _i, _item in enumerate(_LARGE_DSET[_key[5:]])
            if _i not in slicing_axes
        ]
        assert _ref == list(getattr(new_array, _key).values())
    _ref_ranges = [
        _range
        for _i, _range in enumerate(_LARGE_DSET["ranges"])
        if _i not in slicing_axes
    ]
    for _ref, _new in zip(_ref_ranges, list(new_array.axis_ranges.values())):
        assert np.allclose(_ref, _new)


def assert_reshape_metadata_correct(obj: Dataset):
    """Assert that the metadata of a reshaped large dataset is correct."""
    _dim_matches = get_corresponding_dims(_LARGE_DSET["shape"], obj.shape)
    for _index, _len in enumerate(obj.shape):
        if _index in _dim_matches:
            _original_index = _dim_matches[_index]
            assert obj.axis_labels[_index] == _LARGE_DSET["labels"][_original_index]
            assert obj.axis_units[_index] == _LARGE_DSET["units"][_original_index]
            assert np.allclose(
                obj.axis_ranges[_index], _LARGE_DSET["ranges"][_original_index]
            )
        else:
            assert obj.axis_labels[_index] == ""
            assert obj.axis_units[_index] == ""
            assert np.allclose(obj.axis_ranges[_index], np.arange(_len))


@pytest.fixture
def simple_dataset() -> Dataset:
    return create_simple_dataset()


@pytest.fixture
def large_dataset() -> Dataset:
    return create_large_dataset()


@pytest.mark.parametrize(
    "ds_slice, key_slices, range_slices",
    [
        (0, (1, 2, 3), {}),
        ((slice(None, None), 0), (0, 2, 3), {}),
        ((slice(None, None), 7, 6), (0, 3), {}),
        (slice(1, 4), (0, 1, 2, 3), {0: slice(1, 4)}),
        (np.arange(1, 4), (0, 1, 2, 3), {0: slice(1, 4)}),
    ],
)
def test_array_finalize__simple_indexing(
    large_dataset, ds_slice, key_slices, range_slices
):
    _new = large_dataset[ds_slice]
    for _key in ["axis_labels", "axis_units"]:
        assert list(getattr(_new, _key).values()) == get_large_dset_prop(
            _key, key_slices
        )
    for _new_dim, _original_dim in enumerate(key_slices):
        _new_range = _new.axis_ranges[_new_dim]
        _original_range = _LARGE_DSET["ranges"][_original_dim]
        if _original_dim in range_slices:
            _original_range = _original_range[range_slices[_original_dim]]
        assert np.allclose(_new_range, _original_range)


def test_array_finalize__add_dimension(large_dataset):
    _new = large_dataset[None, :]
    assert list(_new.axis_labels.values()) == [""] + _LARGE_DSET["labels"]
    assert list(_new.axis_units.values()) == [""] + _LARGE_DSET["units"]
    for _dim, _new_range in enumerate(_new.axis_ranges.values()):
        if _dim == 0:
            assert np.allclose(_new_range, np.arange(_new.shape[0]))
        else:
            assert np.allclose(_new_range, _LARGE_DSET["ranges"][_dim - 1])


def test_array_finalize__add_dimension_in_middle(large_dataset):
    _new = large_dataset[:, None, :]
    assert list(_new.axis_labels.values()) == (
        [_LARGE_DSET["labels"][0]] + [""] + _LARGE_DSET["labels"][1:]
    )
    assert list(_new.axis_units.values()) == (
        [_LARGE_DSET["units"][0]] + [""] + _LARGE_DSET["units"][1:]
    )


def test_array_finalize__with_array_mask(large_dataset):
    _mask = np.zeros(large_dataset.shape)
    large_dataset[_mask == 0] = 1
    assert (large_dataset == 1).all()


def test_array_finalize__get_full_masked(large_dataset):
    _mask = np.zeros(large_dataset.shape)
    _new = large_dataset[_mask == 0]
    assert np.allclose(large_dataset.flatten(), _new)


def test_array_finalize__get_masked(large_dataset):
    _mask = np.zeros(large_dataset.shape)
    _mask[1, 1, 1, 1] = 1
    _mask[2, 2, 2, 2] = 1
    _new = large_dataset[_mask == 1]
    _ref = [large_dataset[1, 1, 1, 1], large_dataset[2, 2, 2, 2]]
    assert np.allclose(_ref, _new)
    assert _new.axis_ranges[0].size == 2


def test_array_finalize__get_masked_1d():
    _slice = slice(12, 18)
    obj = create_dataset(1, float, shape=(42,))
    _mask = np.zeros(obj.shape)
    _mask[_slice] = 1
    _new = obj[_mask == 1]
    assert np.allclose(obj[_slice], _new)
    assert _new.axis_ranges[0].size == 6


def test_new__from_array():
    _ndarray = np.random.random((10, 12))
    obj = Dataset(_ndarray)
    assert id(_ndarray) != id(obj)
    assert id(_ndarray) != id(obj.base)


def test_new__assure_memory_not_shared():
    _ndarray = np.random.random((10, 12))
    obj = Dataset(_ndarray)
    _ndarray[0, 0] = 42
    assert obj[0, 0] <= 1


def test_view__assure_memory_shared_in_view():
    obj = Dataset(np.random.random((10, 12)))
    _view = obj[0]
    _view[0] = 42
    assert obj[0, 0] == 42


@pytest.mark.parametrize("base", [[1, 4, 42], (0.5, 7, 1.2)])
def test_new__from_iterable(base):
    obj = Dataset(base)
    for _index, _item in enumerate(base):
        assert obj[_index] == _item


def test_new__from_scalar():
    _val = 42.0
    obj = Dataset(_val)
    assert obj.shape == ()
    assert obj[()] == _val


def test_get_rebinned_copy__bin2(large_dataset):
    _new = large_dataset.get_rebinned_copy(2)
    assert isinstance(_new, Dataset)
    assert id(large_dataset) != id(_new)
    assert tuple(_s // 2 for _s in _LARGE_DSET["shape"]) == _new.shape


def test_get_rebinned_copy__bin1(large_dataset):
    _new = large_dataset.get_rebinned_copy(1)
    assert isinstance(_new, Dataset)
    assert id(large_dataset) != id(_new)
    assert large_dataset.shape == _new.shape


def test_T(large_dataset):
    _new = large_dataset.T
    assert _new.shape == tuple(reversed(large_dataset.shape))
    for _dim, _new_range in _new.axis_ranges.items():
        assert np.allclose(
            _new_range, large_dataset.axis_ranges[large_dataset.ndim - 1 - _dim]
        )


def test_property_dict(large_dataset):
    _obj_props = large_dataset.property_dict
    _copy = large_dataset.property_dict
    _copy["data_unit"] = "42 space"
    assert _obj_props["data_unit"] == large_dataset.data_unit
    assert _copy["data_unit"] != large_dataset.data_unit


def test_flatten(large_dataset):
    _new = large_dataset.flatten()
    assert _new.shape == (large_dataset.size,)
    assert _new.axis_labels == {0: "Flattened"}
    assert _new.axis_units == {0: ""}
    assert np.equal(_new.axis_ranges[0], np.arange(_new.size)).all()


def test_flatten_dims__simple(large_dataset):
    _dims = (1, 2)
    large_dataset.flatten_dims(*_dims)
    assert large_dataset.ndim == len(_LARGE_DSET["shape"]) - 1
    assert large_dataset.axis_labels[_dims[0]] == "Flattened"
    assert large_dataset.axis_units[_dims[0]] == ""
    assert np.allclose(
        large_dataset.axis_ranges[_dims[0]], np.arange(large_dataset.shape[1])
    )


def test_flatten_dims__1dim_only(large_dataset):
    obj2 = copy.copy(large_dataset)
    obj2.flatten_dims(1)
    assert np.equal(large_dataset, obj2).all()


def test_flatten_dims__distributed_dims(large_dataset):
    with pytest.raises(ValueError):
        large_dataset.flatten_dims(1, 3)


def test_flatten_dims__new_label(large_dataset):
    _dims = (1, 2)
    _new_label = "new label"
    large_dataset.flatten_dims(*_dims, new_dim_label=_new_label)
    _labels = [
        _label for _i, _label in enumerate(_LARGE_DSET["labels"]) if _i not in _dims
    ]
    _labels.insert(_dims[0], _new_label)
    assert list(large_dataset.axis_labels.values()) == _labels


def test_flatten_dims__new_unit(large_dataset):
    _dims = (1, 2)
    _new_unit = "new unit"
    large_dataset.flatten_dims(*_dims, new_dim_unit=_new_unit)
    _units = [_unit for _i, _unit in enumerate(_LARGE_DSET["units"]) if _i not in _dims]
    _units.insert(_dims[0], _new_unit)
    assert list(large_dataset.axis_units.values()) == _units


def test_flatten_dims__new_range(large_dataset):
    _dims = (1, 2)
    _new_range = np.arange(
        _LARGE_DSET["shape"][_dims[0]] * _LARGE_DSET["shape"][_dims[1]]
    )
    large_dataset.flatten_dims(*_dims, new_dim_range=_new_range)
    assert np.equal(large_dataset.axis_ranges[_dims[0]], _new_range).all()


def test__comparison_with_allclose(large_dataset):
    _new = np.zeros(large_dataset.shape)
    assert not np.allclose(large_dataset, _new)


def test_array_finalize__multiple_ops(large_dataset):
    _ = large_dataset[0, 0]
    _ = large_dataset[0]
    _new = large_dataset[:, 2]
    assert list(_new.axis_labels.values()) == get_large_dset_prop(
        "axis_labels", (0, 2, 3)
    )
    assert list(_new.axis_units.values()) == get_large_dset_prop(
        "axis_units", (0, 2, 3)
    )
    for _new_dim, _original_dim in enumerate((0, 2, 3)):
        assert np.allclose(
            _new.axis_ranges[_new_dim], _LARGE_DSET["ranges"][_original_dim]
        )


def test_array_finalize__multiple_slicing(large_dataset):
    _new = large_dataset[:, 3:7, 5:10]
    assert list(_new.axis_labels.values()) == _LARGE_DSET["labels"]
    assert list(_new.axis_units.values()) == _LARGE_DSET["units"]
    for _dim, _new_range in enumerate(_new.axis_ranges.values()):
        if _dim == 1:
            assert np.allclose(_new_range, _LARGE_DSET["ranges"][1][3:7])
        elif _dim == 2:
            assert np.allclose(_new_range, _LARGE_DSET["ranges"][2][5:10])
        else:
            assert np.allclose(_new_range, _LARGE_DSET["ranges"][_dim])


def test_array_finalize__reordering():
    obj = get_random_dataset(1)
    _slicer = np.arange(obj.shape[0] - 1, -1, -1)
    _new = obj[_slicer]
    assert _new.axis_labels == obj.axis_labels
    assert _new.axis_units == obj.axis_units
    assert np.allclose(_new.axis_ranges[0], obj.axis_ranges[0][_slicer])
    assert obj.shape == _new.shape


@pytest.mark.parametrize("index", [(2,), (2, 3)])
def test_array_finalize__insert_data(large_dataset, index):
    _new = np.random.random(_LARGE_DSET["shape"][len(index) :])
    large_dataset[index] = _new
    for _key in ["labels", "units"]:
        assert getattr(large_dataset, f"axis_{_key}") == dict(
            enumerate(_LARGE_DSET[_key])
        )


def test_array_finalize__1d_array_w_array_mask():
    obj = get_random_dataset(1)
    indices = np.ones((obj.size), dtype=bool)
    indices[1] = False
    _new = obj[indices]
    assert isinstance(_new, Dataset)
    assert np.allclose(_new, np.append(obj[0], obj[2:]))
    assert _new.axis_ranges[0].size == _new.size


def test_array_finalize__get_single_value(simple_dataset):
    obj = simple_dataset[0]
    _val = obj[0]
    assert isinstance(_val, Real)
    _new = obj[0:2]
    assert _new.axis_labels[0] == obj.axis_labels[0]
    assert np.allclose(_new.axis_ranges[0], obj.axis_ranges[0])


def test__with_rebin2d():
    obj = Dataset(np.random.random((11, 11)), axis_labels=["0", "1"])
    _new = rebin2d(obj, 2)
    assert _new.shape == (5, 5)


def test_transpose__1d():
    obj = Dataset(np.random.random(12), axis_labels=["0"], axis_units=["a"])
    _new = obj.transpose()
    assert obj.axis_labels[0] == _new.axis_labels[0]
    assert obj.axis_units[0] == _new.axis_units[0]
    assert np.allclose(obj.axis_ranges[0], _new.axis_ranges[0])


def test_transpose__2d():
    obj = get_random_dataset(2)
    _new = obj.transpose()
    for _i1, _i2 in [[0, 1], [1, 0]]:
        assert obj.axis_labels[_i1] == _new.axis_labels[_i2]
        assert obj.axis_units[_i1] == _new.axis_units[_i2]
        assert np.allclose(obj.axis_ranges[_i1], _new.axis_ranges[_i2])
    assert np.allclose(obj[0], _new[:, 0])
    assert np.allclose(obj[:, 0], _new[0])


def test_transpose__3d():
    obj = get_random_dataset(3)
    _new = obj.transpose()
    for _i1, _i2 in [[0, 2], [2, 0], [1, 1]]:
        assert obj.axis_labels[_i1] == _new.axis_labels[_i2]
        assert obj.axis_units[_i1] == _new.axis_units[_i2]
        assert np.allclose(obj.axis_ranges[_i1], _new.axis_ranges[_i2])
    assert np.allclose(obj[0, 0], _new[:, 0, 0])
    assert np.allclose(obj[:, 0, 0], _new[0, 0])
    assert np.allclose(obj[0, :, 0], _new[0, :, 0])


def test_transpose__4d():
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
def test_transpose__4d_with_axes(axes_as_tuple):
    obj = get_random_dataset(4)
    _new = obj.transpose((2, 1, 0, 3)) if axes_as_tuple else obj.transpose(2, 1, 0, 3)
    for _i1, _i2 in [[0, 2], [2, 0]]:
        assert obj.axis_labels[_i1] == _new.axis_labels[_i2]
        assert obj.axis_units[_i1] == _new.axis_units[_i2]
        assert np.allclose(obj.axis_ranges[_i1], _new.axis_ranges[_i2])
    assert np.allclose(obj[0, 0, :, 0], _new[:, 0, 0, 0])
    assert np.allclose(obj[:, 0, 0, 0], _new[0, 0, :, 0])
    assert np.allclose(obj[0, :, 0, 0], _new[0, :, 0, 0])


def test_squeeze__single_dim():
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


def test_squeeze__multi_dim():
    obj = get_random_dataset(5, (6, 1, 7, 1, 9))
    _new = np.squeeze(obj)
    for _i1, _i2 in [[0, 0], [2, 1], [4, 2]]:
        assert obj.axis_labels[_i1] == _new.axis_labels[_i2]
        assert obj.axis_units[_i1] == _new.axis_units[_i2]
        assert np.allclose(obj.axis_ranges[_i1], _new.axis_ranges[_i2])
    assert np.allclose(obj[0, 0, 0, 0], _new[0, 0])


def test_squeeze__multi_dims_of_len_1():
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


def test_squeeze__multi_dim_with_None_range():
    obj = get_random_dataset(5, (6, 1, 7, 1, 9))
    obj.update_axis_range(4, None)
    _new = obj.squeeze()
    for _i1, _i2 in [[0, 0], [2, 1], [4, 2]]:
        assert obj.axis_labels[_i1] == _new.axis_labels[_i2]
        assert obj.axis_units[_i1] == _new.axis_units[_i2]
        assert np.allclose(obj.axis_ranges[_i1], _new.axis_ranges[_i2])
    assert np.allclose(obj[0, 0, 0, 0], _new[0, 0])


def test_squeeze__no_dim():
    obj = get_random_dataset(5, (6, 4, 7, 2, 9))
    _new = np.squeeze(obj)
    for _dim in range(5):
        assert obj.axis_labels[_dim] == _new.axis_labels[_dim]
        assert obj.axis_units[_dim] == _new.axis_units[_dim]
        assert np.allclose(obj.axis_ranges[_dim], _new.axis_ranges[_dim])
    assert np.allclose(obj, _new)


def test_squeeze__with_slicing():
    obj = get_random_dataset(5, (6, 4, 7, 1, 9))
    _new = np.squeeze(obj[0:3])
    assert np.allclose(obj.axis_ranges[0][:3], _new.axis_ranges[0])
    for _i1, _i2 in [[1, 1], [2, 2], [4, 3]]:
        assert obj.axis_labels[_i1] == _new.axis_labels[_i2]
        assert obj.axis_units[_i1] == _new.axis_units[_i2]
        assert np.allclose(obj.axis_ranges[_i1], _new.axis_ranges[_i2])
    assert np.allclose(obj[:3, :, :, 0], _new)


def test_take__full_dim_from_3d():
    obj = get_random_dataset(3, (6, 4, 7))
    _new = np.take(obj, 1, 1)
    assert np.allclose(obj[:, 1], _new)
    assert obj.axis_labels[0] == _new.axis_labels[0]
    assert obj.axis_labels[2] == _new.axis_labels[1]
    assert obj.axis_units[0] == _new.axis_units[0]
    assert obj.axis_units[2] == _new.axis_units[1]
    assert np.allclose(obj.axis_ranges[0], _new.axis_ranges[0])
    assert np.allclose(obj.axis_ranges[2], _new.axis_ranges[1])


def test_take__dim_subset_from_3d():
    obj = get_random_dataset(3, (6, 5, 7))
    _new = np.take(obj, (1, 2, 3), 1)
    assert np.allclose(obj[:, slice(1, 4)], _new)
    for _dim in range(3):
        assert obj.axis_labels[_dim] == _new.axis_labels[_dim]
        assert obj.axis_units[_dim] == _new.axis_units[_dim]
        _slice = slice(1, 4) if _dim == 1 else slice(None, None)
        assert np.allclose(obj.axis_ranges[_dim][_slice], _new.axis_ranges[_dim])


def test_take__full_dim_from_2d():
    obj = get_random_dataset(2)
    _new = np.take(obj, 1, 0)
    assert np.allclose(obj[1], _new)
    assert obj.axis_labels[1] == _new.axis_labels[0]
    assert obj.axis_units[1] == _new.axis_units[0]
    assert np.allclose(obj.axis_ranges[1], _new.axis_ranges[0])


def test_take__dim_subset_from_2d():
    obj = get_random_dataset(2)
    _new = np.take(obj, (1, 2, 3), 1)
    assert np.allclose(obj[:, slice(1, 4)], _new)
    for _dim in range(2):
        assert obj.axis_labels[_dim] == _new.axis_labels[_dim]
        assert obj.axis_units[_dim] == _new.axis_units[_dim]
    assert np.allclose(obj.axis_ranges[1][slice(1, 4)], _new.axis_ranges[1])
    assert np.allclose(obj.axis_ranges[0], _new.axis_ranges[0])


def test_take__with_single_iterable_value():
    obj = get_random_dataset(2)
    _new = np.take(obj, [2], 0)
    assert np.allclose(obj[2], _new[0])
    for _dim in range(2):
        assert obj.axis_labels[_dim] == _new.axis_labels[_dim]
        assert obj.axis_units[_dim] == _new.axis_units[_dim]
    assert np.allclose(obj.axis_ranges[0][2], _new.axis_ranges[0])
    assert np.allclose(obj.axis_ranges[1], _new.axis_ranges[1])


def test_take__single_number():
    obj = get_random_dataset(1)
    _new = np.take(obj, 2, 0)
    assert not isinstance(_new, Dataset)
    assert _new == obj[2]


def test_take__1d_array_wo_axis():
    obj = get_random_dataset(1)
    indices = [i for i in range(obj.size) if i != 1]
    _new = np.take(obj, indices)
    assert isinstance(_new, Dataset)
    assert np.allclose(_new, np.append(obj[0], obj[2:]))
    assert _new.axis_ranges[0].size == _new.size


def test_take__2d_array_wo_axis():
    obj = get_random_dataset(2)
    indices = [i for i in range(obj.size) if i != 1]
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        _new = np.take(obj, indices)
    assert isinstance(_new, Dataset)
    assert _new.size == obj.size - 1
    assert _new.ndim == 1
    assert _new.axis_ranges[0].size == _new.size


def test_getitem__simple(large_dataset):
    _new = large_dataset[0, 0]
    assert isinstance(_new, Dataset)


def test_slice__w_tuple(large_dataset):
    _new = large_dataset[:, (1, 2, 3)]
    _new_shape = (large_dataset.shape[0], 3) + (large_dataset.shape[2:])
    assert _new.shape == _new_shape


def test__new__kwargs(simple_dataset):
    assert isinstance(simple_dataset.axis_labels, dict)
    assert isinstance(simple_dataset.axis_ranges, dict)
    assert isinstance(simple_dataset.axis_units, dict)


def test_data_label_property(simple_dataset):
    assert isinstance(simple_dataset.data_label, str)


def test_data_label_property__modify(simple_dataset):
    _new = "new value"
    simple_dataset.data_label = _new
    assert simple_dataset.data_label == _new


def test_data_unit_property(simple_dataset):
    assert isinstance(simple_dataset.data_unit, str)


def test_data_unit_property__modify(simple_dataset):
    _new = "new value"
    simple_dataset.data_unit = _new
    assert simple_dataset.data_unit == _new


@pytest.mark.parametrize("prop_name", ["axis_labels", "axis_units"])
def test_axis_str_property(simple_dataset, prop_name):
    assert getattr(simple_dataset, prop_name) == as_dict(
        _SIMPLE_DSET[prop_name.removeprefix("axis_")]
    )


@pytest.mark.parametrize("prop_name", ["axis_labels", "axis_units"])
def test_axis_str_property__not_str_types(simple_dataset, prop_name):
    with pytest.raises(PydidasConfigError):
        setattr(simple_dataset, prop_name, [["a", "b"], "c", "d"])


@pytest.mark.parametrize("prop_name", ["axis_labels", "axis_units"])
def test_axis_str_property__modify_copy(simple_dataset, prop_name):
    _item = getattr(simple_dataset, prop_name)
    _item[0] = "new value"
    assert getattr(simple_dataset, prop_name) == as_dict(
        _SIMPLE_DSET[prop_name.removeprefix("axis_")]
    )


def test_axis_ranges_property(simple_dataset):
    _ranges_ref = as_dict(_SIMPLE_DSET["ranges"])
    for _dim in range(simple_dataset.ndim):
        assert np.allclose(_ranges_ref[_dim], simple_dataset.axis_ranges[_dim])


def test_axis_ranges_property__modify_copy(simple_dataset):
    _ranges = simple_dataset.axis_ranges
    _ranges[0] = 2 * _ranges[0] - 5
    _ranges_ref = as_dict(_SIMPLE_DSET["ranges"])
    for _dim in range(simple_dataset.ndim):
        assert np.allclose(_ranges_ref[_dim], simple_dataset.axis_ranges[_dim])


@pytest.mark.parametrize("prop_name", ["axis_labels", "axis_units"])
def test_set_axis_str_property(simple_dataset, prop_name):
    _newkeys = ["123", "456"]
    setattr(simple_dataset, prop_name, _newkeys)
    assert getattr(simple_dataset, prop_name) == dict(enumerate(_newkeys))


def test_set_axis_ranges_property__w_single_key(simple_dataset):
    _newkeys = [123, [234, 456]]
    simple_dataset.axis_ranges = _newkeys
    for _dim, _val in simple_dataset.axis_ranges.items():
        assert np.allclose(_val, np.asarray(_newkeys[_dim]))


def test_set_axis_ranges_property__w_none():
    obj = Dataset(np.random.random((20, 20)), axis_ranges=[None, np.arange(20)])
    assert None not in obj.axis_ranges


def test_set_axis_ranges_property__ndarrays_of_correct_len(simple_dataset):
    _newkeys = [np.arange(_len) for _len in simple_dataset.shape]
    simple_dataset.axis_ranges = _newkeys
    assert simple_dataset.axis_ranges == dict(enumerate(_newkeys))


def test_set_axis_ranges_property__lists_of_correct_len(simple_dataset):
    _newkeys = [list(np.arange(_len)) for _len in simple_dataset.shape]
    simple_dataset.axis_ranges = _newkeys
    for _key, _range in simple_dataset.axis_ranges.items():
        assert np.allclose(_range, np.asarray(_newkeys[_key]))


@pytest.mark.parametrize("as_list", [True, False])
def test_set_axis_ranges_property__entries_of_incorrect_len(simple_dataset, as_list):
    _newkeys = [np.arange(_len + 2) for _len in simple_dataset.shape]
    if as_list:
        _newkeys = [list(_key) for _key in _newkeys]
    with pytest.raises(ValueError):
        simple_dataset.axis_ranges = _newkeys


def test_metadata_property(simple_dataset):
    assert simple_dataset.metadata == {}


def test_set_metadata_property(simple_dataset):
    simple_dataset.metadata = None
    assert simple_dataset.property_dict["metadata"] is None


def test_set_metadata_property_w_dict(simple_dataset):
    _meta = {"key0": 123, "key1": -1, 0: "test"}
    simple_dataset.metadata = _meta
    assert simple_dataset.metadata == _meta


def test_set_metadata_property_w_list(simple_dataset):
    with pytest.raises(TypeError):
        simple_dataset.metadata = [1, 2, 4]


def test_array_property(simple_dataset):
    assert isinstance(simple_dataset.array, np.ndarray)


def test_update_axis_range__single_val():
    _val = 12
    obj = Dataset(np.random.random((10, 1, 10)))
    obj.update_axis_range(1, _val)
    assert obj.axis_ranges[1] == _val


def test_update_axis_range__correct_ndarray(large_dataset):
    _val = np.arange(large_dataset.shape[1])
    large_dataset.update_axis_range(1, _val)
    assert np.allclose(large_dataset.axis_ranges[1], _val)


def test_update_axis_range__incorrect_ndarray(large_dataset):
    _val = np.arange(large_dataset.shape[1] + 5)
    with pytest.raises(ValueError):
        large_dataset.update_axis_range(1, _val)


def test_update_axis_label__single_val(large_dataset):
    _val = "a new label"
    large_dataset.update_axis_label(1, _val)
    assert large_dataset.axis_labels[1] == _val


def test_update_axis_label__w_none(large_dataset):
    with pytest.raises(TypeError):
        large_dataset.update_axis_label(1, None)


def test_update_axis_unit__single_val(large_dataset):
    _val = "a new unit"
    large_dataset.update_axis_unit(1, _val)
    assert large_dataset.axis_units[1] == _val


def test_get_description_of_point__wrong_arg_len(large_dataset):
    with pytest.raises(ValueError):
        large_dataset.get_description_of_point((1, 2, 3, 4, 5, 6))


def test_get_description_of_point__simple(large_dataset):
    _str = large_dataset.get_description_of_point((1, 2, 3, 4))
    assert _str == "a: 1.0000 ua; b: 2.0000 ub; c: 3.0000 uc; d: 4.0000 ud"


def test_get_description_of_point__wNone(large_dataset):
    _str = large_dataset.get_description_of_point((None, 2, None, 4))
    assert _str == "b: 2.0000 ub; d: 4.0000 ud"


def test_dataset_creation():
    _array = np.random.random((10, 10, 10))
    obj = Dataset(_array)
    assert isinstance(obj, Dataset)
    assert (obj.array == _array).all()


def test_dataset_creation_with_kwargs():
    _array = np.random.random((10, 10))
    obj = Dataset(
        _array,
        axis_labels=_SIMPLE_DSET["labels"],
        axis_ranges=[np.arange(10), 10 - np.arange(10)],
        axis_units=_SIMPLE_DSET["units"],
        metadata={},
    )
    assert isinstance(obj, Dataset)
    assert isinstance(obj.axis_labels, dict)
    assert isinstance(obj.axis_ranges, dict)
    assert isinstance(obj.axis_units, dict)
    assert isinstance(obj.metadata, dict)


def test_dataset_creation__with_axis_ranges_property_single_values():
    with pytest.raises(PydidasConfigError):
        Dataset(
            np.random.random((10, 10)),
            axis_labels=_SIMPLE_DSET["labels"],
            axis_ranges=[np.arange(10)],
            axis_units=_SIMPLE_DSET["units"],
            metadata={},
        )


def test_dataset_creation__with_axis_ranges_property_ndarrays_of_correct_len():
    obj = Dataset(
        np.random.random((10, 10)),
        axis_labels=_SIMPLE_DSET["labels"],
        axis_ranges=[np.arange(10), 10 - np.arange(10)],
        axis_units=_SIMPLE_DSET["units"],
        metadata={},
    )
    assert isinstance(obj, Dataset)


def test_dataset_creation__with_axis_ranges_property_ndarrays_of_incorrect_len():
    with pytest.raises(ValueError):
        Dataset(
            np.random.random((10, 10)),
            axis_labels=_SIMPLE_DSET["labels"],
            axis_ranges=[np.arange(12), 10 - np.arange(10)],
            axis_units=_SIMPLE_DSET["units"],
            metadata={},
        )


def test_repr__dataset():
    obj = Dataset(np.random.random((10, 10, 10)))
    assert isinstance(repr(obj), str)


def test_repr__empty_dataset():
    obj = Dataset((10, 10, 10))
    assert isinstance(repr(obj), str)


def test_str__():
    obj = Dataset(np.random.random((10, 10, 10)))
    assert isinstance(str(obj), str)


def test_pickling(large_dataset):
    large_dataset.metadata = {"test": "something"}
    _new = pickle.loads(pickle.dumps(large_dataset))
    assert isinstance(_new, Dataset)
    assert np.allclose(_new.array, large_dataset.array)
    assert _new.axis_labels == large_dataset.axis_labels
    assert _new.axis_units == large_dataset.axis_units
    assert _new.metadata == large_dataset.metadata
    assert _new.data_label == large_dataset.data_label
    assert _new.data_unit == large_dataset.data_unit
    for _dim, _range in large_dataset.axis_ranges.items():
        assert np.allclose(_new.axis_ranges[_dim], _range)


def test_pickling__independent_copy(large_dataset):
    _new = pickle.loads(pickle.dumps(large_dataset))
    _new.update_axis_label(0, "new label")
    _new[0, 0, 0, 0] = 42
    assert large_dataset.axis_labels[0] == _LARGE_DSET["labels"][0]
    assert large_dataset[0, 0, 0, 0] != 42


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


def test_np_array__with_ndmin(large_dataset):
    _new = np.array(large_dataset, copy=None, subok=True, ndmin=large_dataset.ndim + 2)
    for _dim in range(large_dataset.ndim):
        assert _new.shape[2 + _dim] == large_dataset.shape[_dim]
        assert _new.axis_labels[2 + _dim] == large_dataset.axis_labels[_dim]
        assert _new.axis_units[2 + _dim] == large_dataset.axis_units[_dim]
        assert np.allclose(_new.axis_ranges[2 + _dim], large_dataset.axis_ranges[_dim])


def test_copy_dataset():
    obj = Dataset(np.random.random((10, 10, 10)), axis_ranges=_3X10_AXIS_RANGES)
    obj.metadata = {"test": "something"}
    obj2 = copy.copy(obj)
    assert np.allclose(obj2.array, obj.array)
    assert obj2.axis_labels == obj.axis_labels
    assert obj2.axis_units == obj.axis_units
    assert obj2.metadata == obj.metadata
    assert obj2.data_label == obj.data_label
    assert obj2.data_unit == obj.data_unit
    for _dim, _range in obj.axis_ranges.items():
        assert np.allclose(obj2.axis_ranges[_dim], _range)


def test_copy_dataset__update_ax_label():
    obj = Dataset(
        np.random.random((10, 10, 10)),
        axis_ranges=_3X10_AXIS_RANGES,
        axis_labels=["a", "b", "c"],
    )
    obj2 = obj.copy()
    obj2.update_axis_label(2, "new")
    assert obj.axis_labels[2] == "c"


def test_hash():
    _ranges = [np.arange(10), 12 - np.arange(10), 3 * np.arange(10) ** 2]
    obj = Dataset(np.zeros((10, 10, 10)), axis_ranges=_ranges[:])
    obj2 = Dataset(np.zeros((10, 10, 10)), axis_ranges=_ranges[:])
    assert isinstance(hash(obj), int)
    assert hash(obj) != hash(obj2)


def test_data_description__no_data_unit(simple_dataset):
    _test_label = "Spam, eggs, sausage and spam"
    simple_dataset.data_label = _test_label
    assert simple_dataset.data_description == _test_label


def test_data_description__w_data_unit(simple_dataset):
    _test_label = "Spam, eggs, sausage and spam"
    _test_unit = "more spam"
    simple_dataset.data_label = _test_label
    simple_dataset.data_unit = _test_unit
    assert simple_dataset.data_description == f"{_test_label} / {_test_unit}"


@pytest.mark.parametrize("sep", _SEPARATORS)
def test_get_data_description__no_unit(simple_dataset, sep):
    assert simple_dataset.get_data_description(sep=sep) == simple_dataset.data_label


@pytest.mark.parametrize("sep", _SEPARATORS)
def test_get_data_description__w_unit(simple_dataset, sep):
    simple_dataset.data_unit = "Tm"
    _label, _unit = simple_dataset.get_data_description(sep=sep).split(sep, 1)
    assert _label.strip() == simple_dataset.data_label
    assert _unit.strip(" )]").strip() == simple_dataset.data_unit


@pytest.mark.parametrize("index", [0, 1])
@pytest.mark.parametrize("sep", _SEPARATORS)
def test_get_axis_description__no_unit(simple_dataset, index, sep):
    simple_dataset.update_axis_unit(index, "")
    _ax_str = simple_dataset.get_axis_description(index, sep=sep)
    assert _ax_str == _SIMPLE_DSET["labels"][index]


@pytest.mark.parametrize("index", [0, 1])
@pytest.mark.parametrize("sep", _SEPARATORS)
def test_get_axis_description__w_unit(simple_dataset, index, sep):
    _ax_str = simple_dataset.get_axis_description(index, sep=sep)
    _label, _unit = _ax_str.split(sep, 1)
    assert _label.strip() == _SIMPLE_DSET["labels"][index]
    assert _unit.strip(" )]").strip() == _SIMPLE_DSET["units"][index]


@pytest.mark.parametrize("method_name", _IMPLEMENTED_METHODS)
def test_np_reimplementation__invalid_kwargs(large_dataset, method_name):
    with pytest.raises(TypeError):
        getattr(large_dataset, method_name)(wrong_key=True)


@pytest.mark.parametrize("method_name", _IMPLEMENTED_METHODS)
def test_np_reimplementation__full(large_dataset, method_name):
    assert (
        getattr(large_dataset, method_name)()
        == getattr(large_dataset.array, method_name)()
    )


@pytest.mark.parametrize("method_name", _IMPLEMENTED_METHODS)
def test_np_reimplementation__none_axis(large_dataset, method_name):
    assert getattr(large_dataset, method_name)(axis=None) == getattr(
        large_dataset.array, method_name
    )(axis=None)


@pytest.mark.parametrize("method_name", _IMPLEMENTED_METHODS)
def test_np_reimplementation__all_axes(large_dataset, method_name):
    assert getattr(large_dataset, method_name)(axis=(0, 1, 2, 3)) == getattr(
        large_dataset.array, method_name
    )(axis=(0, 1, 2, 3))


@pytest.mark.parametrize("axis", _AXIS_SLICES)
@pytest.mark.parametrize("use_np_function", [True, False])
def test_mean__simple(large_dataset, axis, use_np_function):
    _mean = (
        np.mean(large_dataset, axis=axis)
        if use_np_function
        else large_dataset.mean(axis=axis)
    )
    assert np.allclose(_mean, large_dataset.array.mean(axis=axis))
    assert_new_metadata_correct(_mean, ax_tuple(large_dataset, axis), "mean")


@pytest.mark.parametrize("axis", _AXIS_SLICES)
@pytest.mark.parametrize("use_np_function", [True, False])
def test_sum__simple(large_dataset, axis, use_np_function):
    _sum = (
        np.sum(large_dataset, axis=axis)
        if use_np_function
        else large_dataset.sum(axis=axis)
    )
    assert np.allclose(_sum, large_dataset.array.sum(axis=axis))
    assert_new_metadata_correct(_sum, ax_tuple(large_dataset, axis), "sum")


@pytest.mark.parametrize("axis", _AXIS_SLICES)
@pytest.mark.parametrize("method_name", ["max", "mean", "sum"])
def test_np_reimplementation__w_out_ndarray(large_dataset, axis, method_name):
    _ax_tuple = ax_tuple(large_dataset, axis)
    _new_shape = tuple(
        n for i, n in enumerate(large_dataset.shape) if i not in _ax_tuple
    )
    _out = np.zeros(_new_shape)
    getattr(large_dataset, method_name)(axis=axis, out=_out)
    assert np.allclose(_out, getattr(large_dataset.array, method_name)(axis=axis))


@pytest.mark.parametrize("axis", _AXIS_SLICES)
@pytest.mark.parametrize("method_name", _IMPLEMENTED_METHODS)
def test_np_reimplementation__w_out_dataset(large_dataset, axis, method_name):
    _ax_tuple = ax_tuple(large_dataset, axis)
    _new_shape = tuple(
        n for i, n in enumerate(large_dataset.shape) if i not in _ax_tuple
    )
    _out = Dataset(np.zeros(_new_shape))
    getattr(large_dataset, method_name)(axis=axis, out=_out)
    assert np.allclose(_out, getattr(large_dataset.array, method_name)(axis=axis))
    assert_new_metadata_correct(_out, _ax_tuple, method_name)


@pytest.mark.parametrize("method_name", _METHODS_WITH_DTYPE)
def test_np_reimplementation__all_w_dtype(large_dataset, method_name):
    _result = getattr(large_dataset, method_name)(dtype=np.float32)
    assert _result == getattr(large_dataset.array, method_name)(dtype=np.float32)
    assert _result.dtype == np.float32


@pytest.mark.parametrize("axis", _AXIS_SLICES)
@pytest.mark.parametrize("method_name", _METHODS_WITH_DTYPE)
def test_np_reimplementation__w_axis_w_dtype(large_dataset, axis, method_name):
    _result = getattr(large_dataset, method_name)(axis=axis, dtype=np.float32)
    _ref = getattr(large_dataset.array, method_name)(axis=axis, dtype=np.float32)
    assert np.allclose(_result, _ref)
    assert_new_metadata_correct(_result, ax_tuple(large_dataset, axis), method_name)
    assert _result.dtype == np.float32


@pytest.mark.parametrize("axis", _AXIS_SLICES)
@pytest.mark.parametrize("method_name", _IMPLEMENTED_METHODS)
def test_np_reimplementation__w_keepdims(large_dataset, axis, method_name):
    _ax_tuple = ax_tuple(large_dataset, axis)
    _result = getattr(large_dataset, method_name)(axis=axis, keepdims=True)
    _ref = getattr(large_dataset.array, method_name)(axis=axis, keepdims=True)
    assert list(_result.shape) == [
        1 if i in _ax_tuple else n for i, n in enumerate(large_dataset.shape)
    ]
    assert np.allclose(_result, _ref)
    assert_new_metadata_correct(_result, [], method_name)


@pytest.mark.parametrize("axis", _AXIS_SLICES)
@pytest.mark.parametrize("method_name", _IMPLEMENTED_METHODS)
def test_np_reimplementation__w_where(large_dataset, axis, method_name):
    _mask = np.ones(large_dataset.shape, dtype=bool)
    _mask[large_dataset.shape[0] // 2 :] = False
    _kwargs = {"where": _mask} | (
        {"initial": 0} if method_name in _METHOD_REQUIRES_INITIAL else {}
    )
    _result = getattr(large_dataset, method_name)(axis=axis, **_kwargs)
    _ref = getattr(large_dataset.array, method_name)(axis=axis, **_kwargs)
    assert np.allclose(_result[~np.isnan(_result)], _ref[~np.isnan(_result)])
    assert_new_metadata_correct(_result, ax_tuple(large_dataset, axis), method_name)


@pytest.mark.parametrize("axis", _AXIS_SLICES)
def test_nanmean(large_dataset, axis):
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
def test_reshape__simple(large_dataset, axes):
    i0, i1 = axes
    _new_shape = tuple(
        (n if i not in [i0, i1] else n * large_dataset.shape[i1])
        for i, n in enumerate(large_dataset.shape)
        if i != i1
    )
    large_dataset.shape = _new_shape
    assert large_dataset.shape == _new_shape
    assert_reshape_metadata_correct(large_dataset)


def test_reshape__shape_inversion(large_dataset):
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
def test_reshape__complex(large_dataset, new_shape):
    large_dataset.shape = new_shape
    assert large_dataset.shape == new_shape
    assert_reshape_metadata_correct(large_dataset)


@pytest.mark.parametrize("dim", [0, 1, 2, 3])
def test_reshape_w_neg_index(large_dataset, dim):
    _new_shape = list(large_dataset.shape)
    _new_shape[dim] = -1
    large_dataset.shape = _new_shape
    assert large_dataset.shape == _LARGE_DSET["shape"]
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
def test_reshape_w_neg_index__and_reshape(large_dataset, new_shape):
    _size = large_dataset.size
    large_dataset.shape = new_shape
    _missing_dim = _size // np.prod([n for n in new_shape if n != -1])
    assert large_dataset.shape == tuple(
        (n if n != -1 else _missing_dim) for n in new_shape
    )
    assert_reshape_metadata_correct(large_dataset)


def test_reshape__insert_dim(large_dataset):
    _new_shape = (large_dataset.shape[0], 1, 1, *large_dataset.shape[1:])
    large_dataset.shape = _new_shape
    assert large_dataset.shape == _new_shape
    assert_reshape_metadata_correct(large_dataset)


def test_reshape__1d_insert_dim():
    obj = get_random_dataset(1)
    _new = obj.reshape(-1, obj.size)
    assert _new.shape == (1, obj.size)


def test_reshape_1d():
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
def test_repeat(axis):
    obj = get_random_dataset(4)
    _new = obj.repeat(repeats=3, axis=axis)
    for _dim in range(obj.ndim):
        _factor = 3 if _dim == axis else 1
        assert _new.shape[_dim] == obj.shape[_dim] * _factor
    assert _new.axis_labels == obj.axis_labels
    assert _new.axis_units == obj.axis_units


def test_repeat__axis_None():
    obj = get_random_dataset(4)
    _new = obj.repeat(repeats=3, axis=None)
    assert _new.shape == (obj.size * 3,)
    for _iter in [0, 1, 2]:
        assert np.allclose(obj.flatten(), _new.reshape(-1, 3)[:, _iter])


def test_np_array__simple():
    obj = get_random_dataset(1)
    _new = np.array(obj)
    assert np.allclose(obj, _new)
    assert isinstance(_new, np.ndarray)


def test_np_array__w_subok():
    obj = get_random_dataset(3)
    _new = np.array(obj, subok=True)
    assert np.allclose(obj, _new)
    assert isinstance(_new, Dataset)


def test_np_array__w_subok_ndmin():
    obj = get_random_dataset(1)
    _new = np.array(obj, subok=True, ndmin=4)
    assert np.allclose(obj, _new)
    assert isinstance(_new, Dataset)


def test_np_tile():
    obj = get_random_dataset(2)
    assert isinstance(np.tile(obj, (1, 2, 3)), Dataset)


@pytest.mark.parametrize("ndim", [1, 2, 3, 4, 5])
def test_argsort(ndim):
    obj = get_random_dataset(ndim)
    _indices = obj.argsort()
    assert isinstance(_indices, np.ndarray)
    assert not isinstance(_indices, Dataset)
    assert _indices.shape == obj.shape


@pytest.mark.parametrize("axis_kwargs", [{}, {"axis": None}])
def test_sort__1d_np_sort(axis_kwargs):
    obj = get_random_dataset(1, shape=(50,))
    _indices = obj.argsort()
    _range = obj.axis_ranges[0]
    _new = np.sort(obj, **axis_kwargs)
    assert np.allclose(obj[_indices], _new)
    assert np.allclose(_new.axis_ranges[0], _range[_indices])


def test_sort__1d_self_sort():
    obj = get_random_dataset(1, shape=(50,))
    _range = obj.axis_ranges[0]
    _indices = obj.argsort()
    obj.sort()
    assert np.all(np.diff(obj) >= 0)
    assert np.allclose(obj.axis_ranges[0], _range[_indices])


@pytest.mark.parametrize("ndim", [2, 3, 4])
def test_sort__multidim(ndim):
    obj = get_random_dataset(ndim)
    with pytest.raises(UserConfigError):
        obj.sort()


@pytest.mark.parametrize("ndim", [2, 3, 4])
def test_sort__multidim_axis_None(ndim):
    obj = get_random_dataset(ndim)
    obj.sort(axis=None)
    assert np.all(np.diff(obj) >= 0)
    assert obj.shape == (obj.size,)


def test_is_axis_nonlinear__simple(large_dataset):
    for _ax in range(large_dataset.ndim):
        assert not large_dataset.is_axis_nonlinear(_ax)


def test_is_axis_nonlinear__falling_numbers(large_dataset):
    obj = large_dataset[::-1, :, ::-1]
    for _ax in range(obj.ndim):
        assert not obj.is_axis_nonlinear(_ax)


@pytest.mark.parametrize("level", [1e-8, 1e-7, 1e-6, 1e-5, 1e-4, 1e-3, 1e-2, 1e-1])
def test_is_axis_nonlinear__linear_w_jitter(large_dataset, level):
    large_dataset.update_axis_range(
        1,
        np.arange(large_dataset.shape[1])
        + level * np.random.random(large_dataset.shape[1]),
    )
    assert large_dataset.is_axis_nonlinear(1) == (level > 1e-4)
    for _ax in [0, 2, 3]:
        assert not large_dataset.is_axis_nonlinear(_ax)


def test_is_axis_nonlinear__inverse_func(large_dataset):
    large_dataset.update_axis_range(1, 1 / (1 + large_dataset.axis_ranges[1]))
    for _ax in range(large_dataset.ndim):
        assert large_dataset.is_axis_nonlinear(_ax) == (_ax == 1)


def test_is_axis_nonlinear__sine_func(large_dataset):
    large_dataset.update_axis_range(1, np.sin(np.arange(large_dataset.shape[1])))
    for _ax in range(large_dataset.ndim):
        assert large_dataset.is_axis_nonlinear(_ax) == (_ax == 1)
