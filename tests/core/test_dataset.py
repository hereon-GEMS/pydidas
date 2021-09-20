# This file is part of pydidas.

# pydidas is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# Pydidas is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with Pydidas. If not, see <http://www.gnu.org/licenses/>.

"""Unit tests for pydidas modules."""

__author__      = "Malte Storm"
__copyright__   = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.0.1"
__maintainer__ = "Malte Storm"
__status__ = "Development"

import unittest

import numpy as np

from pydidas.core.dataset import Dataset, EmptyDataset, DatasetConfigException


class TestDataset(unittest.TestCase):

    def setUp(self):
        self._axis_labels = ['axis0', 'axis1']
        self._axis_scales = [1, 10]
        self._axis_units = {0: 'm', 1: 'rad'}

    def tearDown(self):
        ...

    def create_empty_dataset(self):
        obj = EmptyDataset((10, 10),
                           axis_labels=self._axis_labels,
                           axis_scales=self._axis_scales,
                           axis_units=self._axis_units,
                           metadata={})
        return obj

    def get_dict(self, key):
        if isinstance(getattr(self, key), dict):
            return getattr(self, key)
        return {i: item for i, item in enumerate(getattr(self, key))}

    def test_empty_dataset_new(self):
        obj = EmptyDataset((10, 10))
        self.assertIsInstance(obj, EmptyDataset)
        for key in ('axis_labels', 'axis_scales', 'axis_units', 'metadata'):
            self.assertTrue(hasattr(obj, key))

    def test__get_dict_w_dict_missing_key(self):
        obj = EmptyDataset((10, 10))
        with self.assertRaises(DatasetConfigException):
            obj._EmptyDataset__get_dict({1: 0}, 'test')

    def test__get_dict_w_dict_too_many_keys(self):
        obj = EmptyDataset((10, 10))
        with self.assertRaises(DatasetConfigException):
            obj._EmptyDataset__get_dict({0: 1, 1: 2, 2: 3}, 'test')

    def test__get_dict_w_dict(self):
        obj = EmptyDataset((10, 10))
        obj._EmptyDataset__get_dict({0: 0, 1: 1}, 'test')

    def test__get_dict_w_list_missing_entry(self):
        obj = EmptyDataset((10, 10))
        with self.assertRaises(DatasetConfigException):
            obj._EmptyDataset__get_dict([0], 'test')

    def test__get_dict_w_list_too_many_entries(self):
        obj = EmptyDataset((10, 10))
        with self.assertRaises(DatasetConfigException):
            obj._EmptyDataset__get_dict([1, 2, 3], 'test')

    def test__get_dict_w_list(self):
        obj = EmptyDataset((10, 10))
        obj._EmptyDataset__get_dict([0, 1], 'test')

    def test__get_dict_w_value(self):
        obj = EmptyDataset((10, 10))
        with self.assertRaises(DatasetConfigException):
            obj._EmptyDataset__get_dict(0, 'test')

    def test_empty_dataset_new_kwargs(self):
        obj = self.create_empty_dataset()
        self.assertIsInstance(obj.axis_labels, dict)
        self.assertIsInstance(obj.axis_scales, dict)
        self.assertIsInstance(obj.axis_units, dict)

    def test_empty_dataset_axis_labels_property(self):
        obj = self.create_empty_dataset()
        self.assertEqual(obj.axis_labels, self.get_dict('_axis_labels'))

    def test_empty_dataset_axis_units_property(self):
        obj = self.create_empty_dataset()
        self.assertEqual(obj.axis_units, self.get_dict('_axis_units'))

    def test_empty_dataset_axis_scales_property(self):
        obj = self.create_empty_dataset()
        self.assertEqual(obj.axis_scales, self.get_dict('_axis_scales'))

    def test_empty_dataset_set_axis_labels_property(self):
        obj = self.create_empty_dataset()
        _newkeys = [123, 456]
        obj.axis_labels = _newkeys
        self.assertEqual(obj.axis_labels,
                         {i: o for i, o in enumerate(_newkeys)})

    def test_empty_dataset_set_axis_units_property(self):
        obj = self.create_empty_dataset()
        _newkeys = [123, 456]
        obj.axis_units = _newkeys
        self.assertEqual(obj.axis_units,
                         {i: o for i, o in enumerate(_newkeys)})

    def test_empty_dataset_set_axis_scales_property(self):
        obj = self.create_empty_dataset()
        _newkeys = [123, 456]
        obj.axis_scales = _newkeys
        self.assertEqual(obj.axis_scales,
                         {i: o for i, o in enumerate(_newkeys)})

    def test_empty_dataset_metadata_property(self):
        obj = self.create_empty_dataset()
        self.assertEqual(obj.metadata, {})

    def test_empty_dataset_set_metadata_property(self):
        obj = self.create_empty_dataset()
        obj.metadata = None

    def test_empty_dataset_set_metadata_property_w_dict(self):
        obj = self.create_empty_dataset()
        _meta = {'key0': 123, 'key1': -1, 0: 'test'}
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

    def test_dataset_creation(self):
        _array = np.random.random((10, 10, 10))
        obj = Dataset(_array)
        self.assertIsInstance(obj, Dataset)
        self.assertTrue((obj.array == _array).all())

    def test_dataset_creation_with_kwargs(self):
        _array = np.random.random((10, 10))
        obj = Dataset(_array,
                      axis_labels=self._axis_labels,
                      axis_scales=self._axis_scales,
                      axis_units=self._axis_units,
                      metadata={})
        self.assertIsInstance(obj, Dataset)
        self.assertIsInstance(obj.axis_labels, dict)
        self.assertIsInstance(obj.axis_scales, dict)
        self.assertIsInstance(obj.axis_units, dict)
        self.assertIsInstance(obj.metadata, dict)

    def test_repr__dataset(self):
        _array = np.random.random((10, 10, 10))
        obj = Dataset(_array)
        self.assertIsInstance(obj.__repr__(), str)

    def test_repr__empty_dataset(self):
        obj = EmptyDataset((10, 10, 10))
        self.assertIsInstance(obj.__repr__(), str)

    def test__str__(self):
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

if __name__ == "__main__":
    unittest.main()
