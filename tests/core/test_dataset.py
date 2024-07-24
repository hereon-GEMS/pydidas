# This file is part of pydidas.
#
# Copyright 2023 - 2024, Helmholtz-Zentrum Hereon
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
__copyright__ = "Copyright 2023 - 2024, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"


import copy
import unittest
from numbers import Real

import numpy as np

from pydidas.core import Dataset, PydidasConfigError
from pydidas.core.utils import rebin2d
from pydidas.core.utils.dataset_utils import get_corresponding_dims


_np_random_generator = np.random.default_rng()

_AXIS_SLICES = [0, 3, -1, -3, (0,), (2,), (0, 1), (1, 3), (2, 0), (1, 2, 3), (0, 2, 3)]
_IMPLEMENTED_METHODS = ["mean", "sum", "max", "min"]
_METHOD_TAKES_INT_ONLY = ["cumsum"]
_METHOD_REQUIRES_INITIAL = ["max", "min"]
_METHOD_TAKES_NO_DTYPE = ["max", "min"]


class TestDataset(unittest.TestCase):
    def setUp(self):
        self._axis_labels = ["axis0", "axis1"]
        self._axis_ranges = [1, 10]
        self._axis_units = {0: "m", 1: "rad"}

    def tearDown(self): ...

    def create_simple_dataset(self):
        obj = Dataset(
            [[10, 10]],
            axis_labels=self._axis_labels,
            axis_ranges=self._axis_ranges,
            axis_units=self._axis_units,
            metadata={},
        )
        return obj

    def create_large_dataset(self):
        self._dset = {
            "shape": (10, 12, 14, 16),
            "labels": ["a", "b", "c", "d"],
            "ranges": [np.arange(10), np.arange(12), np.arange(14), np.arange(16)],
            "units": ["ua", "ub", "uc", "ud"],
            "data_label": "data label",
            "data_unit": "data unit",
        }
        obj = Dataset(
            np.random.random(self._dset["shape"]),
            axis_labels=self._dset["labels"],
            axis_ranges=self._dset["ranges"],
            axis_units=self._dset["units"],
            data_label=self._dset["data_label"],
            data_unit=self._dset["data_unit"],
            metadata={},
        )
        return obj

    def get_dset_prop(self, key: str, indices: tuple[int]):
        if key.startswith("axis_"):
            key = key[5:]
        return [item for i, item in enumerate(self._dset[key]) if i in indices]

    def get_random_dataset(self, ndim: int, shape=None):
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

    def ax_tuple(self, obj: Dataset, axes: tuple[int]) -> tuple[int]:
        return tuple(
            np.mod(_x, obj.ndim)
            for _x in (axes if isinstance(axes, tuple) else (axes,))
        )

    def get_dict(self, key):
        if isinstance(getattr(self, key), dict):
            return getattr(self, key)
        return dict(enumerate(getattr(self, key)))

    def test_array_finalize__simple_indexing(self):
        obj = self.create_large_dataset()
        for _ds_slice, _key_slices, _range_slices in [
            [0, (1, 2, 3), {}],
            [(slice(None, None), 0), (0, 2, 3), {}],
            [(slice(None, None), 7, 6), (0, 3), {}],
            [(slice(1, 4)), (0, 1, 2, 3), {0: slice(1, 4)}],
            [np.arange(1, 4), (0, 1, 2, 3), {0: slice(1, 4)}],
        ]:
            with self.subTest(slice=_ds_slice):
                _new = obj[_ds_slice]
                for _key in ["axis_labels", "axis_units"]:
                    self.assertEqual(
                        list(getattr(_new, _key).values()),
                        self.get_dset_prop(f"{_key}", _key_slices),
                    )
                for _new_dim, _original_dim in enumerate(_key_slices):
                    _new_range = _new.axis_ranges[_new_dim]
                    _original_range = self._dset["ranges"][_original_dim]
                    if _original_dim in _range_slices:
                        _original_range = _original_range[_range_slices[_original_dim]]
                    self.assertTrue(np.allclose(_new_range, _original_range))

    def test_array_finalize__add_dimension(self):
        obj = self.create_large_dataset()
        _new = obj[None, :]
        self.assertEqual(list(_new.axis_labels.values()), [""] + self._dset["labels"])
        self.assertEqual(list(_new.axis_units.values()), [""] + self._dset["units"])
        for _dim, _new_range in enumerate(_new.axis_ranges.values()):
            if _dim == 0:
                self.assertTrue(np.allclose(_new_range, np.arange(_new.shape[0])))
            else:
                self.assertTrue(np.allclose(_new_range, self._dset["ranges"][_dim - 1]))

    def test_array_finalize__add_dimension_in_middle(self):
        obj = self.create_large_dataset()
        _new = obj[:, None, :]
        self.assertEqual(
            list(_new.axis_labels.values()),
            [self._dset["labels"][0]] + [""] + self._dset["labels"][1:],
        )
        self.assertEqual(
            list(_new.axis_units.values()),
            [self._dset["units"][0]] + [""] + self._dset["units"][1:],
        )

    def test_array_finalize__with_array_mask(self):
        obj = self.create_large_dataset()
        _mask = np.zeros(obj.shape)
        obj[_mask == 0] = 1
        self.assertTrue((obj == 1).all())

    def test_array_finalize__get_masked(self):
        obj = self.create_large_dataset()
        _mask = np.zeros(obj.shape)
        _new = obj[_mask == 0]
        self.assertTrue(np.allclose(obj.flatten(), _new))

    def test_get_rebinned_copy__bin2(self):
        obj = self.create_large_dataset()
        _new = obj.get_rebinned_copy(2)
        self.assertIsInstance(_new, Dataset)
        self.assertNotEqual(id(obj), id(_new))
        self.assertEqual(tuple(_s // 2 for _s in self._dset["shape"]), _new.shape)

    def test_get_rebinned_copy__bin1(self):
        obj = self.create_large_dataset()
        _new = obj.get_rebinned_copy(1)
        self.assertIsInstance(_new, Dataset)
        self.assertNotEqual(id(obj), id(_new))
        self.assertEqual(obj.shape, _new.shape)

    def test_property_dict(self):
        obj = self.create_large_dataset()
        _obj_props = obj.property_dict
        _copy = obj.property_dict
        _copy["data_unit"] = "42 space"
        self.assertEqual(_obj_props["data_unit"], obj.data_unit)
        self.assertNotEqual(_copy["data_unit"], obj.data_unit)

    def test_flatten(self):
        obj = self.create_large_dataset()
        _new = obj.flatten()
        self.assertEqual(_new.shape, (obj.size,))
        self.assertEqual(_new.axis_labels, {0: "Flattened"})
        self.assertEqual(_new.axis_units, {0: ""})
        self.assertTrue(np.equal(_new.axis_ranges[0], np.arange(_new.size)).all())

    def test_flatten_dims__simple(self):
        _dims = (1, 2)
        obj = self.create_large_dataset()
        obj.flatten_dims(*_dims)
        self.assertEqual(obj.ndim, len(self._dset["shape"]) - 1)
        for key, preset in zip(
            ["axis_labels", "axis_units"],
            ["Flattened", ""],
        ):
            self.assertEqual(getattr(obj, key)[_dims[0]], preset)
        self.assertTrue(np.allclose(obj.axis_ranges[_dims[0]], np.arange(obj.shape[1])))

    def test_flatten_dims__1dim_only(self):
        obj = self.create_large_dataset()
        obj2 = copy.copy(obj)
        obj2.flatten_dims(1)
        self.assertTrue(np.equal(obj, obj2).all())

    def test_flatten_dims__distributed_dims(self):
        obj = self.create_large_dataset()
        with self.assertRaises(ValueError):
            obj.flatten_dims(1, 3)

    def test_flatten_dims__new_label(self):
        _dims = (1, 2)
        obj = self.create_large_dataset()
        obj.flatten_dims(*_dims)
        _new_label = "new label"
        obj = self.create_large_dataset()
        obj.flatten_dims(*_dims, new_dim_label=_new_label)
        _labels = [
            self._dset["labels"][i]
            for i in range(len(self._dset["labels"]))
            if i not in _dims
        ]
        _labels.insert(_dims[0], _new_label)
        self.assertEqual(list(obj.axis_labels.values()), _labels)

    def test_flatten_dims__new_unit(self):
        _dims = (1, 2)
        obj = self.create_large_dataset()
        obj.flatten_dims(*_dims)
        _new_unit = "new unit"
        obj = self.create_large_dataset()
        obj.flatten_dims(*_dims, new_dim_unit=_new_unit)
        _units = [
            self._dset["units"][i]
            for i in range(len(self._dset["units"]))
            if i not in _dims
        ]
        _units.insert(_dims[0], _new_unit)
        self.assertEqual(list(obj.axis_units.values()), _units)

    def test_flatten_dims__new_range(self):
        _dims = (1, 2)
        obj = self.create_large_dataset()
        obj.flatten_dims(*_dims)
        _new_range = np.arange(
            self._dset["shape"][_dims[0]] * self._dset["shape"][_dims[1]]
        )
        obj = self.create_large_dataset()
        obj.flatten_dims(*_dims, new_dim_range=_new_range)
        _range = [
            self._dset["ranges"][i]
            for i in range(len(self._dset["ranges"]))
            if i not in _dims
        ]
        _range.insert(_dims[0], _new_range)
        self.assertTrue(np.equal(obj.axis_ranges[_dims[0]], _new_range).all())

    def test__comparison_with_allclose(self):
        obj = self.create_large_dataset()
        _new = np.zeros((obj.shape))
        self.assertFalse(np.allclose(obj, _new))

    def test_array_finalize__multiple_ops(self):
        obj = self.create_large_dataset()
        _ = obj[0, 0]
        _ = obj[0]
        self.assertEqual(obj._meta["_get_item_key"], ())

    def test_array_finalize__multiple_slicing(self):
        obj = self.create_large_dataset()
        _new = obj[:, 3:7, 5:10]
        self.assertEqual(list(_new.axis_labels.values()), self._dset["labels"])
        self.assertEqual(list(_new.axis_units.values()), self._dset["units"])
        for _dim, _new_range in enumerate(_new.axis_ranges.values()):
            if _dim == 1:
                self.assertTrue(np.allclose(_new_range, self._dset["ranges"][1][3:7]))
            elif _dim == 2:
                self.assertTrue(np.allclose(_new_range, self._dset["ranges"][2][5:10]))
            else:
                self.assertTrue(np.allclose(_new_range, self._dset["ranges"][_dim]))

    def test_array_finalize__insert_data_simple(self):
        obj = self.create_large_dataset()
        _new = np.random.random((12, 14, 16))
        obj[2] = _new

    def test_array_finalize__insert_data(self):
        obj = self.create_large_dataset()
        _new = np.random.random((14, 16))
        obj[2, 3] = _new

    def test_array_finalize__get_single_value(self):
        obj = self.create_simple_dataset()[0]
        _val = obj[0]
        self.assertIsInstance(_val, Real)
        self.assertEqual(obj._meta["_get_item_key"], ())

    def test__with_rebin2d(self):
        obj = Dataset(np.random.random((11, 11)), axis_labels=["0", "1"])
        _new = rebin2d(obj, 2)
        self.assertEqual(_new.shape, (5, 5))

    def test_transpose__1d(self):
        obj = Dataset(np.random.random((12)), axis_labels=["0"], axis_units=["a"])
        _new = obj.transpose()
        self.assertEqual(obj.axis_labels[0], _new.axis_labels[0])
        self.assertEqual(obj.axis_units[0], _new.axis_units[0])
        self.assertTrue(np.allclose(obj.axis_ranges[0], _new.axis_ranges[0]))

    def test_transpose__2d(self):
        obj = self.get_random_dataset(2)
        _new = obj.transpose()
        for _i1, _i2 in [[0, 1], [1, 0]]:
            self.assertEqual(obj.axis_labels[_i1], _new.axis_labels[_i2])
            self.assertEqual(obj.axis_units[_i1], _new.axis_units[_i2])
            self.assertTrue(np.allclose(obj.axis_ranges[_i1], _new.axis_ranges[_i2]))
        self.assertTrue(np.allclose(obj[0], _new[:, 0]))
        self.assertTrue(np.allclose(obj[:, 0], _new[0]))

    def test_transpose__3d(self):
        obj = self.get_random_dataset(3)
        _new = obj.transpose()
        for _i1, _i2 in [[0, 2], [2, 0], [1, 1]]:
            self.assertEqual(obj.axis_labels[_i1], _new.axis_labels[_i2])
            self.assertEqual(obj.axis_units[_i1], _new.axis_units[_i2])
            self.assertTrue(np.allclose(obj.axis_ranges[_i1], _new.axis_ranges[_i2]))
        self.assertTrue(np.allclose(obj[0, 0], _new[:, 0, 0]))
        self.assertTrue(np.allclose(obj[:, 0, 0], _new[0, 0]))
        self.assertTrue(np.allclose(obj[0, :, 0], _new[0, :, 0]))

    def test_transpose__4d(self):
        obj = self.get_random_dataset(4)
        _new = obj.transpose()
        for _i1, _i2 in [[0, 3], [3, 0], [1, 2], [2, 1]]:
            self.assertEqual(obj.axis_labels[_i1], _new.axis_labels[_i2])
            self.assertEqual(obj.axis_units[_i1], _new.axis_units[_i2])
            self.assertTrue(np.allclose(obj.axis_ranges[_i1], _new.axis_ranges[_i2]))
        self.assertTrue(np.allclose(obj[0, 0, 0], _new[:, 0, 0, 0]))
        self.assertTrue(np.allclose(obj[:, 0, 0, 0], _new[0, 0, 0]))
        self.assertTrue(np.allclose(obj[0, :, 0, 0], _new[0, 0, :, 0]))

    def test_transpose__4d_with_axes(self):
        obj = self.get_random_dataset(4)
        _new = obj.transpose(2, 1, 0, 3)
        for _i1, _i2 in [[0, 2], [2, 0]]:
            self.assertEqual(obj.axis_labels[_i1], _new.axis_labels[_i2])
            self.assertEqual(obj.axis_units[_i1], _new.axis_units[_i2])
            self.assertTrue(np.allclose(obj.axis_ranges[_i1], _new.axis_ranges[_i2]))
        self.assertTrue(np.allclose(obj[0, 0, :, 0], _new[:, 0, 0, 0]))
        self.assertTrue(np.allclose(obj[:, 0, 0, 0], _new[0, 0, :, 0]))
        self.assertTrue(np.allclose(obj[0, :, 0, 0], _new[0, :, 0, 0]))

    def test_squeeze__single_dim(self):
        obj = self.get_random_dataset(4)
        obj = obj[:, :, 0:1]
        _new = np.squeeze(obj)
        for _i1, _i2 in [[0, 0], [1, 1], [3, 2]]:
            self.assertEqual(obj.axis_labels[_i1], _new.axis_labels[_i2])
            self.assertEqual(obj.axis_units[_i1], _new.axis_units[_i2])
            self.assertTrue(np.allclose(obj.axis_ranges[_i1], _new.axis_ranges[_i2]))
        self.assertTrue(np.allclose(obj[0, 0, 0], _new[0, 0]))
        self.assertEqual(obj.metadata, _new.metadata)
        self.assertEqual(obj.data_unit, _new.data_unit)

    def test_squeeze__multi_dim(self):
        obj = self.get_random_dataset(5, (6, 1, 7, 1, 9))
        _new = np.squeeze(obj)
        for _i1, _i2 in [[0, 0], [2, 1], [4, 2]]:
            self.assertEqual(obj.axis_labels[_i1], _new.axis_labels[_i2])
            self.assertEqual(obj.axis_units[_i1], _new.axis_units[_i2])
            self.assertTrue(np.allclose(obj.axis_ranges[_i1], _new.axis_ranges[_i2]))
        self.assertTrue(np.allclose(obj[0, 0, 0, 0], _new[0, 0]))

    def test_squeeze__multi_dims_of_len_1(self):
        obj = self.get_random_dataset(5, (1, 1, 7, 1, 1))
        _new = np.squeeze(obj)
        self.assertEqual(obj.axis_labels[2], _new.axis_labels[0])
        self.assertEqual(obj.axis_units[2], _new.axis_units[0])
        self.assertTrue(np.allclose(obj.axis_ranges[2], _new.axis_ranges[0]))
        self.assertTrue(np.allclose(obj[0, 0, :, 0, 0], _new))

    def test_squeeze__multi_dim_size_1(self):
        obj = Dataset([[[[42]]]])
        _new = np.squeeze(obj)
        self.assertEqual(42, _new[0])

    def test_squeeze__multi_dim_with_None_range(self):
        obj = self.get_random_dataset(5, (6, 1, 7, 1, 9))
        obj.update_axis_range(4, None)
        _new = obj.squeeze()
        for _i1, _i2 in [[0, 0], [2, 1], [4, 2]]:
            self.assertEqual(obj.axis_labels[_i1], _new.axis_labels[_i2])
            self.assertEqual(obj.axis_units[_i1], _new.axis_units[_i2])
            self.assertTrue(np.allclose(obj.axis_ranges[_i1], _new.axis_ranges[_i2]))
        self.assertTrue(np.allclose(obj[0, 0, 0, 0], _new[0, 0]))

    def test_squeeze__no_dim(self):
        obj = self.get_random_dataset(5, (6, 4, 7, 2, 9))
        _new = np.squeeze(obj)
        for _i1, _i2 in [[0, 0], [1, 1], [2, 2], [3, 3], [4, 4]]:
            self.assertEqual(obj.axis_labels[_i1], _new.axis_labels[_i2])
            self.assertEqual(obj.axis_units[_i1], _new.axis_units[_i2])
            self.assertTrue(np.allclose(obj.axis_ranges[_i1], _new.axis_ranges[_i2]))
        self.assertTrue(np.allclose(obj, _new))

    def test_squeeze__with_slicing(self):
        obj = self.get_random_dataset(5, (6, 4, 7, 1, 9))
        _new = np.squeeze(obj[0:3])
        self.assertTrue(np.allclose(obj.axis_ranges[0][:3], _new.axis_ranges[0]))
        for _i1, _i2 in [[1, 1], [2, 2], [4, 3]]:
            self.assertEqual(obj.axis_labels[_i1], _new.axis_labels[_i2])
            self.assertEqual(obj.axis_units[_i1], _new.axis_units[_i2])
            self.assertTrue(np.allclose(obj.axis_ranges[_i1], _new.axis_ranges[_i2]))
        self.assertTrue(np.allclose(obj[:3, :, :, 0], _new))

    def test_take__full_dim_from_3d(self):
        obj = self.get_random_dataset(3, (6, 4, 7))
        _dim = 1
        _slice = 1
        _new = np.take(obj, _slice, _dim)
        self.assertTrue(np.allclose(obj[:, 1], _new))
        self.assertEqual(obj.axis_labels[0], _new.axis_labels[0])
        self.assertEqual(obj.axis_labels[2], _new.axis_labels[1])
        self.assertEqual(obj.axis_units[0], _new.axis_units[0])
        self.assertEqual(obj.axis_units[2], _new.axis_units[1])
        self.assertTrue(np.allclose(obj.axis_ranges[0], _new.axis_ranges[0]))
        self.assertTrue(np.allclose(obj.axis_ranges[2], _new.axis_ranges[1]))

    def test_take__dim_subset_from_3d(self):
        obj = self.get_random_dataset(3, (6, 5, 7))
        _dim = 1
        _slice = (1, 2, 3)
        _new = np.take(obj, _slice, _dim)
        self.assertTrue(np.allclose(obj[:, slice(1, 4)], _new))
        for _dim in range(3):
            self.assertEqual(obj.axis_labels[_dim], _new.axis_labels[_dim])
            self.assertEqual(obj.axis_units[_dim], _new.axis_units[_dim])
            _slice = slice(1, 4) if _dim == 1 else slice(None, None)
            self.assertTrue(
                np.allclose(obj.axis_ranges[_dim][_slice], _new.axis_ranges[_dim])
            )

    def test_take__full_dim_from_2d(self):
        obj = self.get_random_dataset(2)
        _dim = 0
        _slice = 1
        _new = np.take(obj, _slice, _dim)
        self.assertTrue(np.allclose(obj[_slice], _new))
        self.assertEqual(obj.axis_labels[1], _new.axis_labels[0])
        self.assertEqual(obj.axis_units[1], _new.axis_units[0])
        self.assertTrue(np.allclose(obj.axis_ranges[1], _new.axis_ranges[0]))

    def test_take__dim_subset_from_2d(self):
        obj = self.get_random_dataset(2)
        _dim = 1
        _slice = (1, 2, 3)
        _new = np.take(obj, _slice, _dim)
        self.assertTrue(np.allclose(obj[:, slice(1, 4)], _new))
        for _dim in range(2):
            self.assertEqual(obj.axis_labels[_dim], _new.axis_labels[_dim])
            self.assertEqual(obj.axis_units[_dim], _new.axis_units[_dim])
        self.assertTrue(
            np.allclose(obj.axis_ranges[1][slice(1, 4)], _new.axis_ranges[1])
        )
        self.assertTrue(np.allclose(obj.axis_ranges[0], _new.axis_ranges[0]))

    def test_take__with_single_iterable_value(self):
        obj = self.get_random_dataset(2)
        _dim = 0
        _slice = [2]
        _new = np.take(obj, _slice, _dim)
        self.assertTrue(np.allclose(obj[2], _new))
        for _dim in range(2):
            self.assertEqual(obj.axis_labels[_dim], _new.axis_labels[_dim])
            self.assertEqual(obj.axis_units[_dim], _new.axis_units[_dim])
        self.assertTrue(np.allclose(obj.axis_ranges[0][_slice[0]], _new.axis_ranges[0]))
        self.assertTrue(np.allclose(obj.axis_ranges[1], _new.axis_ranges[1]))

    def test_take__single_number(self):
        obj = self.get_random_dataset(1)
        _new = np.take(obj, 2, 0)
        self.assertFalse(isinstance(_new, Dataset))
        self.assertEqual(_new, obj[2])

    def test_getitem__simple(self):
        obj = self.create_large_dataset()
        _new = obj.__getitem__((0, 0))
        self.assertIsInstance(_new, Dataset)

    def test_slice__w_tuple(self):
        obj = self.create_large_dataset()
        _new = obj[:, (1, 2, 3)]
        _new_shape = (obj.shape[0], 3) + (obj.shape[2:])
        self.assertEqual(_new.shape, _new_shape)

    def test__new__kwargs(self):
        obj = self.create_simple_dataset()
        self.assertIsInstance(obj.axis_labels, dict)
        self.assertIsInstance(obj.axis_ranges, dict)
        self.assertIsInstance(obj.axis_units, dict)

    def test_data_label_property(self):
        obj = self.create_simple_dataset()
        _label = obj.data_label
        self.assertIsInstance(_label, str)

    def test_data_label_property__modify(self):
        obj = self.create_simple_dataset()
        _new = "new value"
        obj.data_label = _new
        self.assertEqual(obj.data_label, _new)

    def test_data_unit_property(self):
        obj = self.create_simple_dataset()
        _label = obj.data_unit
        self.assertIsInstance(_label, str)

    def test_data_unit_property__modify(self):
        obj = self.create_simple_dataset()
        _new = "new value"
        obj.data_unit = _new
        self.assertEqual(obj.data_unit, _new)

    def test_axis_str_property(self):
        obj = self.create_simple_dataset()
        for _method_name in ["axis_labels", "axis_units"]:
            with self.subTest(method=_method_name):
                self.assertEqual(
                    getattr(obj, _method_name), self.get_dict(f"_{_method_name}")
                )

    def test_axis_str_property__not_str_types(self):
        obj = self.create_simple_dataset()
        _entries = [["a", "b"], "c", "d"]
        for _method_name in ["axis_labels", "axis_units"]:
            with self.subTest(method=_method_name):
                with self.assertRaises(PydidasConfigError):
                    setattr(obj, _method_name, _entries)

    def test_axis_str_property__modify_copy(self):
        obj = self.create_simple_dataset()
        _entries = [["a", "b"], "c", "d"]
        for _method_name in ["axis_labels", "axis_units"]:
            with self.subTest(method=_method_name):
                _item = getattr(obj, _method_name)
                _item[0] = "new value"
                self.assertEqual(
                    getattr(obj, _method_name), self.get_dict(f"_{_method_name}")
                )

    def test_axis_ranges_property(self):
        obj = self.create_simple_dataset()
        self.assertEqual(obj.axis_ranges, self.get_dict("_axis_ranges"))

    def test_axis_ranges_property__modify_copy(self):
        obj = self.create_simple_dataset()
        _ranges = obj.axis_ranges
        _ranges[0] = 2 * _ranges[0] - 5
        self.assertEqual(obj.axis_ranges, self.get_dict("_axis_ranges"))

    def test_set_axis_str_property(self):
        obj = self.create_simple_dataset()
        for _method_name in ["axis_labels", "axis_units"]:
            with self.subTest(method=_method_name):
                _newkeys = ["123", "456"]
                setattr(obj, _method_name, _newkeys)
                self.assertEqual(getattr(obj, _method_name), dict(enumerate(_newkeys)))

    def test_set_axis_ranges_property__single_keys(self):
        obj = self.create_simple_dataset()
        _newkeys = [123, 456]
        obj.axis_ranges = _newkeys
        self.assertEqual(obj.axis_ranges, dict(enumerate(_newkeys)))

    def test_set_axis_ranges_property__w_none(self):
        obj = Dataset(np.random.random((20, 20)), axis_ranges=[None, np.arange(20)])
        self.assertFalse(None in obj.axis_ranges)

    def test_set_axis_ranges_property__ndarrays_of_correct_len(self):
        obj = self.create_simple_dataset()
        _newkeys = [np.arange(_len) for _len in obj.shape]
        obj.axis_ranges = _newkeys
        self.assertEqual(obj.axis_ranges, dict(enumerate(_newkeys)))

    def test_set_axis_ranges_property__lists_of_correct_len(self):
        obj = self.create_simple_dataset()
        _newkeys = [list(np.arange(_len)) for _len in obj.shape]
        obj.axis_ranges = _newkeys
        for _key, _range in obj.axis_ranges.items():
            self.assertTrue(np.allclose(_range, np.asarray(_newkeys[_key])))

    def test_set_axis_ranges_property__ndarrays_of_incorrect_len(self):
        obj = self.create_simple_dataset()
        _newkeys = [np.arange(_len + 2) for _len in obj.shape]
        with self.assertRaises(ValueError):
            obj.axis_ranges = _newkeys

    def test_set_axis_ranges_property__lists_of_incorrect_len(self):
        obj = self.create_simple_dataset()
        _newkeys = [list(np.arange(_len + 2)) for _len in obj.shape]
        with self.assertRaises(ValueError):
            obj.axis_ranges = _newkeys

    def test_metadata_property(self):
        obj = self.create_simple_dataset()
        self.assertEqual(obj.metadata, {})

    def test_set_metadata_property(self):
        obj = self.create_simple_dataset()
        obj.metadata = None

    def test_set_metadata_property_w_dict(self):
        obj = self.create_simple_dataset()
        _meta = {"key0": 123, "key1": -1, 0: "test"}
        obj.metadata = _meta
        self.assertEqual(obj.metadata, _meta)

    def test_set_metadata_property_w_list(self):
        obj = self.create_simple_dataset()
        _meta = [1, 2, 4]
        with self.assertRaises(TypeError):
            obj.metadata = _meta

    def test_array_property(self):
        obj = self.create_simple_dataset()
        self.assertIsInstance(obj.array, np.ndarray)

    def test_update_axis_range__wrong_index(self):
        obj = self.create_large_dataset()
        with self.assertRaises(ValueError):
            obj.update_axis_range(-4, 12)

    def test_update_axis_range__single_val(self):
        _val = 12
        obj = self.create_large_dataset()
        obj.update_axis_range(1, _val)
        self.assertEqual(obj.axis_ranges[1], _val)

    def test_update_axis_range__correct_ndarray(self):
        obj = self.create_large_dataset()
        _val = np.arange(obj.shape[1])
        obj.update_axis_range(1, _val)
        self.assertTrue(np.allclose(obj.axis_ranges[1], _val))

    def test_update_axis_range__incorrect_ndarray(self):
        obj = self.create_large_dataset()
        _val = np.arange(obj.shape[1] + 5)
        with self.assertRaises(ValueError):
            obj.update_axis_range(1, _val)

    def test_update_axis_label__wrong_index(self):
        obj = self.create_large_dataset()
        with self.assertRaises(ValueError):
            obj.update_axis_label(-4, 12)

    def test_update_axis_label__single_val(self):
        _val = "a new label"
        obj = self.create_large_dataset()
        obj.update_axis_label(1, _val)
        self.assertEqual(obj.axis_labels[1], _val)

    def test_update_axis_label__w_none(self):
        obj = self.create_large_dataset()
        with self.assertRaises(ValueError):
            obj.update_axis_label(1, None)

    def test_update_axis_unit__wrong_index(self):
        obj = self.create_large_dataset()
        with self.assertRaises(ValueError):
            obj.update_axis_unit(-4, 12)

    def test_update_axis_unit__single_val(self):
        _val = "a new unit"
        obj = self.create_large_dataset()
        obj.update_axis_unit(1, _val)
        self.assertEqual(obj.axis_units[1], _val)

    def test_get_description_of_point__wrong_arg_len(self):
        obj = self.create_large_dataset()
        with self.assertRaises(ValueError):
            obj.get_description_of_point((1, 2, 3, 4, 5, 6))

    def test_get_description_of_point__simple(self):
        obj = self.create_large_dataset()
        _str = obj.get_description_of_point((1, 2, 3, 4))
        self.assertEqual(_str, "a: 1.0000 ua; b: 2.0000 ub; c: 3.0000 uc; d: 4.0000 ud")

    def test_get_description_of_point__wNone(self):
        obj = self.create_large_dataset()
        _str = obj.get_description_of_point((None, 2, None, 4))
        self.assertEqual(_str, "b: 2.0000 ub; d: 4.0000 ud")

    def test_dataset_creation(self):
        _array = np.random.random((10, 10, 10))
        obj = Dataset(_array)
        self.assertIsInstance(obj, Dataset)
        self.assertTrue((obj.array == _array).all())

    def test_dataset_creation_with_kwargs(self):
        _array = np.random.random((10, 10))
        obj = Dataset(
            _array,
            axis_labels=self._axis_labels,
            axis_ranges=self._axis_ranges,
            axis_units=self._axis_units,
            metadata={},
        )
        self.assertIsInstance(obj, Dataset)
        self.assertIsInstance(obj.axis_labels, dict)
        self.assertIsInstance(obj.axis_ranges, dict)
        self.assertIsInstance(obj.axis_units, dict)
        self.assertIsInstance(obj.metadata, dict)

    def test_dataset_creation__with_axis_ranges_property_single_values(self):
        _array = np.random.random((10, 10))
        obj = Dataset(
            _array,
            axis_labels=self._axis_labels,
            axis_ranges=self._axis_ranges,
            axis_units=self._axis_units,
            metadata={},
        )
        self.assertIsInstance(obj, Dataset)

    def test_dataset_creation__with_axis_ranges_property_ndarrays_of_correct_len(self):
        _array = np.random.random((10, 10))
        obj = Dataset(
            _array,
            axis_labels=self._axis_labels,
            axis_ranges=[np.arange(10), 10 - np.arange(10)],
            axis_units=self._axis_units,
            metadata={},
        )
        self.assertIsInstance(obj, Dataset)

    def test_dataset_creation__with_axis_ranges_property_ndarrays_of_incorrect_len(
        self,
    ):
        _array = np.random.random((10, 10))
        with self.assertRaises(ValueError):
            Dataset(
                _array,
                axis_labels=self._axis_labels,
                axis_ranges=[np.arange(12), 10 - np.arange(10)],
                axis_units=self._axis_units,
                metadata={},
            )

    def test_repr__dataset(self):
        _array = np.random.random((10, 10, 10))
        obj = Dataset(_array)
        self.assertIsInstance(obj.__repr__(), str)

    def test_repr__empty_dataset(self):
        obj = Dataset((10, 10, 10))
        self.assertIsInstance(obj.__repr__(), str)

    def test_str__(self):
        _array = np.random.random((10, 10, 10))
        obj = Dataset(_array)
        self.assertIsInstance(str(obj), str)

    def test_reduce(self):
        _array = np.random.random((10, 10, 10))
        obj = Dataset(_array)
        _array_reduce = _array.__reduce__()
        _obj_reduce = obj.__reduce__()
        self.assertEqual(_array_reduce[0], _obj_reduce[0])
        self.assertIsInstance(_obj_reduce[2][-1], dict)
        for index, item in enumerate(_array_reduce[2]):
            self.assertEqual(_obj_reduce[2][index], item)

    def test_setstate(self):
        _array = np.random.random((10, 10, 10))
        obj = Dataset(_array)
        _obj_state = obj.__reduce__()[2]
        new_obj = Dataset((1))
        new_obj.__setstate__(_obj_state)
        for key in obj.__dict__:
            self.assertEqual(obj.__dict__[key], new_obj.__dict__[key])
        self.assertTrue((new_obj.array == obj.array).all())

    def test_np_amax__simple(self):
        _array = np.random.random((10, 10, 10))
        obj = Dataset(_array)
        _max = np.amax(obj)
        self.assertIsInstance(_max, Real)

    def test_np_amax__with_metadata(self):
        _array = np.random.random((10, 10, 10))
        obj = Dataset(_array)
        obj.metadata = {"test": "something"}
        _max = np.amax(obj)
        self.assertIsInstance(_max, Real)

    def test_np_amax__with_axis_with_metadata(self):
        _array = np.random.random((10, 10, 10))
        obj = Dataset(_array)
        obj.metadata = {"test": "something"}
        _max = np.amax(obj, axis=0)
        self.assertIsInstance(_max, Dataset)
        self.assertEqual(_max.shape, obj.shape[1:])

    def test_copy_dataset(self):
        _array = np.random.random((10, 10, 10))
        obj = Dataset(_array, axis_ranges=[0, 1, 2])
        obj.metadata = {"test": "something"}
        obj2 = copy.copy(obj)
        for _key, _item in obj2.__dict__.items():
            _target = getattr(obj, _key)
            if isinstance(_item, dict):
                for _local_key, _local_item in _item.items():
                    self.assertEqual(_local_item, _target[_local_key])
            else:
                self.assertEqual(_item, _target)

    def test_copy_dataset__update_ax_label(self):
        _array = np.random.random((10, 10, 10))
        obj = Dataset(_array, axis_ranges=[0, 1, 2], axis_labels=["a", "b", "c"])
        obj2 = obj.copy()
        obj2.update_axis_label(2, "new")
        self.assertEqual(obj.axis_labels[2], "c")

    def test_hash(self):
        obj = Dataset(np.zeros((10, 10, 10)), axis_ranges=[0, 1, 2])
        obj2 = Dataset(np.zeros((10, 10, 10)), axis_ranges=[0, 1, 2])
        self.assertIsInstance(hash(obj), int)
        self.assertNotEqual(hash(obj), hash(obj2))

    def test_data_description__no_data_unit(self):
        _test_label = "Spam, eggs, sausage and spam"
        obj = self.create_simple_dataset()
        obj.data_label = _test_label
        self.assertEqual(obj.data_description, _test_label)

    def test_data_description__w_data_unit(self):
        _test_label = "Spam, eggs, sausage and spam"
        _test_unit = "more spam"
        obj = self.create_simple_dataset()
        obj.data_label = _test_label
        obj.data_unit = _test_unit
        self.assertEqual(obj.data_description, f"{_test_label} / {_test_unit}")

    def test_get_axis_description__no_unit(self):
        obj = self.create_simple_dataset()
        for index in range(2):
            with self.subTest(index=index):
                obj.update_axis_unit(index, "")
                _ax_str = obj.get_axis_description(index)
                self.assertEqual(_ax_str, self._axis_labels[index])

    def test_get_axis_description__w_unit(self):
        obj = self.create_simple_dataset()
        for index in range(2):
            with self.subTest(index=index):
                _ax_str = obj.get_axis_description(index)
                self.assertEqual(
                    _ax_str, f"{self._axis_labels[index]} / {self._axis_units[index]}"
                )

    def test_np_reimplementation__invalid_kwargs(self):
        for _method_name in _IMPLEMENTED_METHODS:
            with self.subTest(method=_method_name):
                obj = self.create_large_dataset()
                _method = getattr(obj, _method_name)
                with self.assertRaises(TypeError):
                    _method(wrong_key=True)

    def test_np_reimplementation__full(self):
        for _method_name in _IMPLEMENTED_METHODS:
            with self.subTest(method=_method_name):
                obj = self.create_large_dataset()
                _method = getattr(obj, _method_name)
                _val = _method()
                _ref = getattr(obj.array, _method_name)()
                self.assertEqual(_val, _ref)

    def test_np_reimplementation__none_axis(self):
        for _method_name in _IMPLEMENTED_METHODS:
            with self.subTest(method=_method_name):
                obj = self.create_large_dataset()
                _method = getattr(obj, _method_name)
                _val = _method(axis=None)
                _ref = getattr(obj.array, _method_name)(axis=None)
                self.assertEqual(_val, _ref)

    def test_np_reimplementation__all_axes(self):
        for _method_name in _IMPLEMENTED_METHODS:
            with self.subTest(method=_method_name):
                obj = self.create_large_dataset()
                _method = getattr(obj, _method_name)
                _val = _method(axis=(0, 1, 2, 3))
                _ref = getattr(obj.array, _method_name)(axis=(0, 1, 2, 3))
                self.assertEqual(_val, _ref)

    def test_mean__simple(self):
        obj = self.create_large_dataset()
        for _ax in _AXIS_SLICES:
            for _method, _mean in [
                ("Dataset.mean", obj.mean(axis=_ax)),
                ("np.mean(Dataset)", np.mean(obj, axis=_ax)),
            ]:
                with self.subTest(axis=_ax, method=_method):
                    _ax_tuple = self.ax_tuple(obj, _ax)
                    self.assertTrue(np.allclose(_mean, obj.array.mean(axis=_ax)))
                    self.__assert_new_metadata_correct(_mean, _ax_tuple, "mean")

    def test_sum__simple(self):
        obj = self.create_large_dataset()
        for _ax in _AXIS_SLICES:
            for _method, _sum in [
                ("Dataset.sum", obj.sum(axis=_ax)),
                ("np.sum(Dataset)", np.sum(obj, axis=_ax)),
            ]:
                with self.subTest(axis=_ax, method=_method):
                    _ax_tuple = self.ax_tuple(obj, _ax)
                    self.assertTrue(np.allclose(_sum, obj.array.sum(axis=_ax)))
                    self.__assert_new_metadata_correct(_sum, _ax_tuple, "sum")

    def test_np_reimplementation__w_out_ndarray(self):
        obj = self.create_large_dataset()
        for _method_name in ["max", "mean", "sum"]:
            for _ax in _AXIS_SLICES:
                _ax_tuple = self.ax_tuple(obj, _ax)
                _new_shape = tuple(
                    n for i, n in enumerate(obj.shape) if i not in _ax_tuple
                )
                _out = np.zeros(_new_shape)
                with self.subTest(method=_method_name, axis=_ax):
                    _method = getattr(obj, _method_name)
                    _ = _method(axis=_ax, out=_out)
                    _ref = getattr(obj.array, _method_name)(axis=_ax)
                    self.assertTrue(np.allclose(_out, _ref))

    def test_np_reimplementation__w_out_dataset(self):
        obj = self.create_large_dataset()
        for _method_name in _IMPLEMENTED_METHODS:
            for _ax in _AXIS_SLICES:
                if _method_name in _METHOD_TAKES_INT_ONLY and isinstance(_ax, tuple):
                    continue
                _ax_tuple = self.ax_tuple(obj, _ax)
                _new_shape = tuple(
                    n for i, n in enumerate(obj.shape) if i not in _ax_tuple
                )
                with self.subTest(method=_method_name, axis=_ax):
                    _out = Dataset(np.zeros(_new_shape))
                    _method = getattr(obj, _method_name)
                    _ = _method(axis=_ax, out=_out)
                    _ref = getattr(obj.array, _method_name)(axis=_ax)
                    self.assertTrue(np.allclose(_out, _ref))
                    self.__assert_new_metadata_correct(_out, _ax_tuple, _method_name)

    def test_np_reimplementation__all_w_dtype(self):
        obj = self.create_large_dataset()
        for _method_name in _IMPLEMENTED_METHODS:
            if _method_name in _METHOD_TAKES_NO_DTYPE:
                continue
            with self.subTest(method=_method_name):
                _method = getattr(obj, _method_name)
                _result = _method(dtype=np.float32)
                _ref = getattr(obj.array, _method_name)(dtype=np.float32)
                self.assertEqual(_result, _ref)
                self.assertEqual(_result.dtype, np.float32)

    def test_np_reimplementation__w_axis_w_dtype(self):
        obj = self.create_large_dataset()
        for _method_name in _IMPLEMENTED_METHODS:
            if _method_name in _METHOD_TAKES_NO_DTYPE:
                continue
            for _ax in _AXIS_SLICES:
                if _method_name in _METHOD_TAKES_INT_ONLY and isinstance(_ax, tuple):
                    continue
                _ax_tuple = self.ax_tuple(obj, _ax)
                with self.subTest(method=_method_name, axis=_ax):
                    _method = getattr(obj, _method_name)
                    _result = _method(axis=_ax, dtype=np.float32)
                    _ref = getattr(obj.array, _method_name)(axis=_ax, dtype=np.float32)
                    self.assertTrue(np.allclose(_result, _ref))
                    self.__assert_new_metadata_correct(_result, _ax_tuple, _method_name)
                    self.assertEqual(_result.dtype, np.float32)

    def test_np_reimplementation__w_keepdims(self):
        obj = self.create_large_dataset()
        for _ax in _AXIS_SLICES:
            _ax_tuple = self.ax_tuple(obj, _ax)
            for _method_name in _IMPLEMENTED_METHODS:
                if _method_name in _METHOD_TAKES_INT_ONLY and isinstance(_ax, tuple):
                    continue
                with self.subTest(method=_method_name, axis=_ax):
                    _method = getattr(obj, _method_name)
                    _result = _method(axis=_ax, keepdims=True)
                    _ref = getattr(obj.array, _method_name)(axis=_ax, keepdims=True)
                    self.assertEqual(
                        list(_result.shape),
                        [1 if i in _ax_tuple else n for i, n in enumerate(obj.shape)],
                    )
                    self.assertTrue(np.allclose(_result, _ref))
                    self.__assert_new_metadata_correct(_result, [], _method_name)

    def test_np_reimplementation__w_where(self):
        obj = self.create_large_dataset()
        _mask = np.ones(obj.shape, dtype=bool)
        _mask[obj.shape[0] // 2 :] = False
        for _ax in _AXIS_SLICES:
            _ax_tuple = self.ax_tuple(obj, _ax)
            for _method_name in _IMPLEMENTED_METHODS:
                if _method_name in _METHOD_TAKES_INT_ONLY and isinstance(_ax, tuple):
                    continue
                with self.subTest(method=_method_name, axis=_ax):
                    _method = getattr(obj, _method_name)
                    if _method_name in _METHOD_REQUIRES_INITIAL:
                        _result = _method(axis=_ax, where=_mask, initial=0)
                        _ref = getattr(obj.array, _method_name)(
                            axis=_ax, where=_mask, initial=0
                        )
                    else:
                        _result = _method(axis=_ax, where=_mask)
                        _ref = getattr(obj.array, _method_name)(axis=_ax, where=_mask)
                    self.assertTrue(
                        np.allclose(
                            _result[~np.isnan(_result)], _ref[~np.isnan(_result)]
                        )
                    )
                    self.__assert_new_metadata_correct(_result, _ax_tuple, _method_name)

    def __assert_new_metadata_correct(self, new_array, slicing_axes, function_name):
        self.assertEqual(
            new_array.data_label,
            f"{function_name.capitalize()} of " + self._dset["data_label"],
        )
        self.assertEqual(new_array.data_unit, self._dset["data_unit"])
        for _key in ["axis_labels", "axis_units"]:
            _ref = [
                _item
                for _i, _item in enumerate(self._dset[_key[5:]])
                if _i not in slicing_axes
            ]
            self.assertEqual(_ref, list(getattr(new_array, _key).values()))
        _ref_ranges = [
            _range
            for _i, _range in enumerate(self._dset["ranges"])
            if _i not in slicing_axes
        ]
        _new_ranges = list(new_array.axis_ranges.values())
        for _ref, _new in zip(_ref_ranges, _new_ranges):
            self.assertTrue(np.allclose(_ref, _new))

    def test_nanmean(self):
        obj = self.create_large_dataset()
        obj[0, 0, :, 0] = np.nan
        for _ax in _AXIS_SLICES:
            _ax_tuple = self.ax_tuple(obj, _ax)
            with self.subTest(axis=_ax):
                _result = np.nanmean(obj, axis=_ax)
                self.__assert_new_metadata_correct(_result, _ax_tuple, "sum")

    def test_reshape__syntax(self):
        obj = self.create_large_dataset()
        _shape = (5, 2, 6, 2, 14, 16)
        for _type in ("tuple", "ints"):
            with self.subTest(type=_type):
                if _type == "ints":
                    new = obj.reshape(*_shape)
                elif _type == "tuple":
                    new = obj.reshape(_shape)
                self.assertEqual(new.shape, _shape)

    def test_shape__setter(self):
        obj = self.create_large_dataset()
        _shape = (5, 2, 6, 2, 14, 16)
        obj.shape = _shape
        self.assertEqual(obj.shape, _shape)

    def test_reshape__syntax_flat(self):
        obj = self.create_large_dataset()
        new = obj.reshape(obj.size)
        self.assertEqual(new.shape, (obj.size,))

    def test_reshape__simple(self):
        for i0, i1 in [(0, 1), (1, 2), (2, 3)]:
            with self.subTest(axes=(i0, i1)):
                obj = self.create_large_dataset()
                _new_shape = tuple(
                    (n if i not in [i0, i1] else n * obj.shape[i1])
                    for i, n in enumerate(obj.shape)
                    if i != i1
                )
                obj.shape = _new_shape
                self.assertEqual(obj.shape, _new_shape)
                self.__check_reshape_metadata(obj)

    def test_reshape__shape_inversion(self):
        obj = self.create_large_dataset()
        _new_shape = obj.shape[::-1]
        obj.shape = _new_shape
        self.assertEqual(obj.shape, _new_shape)
        self.__check_reshape_metadata(obj)

    def test_reshape_0d(self):
        obj = Dataset(0)
        new = obj.reshape(1)
        self.assertEqual(new.shape, (1,))

    def test_reshape__complex(self):
        for _new_shape in [
            (5, 2, 6, 2, 14, 16),
            (5, 2, 6, 2, 14, 16),
            (2, 5, 6, 2, 7, 2, 4, 4),
            (10, 7, 12, 2, 16),
            (10, 12, 7, 16, 2),
        ]:
            with self.subTest(shape=_new_shape):
                obj = self.create_large_dataset()
                obj.shape = _new_shape
                self.assertEqual(obj.shape, _new_shape)
                self.__check_reshape_metadata(obj)

    def test_reshape_w_neg_index(self):
        obj = self.create_large_dataset()
        for _dim in range(len(obj.shape)):
            _new_shape = list(obj.shape)
            _new_shape[_dim] = -1
            obj.shape = _new_shape
            self.assertEqual(obj.shape, self._dset["shape"])
            self.__check_reshape_metadata(obj)

    def test_reshape_w_neg_index__and_reshape(self):
        for _new_shape in [
            (5, 2, 6, 2, 14, -1),
            (5, 2, 6, -1, 14, 16),
            (2, 5, 6, 2, -1, 2, 4, 4),
            (10, 7, -1, 2, 16),
            (-1, 12, 7, 16, 2),
        ]:
            with self.subTest(shape=_new_shape):
                obj = self.create_large_dataset()
                obj.shape = _new_shape
                _new_dim = obj.size // np.cumprod([n for n in obj.shape if n != -1])
                _new_final_shape = tuple(
                    (n if n != -1 else _new_dim) for n in obj.shape
                )
                self.assertEqual(obj.shape, _new_final_shape)
                self.__check_reshape_metadata(obj)

    def test_reshape__insert_dim(self):
        obj = self.create_large_dataset()
        _new_shape = (obj.shape[0], 1, 1, *obj.shape[1:])
        obj.shape = _new_shape
        self.assertEqual(obj.shape, _new_shape)
        self.__check_reshape_metadata(obj)

    def __check_reshape_metadata(self, obj):
        _dim_matches = get_corresponding_dims(self._dset["shape"], obj.shape)
        for _index, _len in enumerate(obj.shape):
            if _index in _dim_matches:
                _original_index = _dim_matches[_index]
                self.assertEqual(
                    obj.axis_labels[_index], self._dset["labels"][_original_index]
                )
                self.assertEqual(
                    obj.axis_units[_index], self._dset["units"][_original_index]
                )
                self.assertTrue(
                    np.allclose(
                        obj.axis_ranges[_index], self._dset["ranges"][_original_index]
                    )
                )
            else:
                self.assertEqual(obj.axis_labels[_index], "")
                self.assertEqual(obj.axis_units[_index], "")
                self.assertTrue(np.allclose(obj.axis_ranges[_index], np.arange(_len)))

    def test_reshape__1d_insert_dim(self):
        obj = self.get_random_dataset(1)
        _new = obj.reshape(-1, obj.size)
        self.assertEqual(_new.shape, (1, obj.size))

    def test_reshape_1d(self):
        obj = self.get_random_dataset(1)
        _axlabel = obj.axis_labels[0]
        _axunit = obj.axis_units[0]
        _axrange = obj.axis_ranges[0]
        _new_shape = (1, obj.size)
        obj.shape = _new_shape
        self.assertEqual(obj.shape, _new_shape)
        self.assertEqual(obj.axis_labels, {0: "", 1: _axlabel})
        self.assertEqual(obj.axis_units, {0: "", 1: _axunit})
        self.assertTrue(np.allclose(obj.axis_ranges[0], np.arange(1)))
        self.assertTrue(np.allclose(obj.axis_ranges[1], _axrange))

    def test_repeat(self):
        obj = self.get_random_dataset(4)
        for _ax in range(obj.ndim):
            with self.subTest(axis=_ax):
                _new = obj.repeat(repeats=3, axis=_ax)
                for _dim in range(obj.ndim):
                    if _dim == _ax:
                        self.assertEqual(_new.shape[_dim], obj.shape[_dim] * 3)
                    else:
                        self.assertEqual(_new.shape[_dim], obj.shape[_dim])
                self.assertEqual(_new.axis_labels, obj.axis_labels)
                self.assertEqual(_new.axis_units, obj.axis_units)

    def test_np_array__simple(self):
        obj = self.get_random_dataset(1)
        _new = np.array(obj)
        self.assertTrue(np.allclose(obj, _new))
        self.assertIsInstance(_new, np.ndarray)

    def test_np_array__w_subok(self):
        obj = self.get_random_dataset(3)
        _new = np.array(obj, subok=True)
        self.assertTrue(np.allclose(obj, _new))
        self.assertIsInstance(_new, Dataset)

    def test_np_array__w_subok_ndmin(self):
        obj = self.get_random_dataset(1)
        _new = np.array(obj, subok=True, ndmin=4)
        self.assertTrue(np.allclose(obj, _new))
        self.assertIsInstance(_new, Dataset)

    def test_np_tile(self):
        obj = self.get_random_dataset(2)
        _new = np.tile(obj, (1, 2, 3))

    def test_is_axis_nonlinear__simple(self):
        obj = self.create_large_dataset()
        for _ax in range(obj.ndim):
            self.assertFalse(obj.is_axis_nonlinear(_ax))

    def test_is_axis_nonlinear__falling_numbers(self):
        obj = self.create_large_dataset()
        obj = obj[::-1, :, ::-1]
        for _ax in range(obj.ndim):
            self.assertFalse(obj.is_axis_nonlinear(_ax))

    def test_is_axis_nonlinear__linear_w_jitter(self):
        obj = self.create_large_dataset()
        for _level in [1e-8, 1e-7, 1e-6, 1e-5, 1e-4, 1e-3, 1e-2, 1e-1]:
            with self.subTest(jitter_level=_level):
                obj.update_axis_range(
                    1, np.arange(obj.shape[1]) + _level * np.random.random(obj.shape[1])
                )
            self.assertEqual(obj.is_axis_nonlinear(1), _level > 1e-4)
            for _ax in [0, 2, 3]:
                self.assertFalse(obj.is_axis_nonlinear(_ax))

    def test_is_axis_nonlinear__inverse_func(self):
        obj = self.create_large_dataset()
        obj.update_axis_range(1, 1 / (1 + obj.axis_ranges[1]))
        for _ax in range(obj.ndim):
            self.assertEqual(obj.is_axis_nonlinear(_ax), _ax == 1)

    def test_is_axis_nonlinear__sine_func(self):
        obj = self.create_large_dataset()
        obj.update_axis_range(1, np.sin(np.arange(obj.shape[1])))
        for _ax in range(obj.ndim):
            self.assertEqual(obj.is_axis_nonlinear(_ax), _ax == 1)


if __name__ == "__main__":
    unittest.main()
