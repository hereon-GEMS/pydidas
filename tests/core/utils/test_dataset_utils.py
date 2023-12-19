# This file is part of pydidas.
#
# Copyright 2023, Helmholtz-Zentrum Hereon
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
__copyright__ = "Copyright 2023, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"


import unittest
import warnings

import numpy as np

from pydidas.core import PydidasConfigError
from pydidas.core.dataset import Dataset
from pydidas.core.utils.dataset_utils import (
    convert_data_to_dict,
    dataset_ax_str_default,
    dataset_property_default_val,
    get_number_of_entries,
    item_is_iterable_but_not_array,
    update_dataset_properties_from_kwargs,
)


class Test_dataset_utils(unittest.TestCase):
    def setUp(self):
        ...

    def tearDown(self):
        ...

    def test_update_dataset_properties_from_kwargs__no_input(self):
        obj = Dataset(np.random.random((10, 10)))
        update_dataset_properties_from_kwargs(obj, {})
        self.assertEqual(obj._getitem_key, ())

    def test_update_dataset_properties_from_kwargs__axis_units(self):
        _units = {0: "a", 1: "b"}
        obj = Dataset(np.random.random((10, 10)))
        update_dataset_properties_from_kwargs(obj, {"axis_units": _units.values()})
        self.assertEqual(obj.axis_units, _units)

    def test_update_dataset_properties_from_kwargs__axis_labels(self):
        _labels = {0: "abc", 1: "bcd"}
        obj = Dataset(np.random.random((10, 10)))
        update_dataset_properties_from_kwargs(obj, {"axis_labels": _labels.values()})
        self.assertEqual(obj.axis_labels, _labels)

    def test_update_dataset_properties_from_kwargs__axis_ranges(self):
        _ranges = {0: 12, 1: -5}
        obj = Dataset(np.random.random((10, 10)))
        update_dataset_properties_from_kwargs(obj, {"axis_ranges": _ranges.values()})
        self.assertEqual(obj.axis_ranges, _ranges)

    def test_update_dataset_properties_from_kwargs__metadata(self):
        _meta = {"a": 12, 0: "c", 4: 4}
        obj = Dataset(np.random.random((10, 10)))
        update_dataset_properties_from_kwargs(obj, {"metadata": _meta})
        self.assertEqual(obj.metadata, _meta)

    def test_update_dataset_properties_from_kwargs__data_unit(self):
        _unit = "a unit"
        obj = Dataset(np.random.random((10, 10)))
        update_dataset_properties_from_kwargs(obj, {"data_unit": _unit})
        self.assertEqual(obj.data_unit, _unit)

    def test_dataset_property_default_val__metadata(self):
        self.assertEqual(dataset_property_default_val("metadata"), {})

    def test_dataset_property_default_val__data_unit(self):
        self.assertEqual(dataset_property_default_val("data_unit"), "")

    def test_dataset_property_default_val__getitem_key(self):
        self.assertEqual(dataset_property_default_val("getitem_key"), tuple())

    def test_dataset_ax_str_default(self):
        _range = dataset_ax_str_default(5)
        self.assertEqual(set(np.arange(5)), set(_range.keys()))
        self.assertEqual(set([""]), set(_range.values()))

    def test_get_number_of_entries__ndarray(self):
        _arr = np.arange(27)
        _n = get_number_of_entries(_arr)
        self.assertEqual(_arr.size, _n)

    def test_get_number_of_entries__iterable(self):
        _obj = [1, 2, 3, 4]
        _n = get_number_of_entries(_obj)
        self.assertEqual(len(_obj), _n)

    def test_get_number_of_entries__integral(self):
        _obj = 42
        _n = get_number_of_entries(_obj)
        self.assertEqual(1, _n)

    def test_get_number_of_entries__string(self):
        _obj = "a string"
        with self.assertRaises(TypeError):
            get_number_of_entries(_obj)

    def test_get_number_of_entries__float(self):
        _obj = 42.5
        with self.assertRaises(TypeError):
            get_number_of_entries(_obj)

    def test_convert_data_to_dict__correct_dict(self):
        _obj = {0: 5, 1: 4, 2: 42}
        _new = convert_data_to_dict(_obj, (1, 2, 3))
        self.assertEqual(_obj, _new)

    def test_convert_data_to_dict__incorrect_dict(self):
        _obj = {0: 5, 3: 4, 6: 42}
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            _new = convert_data_to_dict(_obj, (1, 2, 3))
            self.assertEqual(_new, dict(enumerate(_obj.values())))

    def test_convert_data_to_dict__correct_iterable(self):
        _obj = [5, 4, 3]
        _new = convert_data_to_dict(_obj, (1, 2, 3))
        self.assertEqual(_new, dict(enumerate(_obj)))

    def test_convert_data_to_dict__incorrect_iterable(self):
        _obj = [4, 2, 7, 4]
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            _new = convert_data_to_dict(_obj, (1, 2, 3))
            self.assertEqual(_new, dataset_ax_str_default(3))

    def test_convert_data_to_dict__incorrect_type(self):
        _obj = "a string"
        with self.assertRaises(PydidasConfigError):
            convert_data_to_dict(_obj, 3)

    def test_item_is_iterable_but_not_array__string(self):
        _flag = item_is_iterable_but_not_array("a string")
        self.assertFalse(_flag)

    def test_item_is_iterable_but_not_array__float(self):
        _flag = item_is_iterable_but_not_array(12.6)
        self.assertFalse(_flag)

    def test_item_is_iterable_but_not_array__int(self):
        _flag = item_is_iterable_but_not_array(42)
        self.assertFalse(_flag)

    def test_item_is_iterable_but_not_array__ndarray(self):
        _flag = item_is_iterable_but_not_array(np.arange(12))
        self.assertFalse(_flag)

    def test_item_is_iterable_but_not_array__list(self):
        _flag = item_is_iterable_but_not_array([1, 2, 3])
        self.assertTrue(_flag)

    def test_item_is_iterable_but_not_array__tuple(self):
        _flag = item_is_iterable_but_not_array((1, 2, 3))
        self.assertTrue(_flag)

    def test_item_is_iterable_but_not_array__set(self):
        _flag = item_is_iterable_but_not_array({1, 2, 3})
        self.assertTrue(_flag)


if __name__ == "__main__":
    unittest.main()
