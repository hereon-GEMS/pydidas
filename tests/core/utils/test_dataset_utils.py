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


import unittest
import warnings

import numpy as np
from pydidas.core import PydidasConfigError
from pydidas.core.dataset import Dataset
from pydidas.core.utils.dataset_utils import (
    convert_ranges_and_check_length,
    dataset_default_attribute,
    get_corresponding_dims,
    get_input_as_dict,
    get_number_of_entries,
    update_dataset_properties_from_kwargs,
)


class Test_dataset_utils(unittest.TestCase):
    def setUp(self): ...

    def tearDown(self): ...

    def test_update_dataset_properties_from_kwargs__no_input(self):
        obj = Dataset(np.random.random((10, 10)))
        update_dataset_properties_from_kwargs(obj, {})
        self.assertEqual(obj._meta["_get_item_key"], ())

    def test_update_dataset_properties_from_kwargs__wrong_input(self):
        obj = Dataset(np.random.random((10, 10)))
        with self.assertWarns(UserWarning):
            update_dataset_properties_from_kwargs(obj, {"wrong_key": 12})

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
        obj = Dataset(np.random.random((10, 10)))
        _ranges = {0: np.arange(obj.shape[0]) - 1, 1: np.arange(obj.shape[1]) + 5}
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

    def dataset_default_attribute__metadata(self):
        self.assertEqual(dataset_default_attribute("metadata", (1,)), {})

    def dataset_default_attribute__data_unit(self):
        self.assertEqual(dataset_default_attribute("data_unit", (1,)), "")

    def dataset_default_attribute___get_item_key(self):
        self.assertEqual(dataset_default_attribute("_get_item_key", (1,)), tuple())

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

    def test_get_input_as_dict__correct_dict(self):
        _obj = {0: 5, 1: 4, 2: 42}
        _new = get_input_as_dict(_obj, (1, 2, 3))
        self.assertEqual(_obj, _new)

    def test_get_input_as_dict__incorrect_dict(self):
        _obj = {0: 5, 3: 4, 6: 42}
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            _new = get_input_as_dict(_obj, (1, 2, 3))
        self.assertEqual(_new, {0: 5, 1: "", 2: ""})

    def test_get_input_as_dict__correct_iterable(self):
        _obj = [5, 4, 3]
        _new = get_input_as_dict(_obj, (1, 2, 3))
        self.assertEqual(_new, dict(enumerate(_obj)))

    def test_get_input_as_dict__incorrect_iterable(self):
        _obj = [4, 2, 7, 4]
        with self.assertRaises(PydidasConfigError):
            get_input_as_dict(_obj, (1, 2, 3))

    def test_get_input_as_dict__incorrect_type(self):
        _obj = "a string"
        with self.assertRaises(PydidasConfigError):
            get_input_as_dict(_obj, (3,))

    def test_get_corresponding_dims__identity(self):
        _old = (10, 11, 12, 15)
        _dims = get_corresponding_dims(_old, _old)
        self.assertEqual(list(_dims.keys()), list(_dims.values()))

    def test_get_corresponding_dims__inverted(self):
        _old = (10, 11, 12, 15)
        _dims = get_corresponding_dims(_old, _old[::-1])
        self.assertEqual(_dims, {})

    def test_get_corresponding_dims(self):
        for _shape1, _shape2, _matches in [
            [(14, 14, 14), (14, 7, 2, 14), {0: 0, 3: 2}],
            [(14, 7, 14, 2), (14, 14, 14), {0: 0}],
            [(16, 16, 16), (16, 4, 2, 2, 16), {0: 0, 4: 2}],
            [(14, 14, 2, 7), (14, 14, 14), {0: 0, 1: 1}],
            [(16, 16, 16), (16, 4, 16, 2, 2), {0: 0}],
            [(16, 16, 16), (2, 16, 4, 16, 2), {}],
            [(16, 16, 16), (4, 4, 16, 2, 2, 4), {2: 1}],
            [(1, 16, 1, 16, 16), (1, 4, 4, 1, 16, 2, 2, 4), {0: 0, 3: 2, 4: 3}],
            [(1, 16, 1, 16, 16), (1, 4, 4, 16, 1, 2, 2, 4), {0: 0, 3: 3}],
            [(16, 16, 16), (4, 2, 2, 8, 2, 16), {5: 2}],
            [(16, 16, 16), (1, 1, 4, 2, 2, 1, 8, 2, 16), {8: 2}],
            [(14, 14, 14), (14, 1, 1, 14, 1, 14), {0: 0, 3: 1, 5: 2}],
            [(1, 14, 14, 14), (1, 1, 1, 14, 1, 1, 14, 1, 14), {0: 0, 3: 1, 6: 2, 8: 3}],
            [(1, 1, 14, 14, 14, 1), (14, 14, 14), {0: 2, 1: 3, 2: 4}],
            [(14, 1, 1, 14, 14), (14, 14, 1, 14), {0: 0, 1: 3, 3: 4}],
            [(5,), (1, 5, 1), {1: 0}],
            ((5,), (1, 1, 5), {2: 0}),
            [(42,), (42, 1, 1), {0: 0}],
        ]:
            with self.subTest(old_shape=_shape1, new_shape=_shape2):
                _dim_matches = get_corresponding_dims(_shape1, _shape2)
                self.assertEqual(_dim_matches, _matches)

    def test_convert_ranges_and_check_length__correct(self):
        _ranges = [
            {0: np.arange(10), 1: np.arange(10)},
            {0: np.arange(10), 1: list(np.arange(10))},
            {0: np.arange(10), 1: tuple(np.arange(10))},
            {0: list(np.arange(10)), 1: np.arange(10)},
            {0: tuple(np.arange(10)), 1: np.arange(10)},
            {0: list(np.arange(10)), 1: list(np.arange(10))},
            {0: tuple(np.arange(10)), 1: tuple(np.arange(10))},
        ]
        for _curr_ranges in _ranges:
            with self.subTest(range=_curr_ranges):
                _new_ranges = convert_ranges_and_check_length(_curr_ranges, (10, 10))
                for _key in _new_ranges:
                    self.assertTrue(np.allclose(_new_ranges[_key], _curr_ranges[_key]))

    def test_convert_ranges_and_check_length__incorrect_length(self):
        _ranges = [
            {0: np.arange(10), 1: np.arange(11)},
            {0: np.arange(10), 1: np.arange(9)},
            {0: np.arange(11), 1: np.arange(9)},
        ]
        _shape = (10, 10)
        for _curr_ranges in _ranges:
            with self.subTest(range=_curr_ranges):
                with self.assertRaises(ValueError):
                    convert_ranges_and_check_length(_curr_ranges, _shape)

    def test_convert_ranges_and_check_length__incorrect_type(self):
        _ranges = [
            {0: np.arange(10), 1: 10 * "a"},
            {0: np.arange(10), 1: set(np.arange(10))},
            {0: np.arange(10), 1: {k: v for k, v in enumerate(np.arange(10))}},
        ]
        _shape = (10, 10)
        for _curr_ranges in _ranges:
            with self.subTest(range=_curr_ranges):
                with self.assertRaises(ValueError):
                    convert_ranges_and_check_length(_curr_ranges, _shape)

    def test_convert_ranges_and_check_length__single_value(self):
        _ranges = {0: np.arange(10), 1: 5, 2: 20 - np.arange(10)}
        _shape = (10, 1, 10)
        _new_ranges = convert_ranges_and_check_length(_ranges, _shape)
        for _key in _new_ranges:
            self.assertTrue(np.allclose(_new_ranges[_key], np.asarray(_ranges[_key])))


if __name__ == "__main__":
    unittest.main()
