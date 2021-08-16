# This file is part of pydidas.

# pydidas is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# Foobar is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with Foobar.  If not, see <http://www.gnu.org/licenses/>.

"""Unit tests for pydidas modules."""

__author__      = "Malte Storm"
__copyright__   = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.0.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"

import unittest
import copy

from pydidas.image_io.roi_manager import RoiManager


class TestRoiManager(unittest.TestCase):

    def setUp(self):
        self._target_ROI = (slice(0, 5, None), slice(0, 5, None))

    def tearDown(self):
        ...

    def create_RoiManager(self, _roi=None):
        obj = RoiManager()
        if _roi is not None:
            obj._RoiManager__kwargs = {'ROI': copy.copy(_roi)}
        obj._RoiManager__check_roi_key()
        obj._RoiManager__check_types_roi_key()
        return obj

    def test_creation(self):
        obj = RoiManager()
        self.assertIsInstance(obj, RoiManager)

    def test_check_roi_key__no_kwarg(self):
        obj = RoiManager()
        obj._RoiManager__check_roi_key()
        self.assertIsNone(obj._RoiManager__roi_key)

    def test_check_roi_key__with_kwarg(self):
        _roi = 'Test'
        obj = RoiManager()
        obj._RoiManager__kwargs = {'ROI': _roi}
        obj._RoiManager__check_roi_key()
        self.assertEqual(obj._RoiManager__roi_key, _roi)

    def test_check_types_roi_key__w_None(self):
        obj = RoiManager()
        obj._RoiManager__roi_key = None
        obj._RoiManager__check_types_roi_key()
        self.assertEqual(obj._RoiManager__roi_key, None)

    def test_check_types_roi_key__w_list(self):
        _list = ['Test', 'Test2']
        obj = RoiManager()
        obj._RoiManager__roi_key = _list
        obj._RoiManager__check_types_roi_key()
        self.assertEqual(obj._RoiManager__roi_key, _list)

    def test_check_types_roi_key__w_str(self):
        _str = 'Test, Test2'
        obj = RoiManager()
        obj._RoiManager__roi_key = _str
        obj._RoiManager__check_types_roi_key()
        self.assertIsInstance(obj._RoiManager__roi_key, list)

    def test_check_types_roi_key__w_tuple(self):
        _roi = ('Test', 'Test2')
        obj = RoiManager()
        obj._RoiManager__roi_key = _roi
        obj._RoiManager__check_types_roi_key()
        self.assertEqual(obj._RoiManager__roi_key, list(_roi))

    def test_check_types_roi_key__w_set(self):
        _roi = {'Test', 'Test2'}
        obj = RoiManager()
        obj._RoiManager__roi_key = _roi
        with self.assertRaises(ValueError):
            obj._RoiManager__check_types_roi_key()

    def test_convert_str_roi_key_to_list__simple(self):
        _roi = '7, 1234, Test2'
        _list = [item.strip() for item in _roi.split(',')]
        obj = RoiManager()
        obj._RoiManager__roi_key = _roi
        obj._RoiManager__convert_str_roi_key_to_list()
        self.assertEqual(obj._RoiManager__roi_key, _list)

    def test_convert_str_roi_key_to_list__slices(self):
        _roi = 'slice(1, 4, 1), slice(0, 4)'
        _list = [item.strip() for item in _roi.split(',')]
        obj = RoiManager()
        obj._RoiManager__roi_key = _roi
        obj._RoiManager__convert_str_roi_key_to_list()
        self.assertEqual(obj._RoiManager__roi_key, _list)

    def test_convert_str_roi_key_to_list__with_brackets(self):
        _roi = '(slice(1, 4, 1), slice(0, 4))'
        _list = [item.strip() for item in _roi[1:-1].split(',')]
        obj = RoiManager()
        obj._RoiManager__roi_key = _roi
        obj._RoiManager__convert_str_roi_key_to_list()
        self.assertEqual(obj._RoiManager__roi_key, _list)

    def test_convert_str_roi_key_to_list__with_straight_brackets(self):
        _roi = '[slice(1, 4, 1), slice(0, 4)]'
        _list = [item.strip() for item in _roi[1:-1].split(',')]
        obj = RoiManager()
        obj._RoiManager__roi_key = _roi
        obj._RoiManager__convert_str_roi_key_to_list()
        self.assertEqual(obj._RoiManager__roi_key, _list)

    def test_convert_str_roi_key_to_list__only_leading_bracket(self):
        _roi = '(slice(1, 4, 1), slice(0, 4)'
        _list = [item.strip() for item in _roi[1:].split(',')]
        obj = RoiManager()
        obj._RoiManager__roi_key = _roi
        obj._RoiManager__convert_str_roi_key_to_list()
        self.assertEqual(obj._RoiManager__roi_key, _list)

    def test_check_types_roi_key_entries(self):
        obj = RoiManager()
        obj._RoiManager__roi_key = [12, slice(0, 2)]
        obj._RoiManager__check_types_roi_key_entries

    def test_check_types_roi_key_entries__w_float(self):
        obj = self.create_RoiManager()
        obj._RoiManager__roi_key = [12, slice(0, 15), 12.3]
        with self.assertRaises(ValueError):
            obj._RoiManager__check_types_roi_key_entries()

    def test_check_types_roi_key_entries__w_str(self):
        obj = self.create_RoiManager()
        obj._RoiManager__roi_key = [12, slice(0, 15), '12.3']
        with self.assertRaises(ValueError):
            obj._RoiManager__check_types_roi_key_entries()

    def test_check_and_convert_str_roi_key_entries__int(self):
        _roi = [1, 2, 3, 4]
        _strroi = ', '.join(str(item) for item in _roi)
        obj = self.create_RoiManager(_strroi)
        obj._RoiManager__check_and_convert_str_roi_key_entries()
        self.assertEqual(obj._RoiManager__roi_key, _roi)

    def test_check_and_convert_str_roi_key_entries__float(self):
        _roi = [1, 2, 3, 4.0]
        _strroi = ', '.join(str(item) for item in _roi)
        obj = self.create_RoiManager(_strroi)
        with self.assertRaises(ValueError):
            obj._RoiManager__check_and_convert_str_roi_key_entries()

    def test_check_and_convert_str_roi_key_entries__slice_last(self):
        _roi = [1, 2, slice(0, 2)]
        _strroi = ', '.join(str(item) for item in _roi)
        obj = self.create_RoiManager(_strroi)
        obj._RoiManager__check_and_convert_str_roi_key_entries()
        self.assertEqual(obj._RoiManager__roi_key, _roi)

    def test_check_and_convert_str_roi_key_entries__slice_first(self):
        _roi = [slice(0, 2), 1, 2]
        _strroi = ', '.join(str(item) for item in _roi)
        obj = self.create_RoiManager(_strroi)
        obj._RoiManager__check_and_convert_str_roi_key_entries()
        self.assertEqual(obj._RoiManager__roi_key, _roi)

    def test_check_and_convert_str_roi_key_entries__2slices(self):
        _roi = [slice(1, 3, 5), slice(0, 2)]
        _strroi = ', '.join(str(item) for item in _roi)
        obj = self.create_RoiManager(_strroi)
        obj._RoiManager__check_and_convert_str_roi_key_entries()
        self.assertEqual(obj._RoiManager__roi_key, _roi)

    def test_check_and_convert_str_roi_key_entries__2slices_wo_steps(self):
        _strroi  ='(slice(1, 5), slice(0, 2))'
        obj = self.create_RoiManager(_strroi)
        obj._RoiManager__check_and_convert_str_roi_key_entries()
        self.assertEqual(obj._RoiManager__roi_key,
                         [slice(1, 5), slice(0, 2)])

    def test_check_and_convert_str_roi_key_entries__2slices_with_steps(self):
        _strroi ='(slice(1, 5, 2), slice(0, 2, 1))'
        obj = self.create_RoiManager(_strroi)
        obj._RoiManager__check_and_convert_str_roi_key_entries()
        self.assertEqual(obj._RoiManager__roi_key,
                         [slice(1, 5, 2), slice(0, 2, 1)])

    def test_check_length_of_roi_key_entries(self):
        _roi = [1, 2, slice(0, 2)]
        obj = self.create_RoiManager(_roi)
        obj._RoiManager__check_length_of_roi_key_entries()

    def test_check_length_of_roi_key_entries__too_long(self):
        _roi = [1, 2, slice(0, 2), 4]
        obj = self.create_RoiManager(_roi)
        with self.assertRaises(ValueError):
            obj._RoiManager__check_length_of_roi_key_entries()

    def test_check_length_of_roi_key_entries__too_short(self):
        _roi = [1, 2, 4]
        obj = self.create_RoiManager(_roi)
        with self.assertRaises(ValueError):
            obj._RoiManager__check_length_of_roi_key_entries()

    def test_convert_roi_key_to_slice_objects__4_ints(self):
        _roi = [1, 5, 0, 7]
        obj = self.create_RoiManager(_roi)
        obj._RoiManager__convert_roi_key_to_slice_objects()
        self.assertEqual(obj._RoiManager__roi,
                         (slice(_roi[0], _roi[1]), slice(_roi[2], _roi[3])))

    def test_convert_roi_key_to_slice_objects__2_slices(self):
        _roi = [slice(0, 5), slice(0, 5)]
        obj = self.create_RoiManager(_roi)
        obj._RoiManager__convert_roi_key_to_slice_objects()
        self.assertEqual(obj._RoiManager__roi, (_roi[0], _roi[1]))

    def test_convert_roi_key_to_slice_objects__ints_and_slice(self):
        _roi = [1, 5, slice(0, 5)]
        obj = self.create_RoiManager(_roi)
        obj._RoiManager__convert_roi_key_to_slice_objects()
        self.assertEqual(obj._RoiManager__roi,
                         (slice(_roi[0], _roi[1]), _roi[2]))

    def test_convert_roi_key_to_slice_objects__slice_and_ints(self):
        _roi = [slice(0, 5), 1, 5]
        obj = self.create_RoiManager(_roi)
        obj._RoiManager__convert_roi_key_to_slice_objects()
        self.assertEqual(obj._RoiManager__roi,
                         (_roi[0], slice(_roi[1], _roi[2])))

    def test_convert_roi_key_to_slice_objects__wrong_order(self):
        _roi = [1, slice(0, 5), 1]
        obj = self.create_RoiManager(_roi)
        with self.assertRaises(ValueError):
            obj._RoiManager__convert_roi_key_to_slice_objects()

    def test_convert_roi_key_to_slice_objects__wrong_trailing_order(self):
        obj = RoiManager()
        obj._RoiManager__roi_key = [slice(0, 5), 1, slice(0, 5)]
        with self.assertRaises(ValueError):
            obj._RoiManager__convert_roi_key_to_slice_objects()

    def test_convert_roi_key_to_slice_objects__wrong_length(self):
        _roi = [1, slice(0, 5)]
        obj = self.create_RoiManager(_roi)
        with self.assertRaises(ValueError):
            obj._RoiManager__convert_roi_key_to_slice_objects()

    def test_full_init(self):
        _roi = [slice(0, 5), 1, 5]
        obj = RoiManager(ROI=_roi)
        self.assertEqual(obj._RoiManager__roi,
                         (_roi[0], slice(_roi[1], _roi[2])))

    def test_create_roi_slices(self):
        _roi = [slice(0, 5), 1, 5]
        obj = RoiManager()
        obj._RoiManager__kwargs = {'ROI': _roi}
        obj.create_roi_slices()
        self.assertEqual(obj._RoiManager__roi,
                         (_roi[0], slice(_roi[1], _roi[2])))

    def test_roi_getter(self):
        _roi = [slice(0, 5), 1, 5]
        obj = RoiManager(ROI=_roi)
        self.assertEqual(obj.roi, (_roi[0], slice(_roi[1], _roi[2])))

    def test_roi_setter_from_list(self):
        _roi = [slice(0, 5), 1, 5]
        obj = RoiManager()
        obj.roi = _roi
        self.assertEqual(obj.roi, (_roi[0], slice(_roi[1], _roi[2])))

    def test_roi_setter_from_entries(self):
        _roi = [slice(0, 5), 1, 5]
        obj = RoiManager()
        obj.roi = _roi[0], _roi[1], _roi[2]
        self.assertEqual(obj.roi, (_roi[0], slice(_roi[1], _roi[2])))


if __name__ == "__main__":
    unittest.main()
