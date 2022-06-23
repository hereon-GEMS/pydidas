# This file is part of pydidas.
#
# pydidas is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
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
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"


import copy
import unittest
from numbers import Real

import numpy as np

from pydidas.core.dataset import Dataset, EmptyDataset
from pydidas.core.utils import rebin2d


class TestDataset(unittest.TestCase):
    def setUp(self):
        self._axis_labels = ["axis0", "axis1"]
        self._axis_ranges = [1, 10]
        self._axis_units = {0: "m", 1: "rad"}

    def tearDown(self):
        ...

    def create_empty_dataset(self):
        obj = EmptyDataset(
            (10, 10),
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
        }
        obj = Dataset(
            np.random.random(self._dset["shape"]),
            axis_labels=self._dset["labels"],
            axis_ranges=self._dset["ranges"],
            axis_units=self._dset["units"],
            metadata={},
        )
        return obj

    def get_dict(self, key):
        if isinstance(getattr(self, key), dict):
            return getattr(self, key)
        return dict(enumerate(getattr(self, key)))

    def test_empty_dataset_new(self):
        obj = EmptyDataset((10, 10))
        self.assertIsInstance(obj, EmptyDataset)
        for key in ("axis_labels", "axis_ranges", "axis_units", "metadata"):
            self.assertTrue(hasattr(obj, key))

    def test_empty_dataset_array_finalize__simple_indexing(self):
        obj = self.create_large_dataset()
        _new = obj[0]
        self.assertEqual(list(_new.axis_labels.values()), self._dset["labels"][1:])
        for _new_ax, _original in zip(
            list(_new.axis_ranges.values()), self._dset["ranges"][1:]
        ):
            self.assertTrue(np.allclose(_new_ax, _original))
        self.assertEqual(list(_new.axis_units.values()), self._dset["units"][1:])

    def test_empty_dataset_array_finalize__simple_indexing_in_middle(self):
        obj = self.create_large_dataset()
        _new = obj[:, 0]
        self.assertEqual(
            list(_new.axis_labels.values()),
            [self._dset["labels"][0]] + self._dset["labels"][2:],
        )
        for _new_ax, _original in zip(
            list(_new.axis_ranges.values()),
            [self._dset["ranges"][0]] + self._dset["ranges"][2:],
        ):
            self.assertTrue(np.allclose(_new_ax, _original))
        self.assertEqual(
            list(_new.axis_units.values()),
            [self._dset["units"][0]] + self._dset["units"][2:],
        )

    def test_empty_dataset_array_finalize__simple_multi_indexing(self):
        obj = self.create_large_dataset()
        _new = obj[:, 7, 6]
        self.assertEqual(tuple(np.arange(_new.ndim)), tuple(_new.axis_labels.keys()))
        self.assertEqual(
            tuple(_new.axis_labels.values()),
            (self._dset["labels"][0], self._dset["labels"][3]),
        )
        for _new_range, _original_range in zip(
            _new.axis_ranges.values(),
            (self._dset["ranges"][0], self._dset["ranges"][3]),
        ):
            self.assertTrue(np.allclose(_new_range, _original_range))
        self.assertEqual(
            tuple(_new.axis_units.values()),
            (self._dset["units"][0], self._dset["units"][3]),
        )

    def test_empty_dataset_array_finalize__single_slicing(self):
        obj = self.create_large_dataset()
        _new = obj[1:4]
        self.assertEqual(list(_new.axis_labels.values()), self._dset["labels"])
        self.assertEqual(list(_new.axis_units.values()), self._dset["units"])
        for _dim, _new_range in enumerate(_new.axis_ranges.values()):
            if _dim == 0:
                self.assertTrue(np.allclose(_new_range, self._dset["ranges"][0][1:4]))
            else:
                self.assertTrue(np.allclose(_new_range, self._dset["ranges"][_dim]))

    def test_empty_dataset_array_finalize__single_slicing_with_ndarray(self):
        obj = self.create_large_dataset()
        _new = obj[np.arange(1, 4)]
        self.assertEqual(list(_new.axis_labels.values()), self._dset["labels"])
        self.assertEqual(list(_new.axis_units.values()), self._dset["units"])
        for _dim, _new_range in enumerate(_new.axis_ranges.values()):
            if _dim == 0:
                self.assertTrue(np.allclose(_new_range, self._dset["ranges"][0][1:4]))
            else:
                self.assertTrue(np.allclose(_new_range, self._dset["ranges"][_dim]))

    def test_empty_dataset_array_finalize__add_dimension(self):
        obj = self.create_large_dataset()
        _new = obj[None, :]
        self.assertEqual(list(_new.axis_labels.values()), [None] + self._dset["labels"])
        self.assertEqual(list(_new.axis_units.values()), [None] + self._dset["units"])

    def test_empty_dataset_array_finalize__add_dimension_in_middle(self):
        obj = self.create_large_dataset()
        _new = obj[:, None, :]
        self.assertEqual(
            list(_new.axis_labels.values()),
            [self._dset["labels"][0]] + [None] + self._dset["labels"][1:],
        )
        self.assertEqual(
            list(_new.axis_units.values()),
            [self._dset["units"][0]] + [None] + self._dset["units"][1:],
        )

    def test_empty_dataset_array_finalize__with_array_mask(self):
        obj = self.create_large_dataset()
        _mask = np.zeros(obj.shape)
        obj[_mask == 0] = 1
        self.assertTrue((obj == 1).all())

    def test_empty_dataset_array_finalize__get_masked(self):
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

    def test_empty_dataset_flatten(self):
        obj = self.create_large_dataset()
        _new = obj.flatten()
        self.assertEqual(_new.size, obj.size)
        self.assertEqual(_new.axis_labels[0], "Flattened")
        self.assertEqual(_new.axis_units[0], "")
        self.assertTrue(np.equal(_new.axis_ranges[0], np.arange(_new.size)).all())

    def test_empty_dataest_flatten_dims__simple(self):
        _dims = (1, 2)
        obj = self.create_large_dataset()
        obj.flatten_dims(*_dims)
        self.assertEqual(obj.ndim, len(self._dset["shape"]) - 1)
        for key, preset in zip(
            ["axis_labels", "axis_units", "axis_ranges"],
            ["Flattened", "", None],
        ):
            self.assertEqual(getattr(obj, key)[_dims[0]], preset)

    def test_empty_dataest_flatten_dims__1dim_only(self):
        obj = self.create_large_dataset()
        obj2 = copy.copy(obj)
        obj2.flatten_dims(1)
        self.assertTrue(np.equal(obj, obj2).all())

    def test_empty_dataest_flatten_dims__distributed_dims(self):
        obj = self.create_large_dataset()
        with self.assertRaises(ValueError):
            obj.flatten_dims(1, 3)

    def test_empty_dataest_flatten_dims__new_label(self):
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

    def test_empty_dataest_flatten_dims__new_unit(self):
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

    def test_empty_dataest_flatten_dims__new_range(self):
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

    def test_empty_dataset__comparison_with_allclose(self):
        obj = self.create_large_dataset()
        _new = np.zeros((obj.shape))
        self.assertFalse(np.allclose(obj, _new))

    def test_empty_dataset_array_finalize__multiple_ops(self):
        obj = self.create_large_dataset()
        _ = obj[0, 0]
        _ = obj[0]
        self.assertIsNone(obj.getitem_key)

    def test_empty_dataset_array_finalize__multiple_slicing(self):
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

    def test_empty_dataset_array_finalize__insert_data_simple(self):
        obj = self.create_large_dataset()
        _new = np.random.random((12, 14, 16))
        obj[2] = _new

    def test_empty_dataset_array_finalize__insert_data(self):
        obj = self.create_large_dataset()
        _new = np.random.random((14, 16))
        obj[2, 3] = _new

    def test_empty_dataset__with_rebin2d(self):
        obj = Dataset(np.random.random((11, 11)), axis_labels=[0, 1])
        _new = rebin2d(obj, 2)
        self.assertEqual(_new.shape, (5, 5))

    def test_transpose__1d(self):
        obj = Dataset(np.random.random((12)), axis_labels=[0], axis_units=["a"])
        _new = obj.transpose()
        self.assertEqual(obj.axis_labels[0], _new.axis_labels[0])
        self.assertEqual(obj.axis_units[0], _new.axis_units[0])
        self.assertEqual(obj.axis_ranges[0], _new.axis_ranges[0])

    def test_transpose__2d(self):
        obj = Dataset(
            np.random.random((12, 12)),
            axis_labels=[0, 1],
            axis_units=["a", "b"],
            axis_ranges=[np.arange(12), 20 - np.arange(12)],
        )
        _new = obj.transpose()
        for _i1, _i2 in [[0, 1], [1, 0]]:
            self.assertEqual(obj.axis_labels[_i1], _new.axis_labels[_i2])
            self.assertEqual(obj.axis_units[_i1], _new.axis_units[_i2])
            self.assertTrue(np.allclose(obj.axis_ranges[_i1], _new.axis_ranges[_i2]))
        self.assertTrue(np.allclose(obj[0], _new[:, 0]))
        self.assertTrue(np.allclose(obj[:, 0], _new[0]))

    def test_transpose__3d(self):
        obj = Dataset(
            np.random.random((6, 7, 8)),
            axis_labels=[0, 1, 2],
            axis_units=["a", "b", "c"],
            axis_ranges=[np.arange(6), 20 - np.arange(7), 3 * np.arange(8)],
        )
        _new = obj.transpose()
        for _i1, _i2 in [[0, 2], [2, 0], [1, 1]]:
            self.assertEqual(obj.axis_labels[_i1], _new.axis_labels[_i2])
            self.assertEqual(obj.axis_units[_i1], _new.axis_units[_i2])
            self.assertTrue(np.allclose(obj.axis_ranges[_i1], _new.axis_ranges[_i2]))
        self.assertTrue(np.allclose(obj[0, 0], _new[:, 0, 0]))
        self.assertTrue(np.allclose(obj[:, 0, 0], _new[0, 0]))
        self.assertTrue(np.allclose(obj[0, :, 0], _new[0, :, 0]))

    def test_transpose__4d(self):
        obj = Dataset(
            np.random.random((6, 7, 8, 9)),
            axis_labels=[0, 1, 2, 3],
            axis_units=["a", "b", "c", "d"],
            axis_ranges=[
                np.arange(6),
                20 - np.arange(7),
                3 * np.arange(8),
                -1 * np.arange(9),
            ],
        )
        _new = obj.transpose()
        for _i1, _i2 in [[0, 3], [3, 0], [1, 2], [2, 1]]:
            self.assertEqual(obj.axis_labels[_i1], _new.axis_labels[_i2])
            self.assertEqual(obj.axis_units[_i1], _new.axis_units[_i2])
            self.assertTrue(np.allclose(obj.axis_ranges[_i1], _new.axis_ranges[_i2]))
        self.assertTrue(np.allclose(obj[0, 0, 0], _new[:, 0, 0, 0]))
        self.assertTrue(np.allclose(obj[:, 0, 0, 0], _new[0, 0, 0]))
        self.assertTrue(np.allclose(obj[0, :, 0, 0], _new[0, 0, :, 0]))

    def test_transpose__4d_with_axes(self):
        obj = Dataset(
            np.random.random((6, 7, 8, 9)),
            axis_labels=[0, 1, 2, 3],
            axis_units=["a", "b", "c", "d"],
            axis_ranges=[
                np.arange(6),
                20 - np.arange(7),
                3 * np.arange(8),
                -1 * np.arange(9),
            ],
        )
        _new = obj.transpose(2, 1, 0, 3)
        for _i1, _i2 in [[0, 2], [2, 0]]:
            self.assertEqual(obj.axis_labels[_i1], _new.axis_labels[_i2])
            self.assertEqual(obj.axis_units[_i1], _new.axis_units[_i2])
            self.assertTrue(np.allclose(obj.axis_ranges[_i1], _new.axis_ranges[_i2]))
        self.assertTrue(np.allclose(obj[0, 0, :, 0], _new[:, 0, 0, 0]))
        self.assertTrue(np.allclose(obj[:, 0, 0, 0], _new[0, 0, :, 0]))
        self.assertTrue(np.allclose(obj[0, :, 0, 0], _new[0, :, 0, 0]))

    def test_squeeze__single_dim(self):
        obj = Dataset(
            np.random.random((6, 7, 1, 9)),
            axis_labels=[0, 1, 2, 3],
            axis_units=["a", "b", "c", "d"],
            axis_ranges=[
                np.arange(6),
                20 - np.arange(7),
                3 * np.arange(1),
                -1 * np.arange(9),
            ],
        )
        _new = np.squeeze(obj)
        for _i1, _i2 in [[0, 0], [1, 1], [3, 2]]:
            self.assertEqual(obj.axis_labels[_i1], _new.axis_labels[_i2])
            self.assertEqual(obj.axis_units[_i1], _new.axis_units[_i2])
            self.assertTrue(np.allclose(obj.axis_ranges[_i1], _new.axis_ranges[_i2]))
        self.assertTrue(np.allclose(obj[0, 0, 0], _new[0, 0]))
        self.assertEqual(obj.metadata, _new.metadata)
        self.assertEqual(obj.data_unit, _new.data_unit)

    def test_squeeze__multi_dim(self):
        obj = Dataset(
            np.random.random((6, 1, 7, 1, 9)),
            axis_labels=[0, 1, 2, 3, 4],
            axis_units=["a", "b", "c", "d", "e"],
            axis_ranges=[np.arange(6), [2], 20 - np.arange(7), [6], -1 * np.arange(9)],
        )
        _new = np.squeeze(obj)
        for _i1, _i2 in [[0, 0], [2, 1], [4, 2]]:
            self.assertEqual(obj.axis_labels[_i1], _new.axis_labels[_i2])
            self.assertEqual(obj.axis_units[_i1], _new.axis_units[_i2])
            self.assertTrue(np.allclose(obj.axis_ranges[_i1], _new.axis_ranges[_i2]))
        self.assertTrue(np.allclose(obj[0, 0, 0, 0], _new[0, 0]))

    def test_squeeze__multi_dim_with_None_range(self):
        obj = Dataset(
            np.random.random((6, 1, 7, 1, 9)),
            axis_labels=[0, 1, 2, 3, 4],
            axis_units=["a", "b", "c", "d", "e"],
            axis_ranges=[np.arange(6), [2], 20 - np.arange(7), [6], None],
        )
        _new = obj.squeeze()
        for _i1, _i2 in [[0, 0], [2, 1]]:
            self.assertEqual(obj.axis_labels[_i1], _new.axis_labels[_i2])
            self.assertEqual(obj.axis_units[_i1], _new.axis_units[_i2])
            self.assertTrue(np.allclose(obj.axis_ranges[_i1], _new.axis_ranges[_i2]))
        self.assertEqual(obj.axis_labels[4], _new.axis_labels[2])
        self.assertEqual(obj.axis_units[4], _new.axis_units[2])
        self.assertIsNone(_new.axis_ranges[2])
        self.assertTrue(np.allclose(obj[0, 0, 0, 0], _new[0, 0]))

    def test_squeeze__no_dim(self):
        obj = Dataset(
            np.random.random((6, 4, 7, 2, 9)),
            axis_labels=[0, 1, 2, 3, 4],
            axis_units=["a", "b", "c", "d", "e"],
            axis_ranges=[
                np.arange(6),
                [2, 5, 8, 9],
                20 - np.arange(7),
                [4, 3],
                -1 * np.arange(9),
            ],
        )
        _new = np.squeeze(obj)
        for _i1, _i2 in [[0, 0], [1, 1], [2, 2], [3, 3], [4, 4]]:
            self.assertEqual(obj.axis_labels[_i1], _new.axis_labels[_i2])
            self.assertEqual(obj.axis_units[_i1], _new.axis_units[_i2])
            self.assertTrue(np.allclose(obj.axis_ranges[_i1], _new.axis_ranges[_i2]))
        self.assertTrue(np.allclose(obj, _new))

    def test_squeeze__with_slicing(self):
        obj = Dataset(
            np.random.random((6, 4, 7, 1, 9)),
            axis_labels=[0, 1, 2, 3, 4],
            axis_units=["a", "b", "c", "d", "e"],
            axis_ranges=[
                np.arange(6),
                [2, 5, 8, 9],
                20 - np.arange(7),
                [4],
                -1 * np.arange(9),
            ],
        )
        _new = np.squeeze(obj[0:3])
        self.assertTrue(np.allclose(obj.axis_ranges[0][:3], _new.axis_ranges[0]))
        for _i1, _i2 in [[1, 1], [2, 2], [4, 3]]:
            self.assertEqual(obj.axis_labels[_i1], _new.axis_labels[_i2])
            self.assertEqual(obj.axis_units[_i1], _new.axis_units[_i2])
            self.assertTrue(np.allclose(obj.axis_ranges[_i1], _new.axis_ranges[_i2]))
        self.assertTrue(np.allclose(obj[:3, :, :, 0], _new))

    def test_take__full_dim_from_3d(self):
        obj = Dataset(
            np.random.random((6, 4, 7)),
            axis_labels=[0, 1, 2],
            axis_units=["a", "b", "c"],
            axis_ranges=[
                np.arange(6),
                [2, 5, 8, 9],
                20 - np.arange(7),
            ],
        )
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
        obj = Dataset(
            np.random.random((6, 5, 7)),
            axis_labels=[0, 1, 2],
            axis_units=["a", "b", "c"],
            axis_ranges=[
                np.arange(6),
                [2, 5, 8, 9, 11],
                20 - np.arange(7),
            ],
        )
        _dim = 1
        _slice = (1, 2, 3)
        _new = np.take(obj, _slice, _dim)
        self.assertTrue(np.allclose(obj[:, slice(1, 4)], _new))
        for _dim in range(3):
            self.assertEqual(obj.axis_labels[_dim], _new.axis_labels[_dim])
            self.assertEqual(obj.axis_units[_dim], _new.axis_units[_dim])
            if _dim == 1:
                self.assertTrue(
                    np.allclose(
                        obj.axis_ranges[_dim][slice(1, 4)], _new.axis_ranges[_dim]
                    )
                )
            else:
                self.assertTrue(
                    np.allclose(obj.axis_ranges[_dim], _new.axis_ranges[_dim])
                )

    def test_take__full_dim_from_2d(self):
        obj = Dataset(
            np.random.random((6, 4)),
            axis_labels=[0, 1],
            axis_units=["a", "b"],
            axis_ranges=[np.arange(6), [2, 5, 8, 9]],
        )
        _dim = 0
        _slice = 1
        _new = np.take(obj, _slice, _dim)
        self.assertTrue(np.allclose(obj[_slice], _new))
        self.assertEqual(obj.axis_labels[1], _new.axis_labels[0])
        self.assertEqual(obj.axis_units[1], _new.axis_units[0])
        self.assertTrue(np.allclose(obj.axis_ranges[1], _new.axis_ranges[0]))

    def test_take__dim_subset_from_2d(self):
        obj = Dataset(
            np.random.random((6, 5)),
            axis_labels=[0, 1],
            axis_units=["a", "b"],
            axis_ranges=[np.arange(6), [2, 5, 8, 9, 11]],
        )
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

    def test_take__with_None_ranges(self):
        obj = Dataset(
            np.random.random((6, 5)),
            axis_labels=[0, 1],
            axis_units=["a", "b"],
            axis_ranges=[None, None],
        )
        _dim = 1
        _slice = (1, 2, 3)
        _new = np.take(obj, _slice, _dim)
        self.assertTrue(np.allclose(obj[:, slice(1, 4)], _new))
        for _dim in range(2):
            self.assertEqual(obj.axis_labels[_dim], _new.axis_labels[_dim])
            self.assertEqual(obj.axis_units[_dim], _new.axis_units[_dim])
            self.assertEqual(obj.axis_ranges[_dim], _new.axis_ranges[_dim])

    def test_take__with_single_iterable_value(self):
        obj = Dataset(
            np.random.random((6, 5)),
            axis_labels=[0, 1],
            axis_units=["a", "b"],
            axis_ranges=[np.arange(6), [2, 5, 8, 9, 11]],
        )
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
        obj = Dataset(
            np.random.random((6)),
            axis_labels=[0],
            axis_units=["a"],
            axis_ranges=[np.arange(6)],
        )
        _new = np.take(obj, 2, 0)
        self.assertFalse(isinstance(_new, Dataset))
        self.assertEqual(_new, obj[2])

    def test_empty_dataset_getitem__simple(self):
        obj = self.create_large_dataset()
        _new = obj.__getitem__((0, 0))
        self.assertIsInstance(_new, Dataset)

    def test_empty_dataset__new__kwargs(self):
        obj = self.create_empty_dataset()
        self.assertIsInstance(obj.axis_labels, dict)
        self.assertIsInstance(obj.axis_ranges, dict)
        self.assertIsInstance(obj.axis_units, dict)

    def test_empty_dataset_axis_labels_property(self):
        obj = self.create_empty_dataset()
        self.assertEqual(obj.axis_labels, self.get_dict("_axis_labels"))

    def test_empty_dataset_axis_labels_property__modify_copy(self):
        obj = self.create_empty_dataset()
        _labels = obj.axis_labels
        _labels[0] = "new value"
        self.assertEqual(obj.axis_labels, self.get_dict("_axis_labels"))

    def test_empty_dataset_axis_units_property(self):
        obj = self.create_empty_dataset()
        self.assertEqual(obj.axis_units, self.get_dict("_axis_units"))

    def test_empty_dataset_axis_units_property__modify_copy(self):
        obj = self.create_empty_dataset()
        _units = obj.axis_units
        _units[0] = "A new unit"
        self.assertEqual(obj.axis_units, self.get_dict("_axis_units"))

    def test_empty_dataset_axis_ranges_property(self):
        obj = self.create_empty_dataset()
        self.assertEqual(obj.axis_ranges, self.get_dict("_axis_ranges"))

    def test_empty_dataset_axis_ranges_property__modify_copy(self):
        obj = self.create_empty_dataset()
        _ranges = obj.axis_ranges
        _ranges[0] = 2 * _ranges[0] - 5
        self.assertEqual(obj.axis_ranges, self.get_dict("_axis_ranges"))

    def test_empty_dataset_set_axis_labels_property(self):
        obj = self.create_empty_dataset()
        _newkeys = [123, 456]
        obj.axis_labels = _newkeys
        self.assertEqual(obj.axis_labels, dict(enumerate(_newkeys)))

    def test_empty_dataset_set_axis_units_property(self):
        obj = self.create_empty_dataset()
        _newkeys = [123, 456]
        obj.axis_units = _newkeys
        self.assertEqual(obj.axis_units, dict(enumerate(_newkeys)))

    def test_empty_dataset_set_axis_ranges_property__single_keys(self):
        obj = self.create_empty_dataset()
        _newkeys = [123, 456]
        obj.axis_ranges = _newkeys
        self.assertEqual(obj.axis_ranges, dict(enumerate(_newkeys)))

    def test_empty_dataset_set_axis_ranges_property__ndarrays_of_correct_len(self):
        obj = self.create_empty_dataset()
        _newkeys = [np.arange(_len) for _len in obj.shape]
        obj.axis_ranges = _newkeys
        self.assertEqual(obj.axis_ranges, dict(enumerate(_newkeys)))

    def test_empty_dataset_set_axis_ranges_property__lists_of_correct_len(self):
        obj = self.create_empty_dataset()
        _newkeys = [list(np.arange(_len)) for _len in obj.shape]
        obj.axis_ranges = _newkeys
        for _key, _range in obj.axis_ranges.items():
            self.assertTrue(np.allclose(_range, np.asarray(_newkeys[_key])))

    def test_empty_dataset_set_axis_ranges_property__ndarrays_of_incorrect_len(self):
        obj = self.create_empty_dataset()
        _newkeys = [np.arange(_len + 2) for _len in obj.shape]
        with self.assertRaises(ValueError):
            obj.axis_ranges = _newkeys

    def test_empty_dataset_set_axis_ranges_property__lists_of_incorrect_len(self):
        obj = self.create_empty_dataset()
        _newkeys = [list(np.arange(_len + 2)) for _len in obj.shape]
        with self.assertRaises(ValueError):
            obj.axis_ranges = _newkeys

    def test_empty_dataset_metadata_property(self):
        obj = self.create_empty_dataset()
        self.assertEqual(obj.metadata, {})

    def test_empty_dataset_set_metadata_property(self):
        obj = self.create_empty_dataset()
        obj.metadata = None

    def test_empty_dataset_set_metadata_property_w_dict(self):
        obj = self.create_empty_dataset()
        _meta = {"key0": 123, "key1": -1, 0: "test"}
        obj.metadata = _meta
        self.assertEqual(obj.metadata, _meta)

    def test_empty_dataset_set_metadata_property_w_list(self):
        obj = self.create_empty_dataset()
        _meta = [1, 2, 4]
        with self.assertRaises(TypeError):
            obj.metadata = _meta

    def test_empty_dataset_array_property(self):
        obj = self.create_empty_dataset()
        self.assertIsInstance(obj.array, np.ndarray)

    def test_update_axis_ranges__wrong_index(self):
        obj = self.create_large_dataset()
        with self.assertRaises(ValueError):
            obj.update_axis_ranges(-4, 12)

    def test_update_axis_ranges__single_val(self):
        _val = 12
        obj = self.create_large_dataset()
        obj.update_axis_ranges(1, _val)
        self.assertEqual(obj.axis_ranges[1], _val)

    def test_update_axis_ranges__correct_ndarray(self):
        obj = self.create_large_dataset()
        _val = np.arange(obj.shape[1])
        obj.update_axis_ranges(1, _val)
        self.assertTrue(np.allclose(obj.axis_ranges[1], _val))

    def test_update_axis_ranges__incorrect_ndarray(self):
        obj = self.create_large_dataset()
        _val = np.arange(obj.shape[1] + 5)
        with self.assertRaises(ValueError):
            obj.update_axis_ranges(1, _val)

    def test_update_axis_labels__wrong_index(self):
        obj = self.create_large_dataset()
        with self.assertRaises(ValueError):
            obj.update_axis_labels(-4, 12)

    def test_update_axis_labels__single_val(self):
        _val = "a new label"
        obj = self.create_large_dataset()
        obj.update_axis_labels(1, _val)
        self.assertEqual(obj.axis_labels[1], _val)

    def test_update_axis_units__wrong_index(self):
        obj = self.create_large_dataset()
        with self.assertRaises(ValueError):
            obj.update_axis_units(-4, 12)

    def test_update_axis_units__single_val(self):
        _val = "a new unit"
        obj = self.create_large_dataset()
        obj.update_axis_units(1, _val)
        self.assertEqual(obj.axis_units[1], _val)

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
        obj = EmptyDataset((10, 10, 10))
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
        new_obj = EmptyDataset((1))
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

    def test_convert_all_none_properties(self):
        _range1 = np.linspace(2.7, 12, num=10)
        _label1 = "Some label"
        _unit1 = "The unit"
        _array = np.random.random((10, 10))
        obj = Dataset(
            _array,
            axis_ranges=[None, _range1],
            axis_labels=[None, _label1],
            axis_units=[None, _unit1],
        )
        obj.convert_all_none_properties()
        self.assertTrue(np.allclose(obj.axis_ranges[0], np.arange(10)))
        self.assertTrue(np.allclose(obj.axis_ranges[1], _range1))
        self.assertEqual(obj.axis_labels, {0: "", 1: _label1})
        self.assertEqual(obj.axis_units, {0: "", 1: _unit1})


if __name__ == "__main__":
    unittest.main()
