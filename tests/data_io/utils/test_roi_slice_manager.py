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


import unittest
import copy

from pydidas.data_io.utils import RoiSliceManager


class TestRoiSliceManager(unittest.TestCase):

    def setUp(self):
        self._target_roi = (slice(0, 5, None), slice(0, 5, None))

    def tearDown(self):
        ...

    def create_RoiSliceManager(self, _roi=None):
        obj = RoiSliceManager()
        if _roi is not None:
            obj._roi_key = copy.copy(_roi)
        obj._check_types_roi_key()
        return obj

    def create_RoiSliceManager1d(self, _roi=None):
        obj = RoiSliceManager(dim=1)
        if _roi is not None:
            obj._roi_key = copy.copy(_roi)
        obj._check_types_roi_key()
        return obj

    def test_creation(self):
        obj = RoiSliceManager()
        self.assertIsInstance(obj, RoiSliceManager)

    def test_modulate_roi_keys__all_positive(self):
        _roi = (slice(3, 7), slice(1, 6))
        _shape = (12, 12)
        obj = RoiSliceManager()
        obj._roi = _roi
        obj._input_shape = _shape
        obj._modulate_roi_keys()
        self.assertEqual(_roi, obj.roi)

    def test_modulate_roi_keys__all_positive_and_larger_than_shape(self):
        _roi = (slice(3, 7), slice(1, 16))
        _shape = (12, 12)
        obj = RoiSliceManager()
        obj._roi = _roi
        obj._input_shape = _shape
        obj._modulate_roi_keys()
        self.assertEqual(obj.roi[0], _roi[0])
        self.assertEqual(obj.roi[1], slice(_roi[1].start, _shape[1]))

    def test_modulate_roi_keys__with_None_key_and_shape(self):
        _roi = (slice(None, 7), slice(1, None))
        _shape = (12, 12)
        obj = RoiSliceManager()
        obj._roi = _roi
        obj._input_shape = _shape
        obj._modulate_roi_keys()
        self.assertEqual(obj.roi[0], slice(0, 7))
        self.assertEqual(obj.roi[1], slice(_roi[1].start, _shape[1]))

    def test_modulate_roi_keys__negative_final_value(self):
        _roi = (slice(3, 7), slice(1, -1))
        _shape = (12, 12)
        obj = RoiSliceManager()
        obj._roi = _roi
        obj._input_shape = _shape
        obj._modulate_roi_keys()
        self.assertEqual(obj.roi[0], _roi[0])
        self.assertEqual(obj.roi[1], slice(_roi[1].start, _shape[1] - 1))

    def test_modulate_roi_keys__negative_value(self):
        _roi = (slice(3, 7), slice(-5, -2))
        _shape = (12, 12)
        obj = RoiSliceManager()
        obj._roi = _roi
        obj._input_shape = _shape
        obj._modulate_roi_keys()
        self.assertEqual(obj.roi[0], _roi[0])
        self.assertEqual(obj.roi[1],
                         slice(_roi[1].start + _shape[1],
                               _roi[1].stop + _shape[1]))

    def test_check_types_roi_key__w_None(self):
        obj = RoiSliceManager()
        obj._roi_key = None
        obj._check_types_roi_key()
        self.assertEqual(obj._roi_key, None)

    def test_check_types_roi_key__w_list(self):
        _list = ['Test', 'Test2']
        obj = RoiSliceManager()
        obj._roi_key = _list
        obj._check_types_roi_key()
        self.assertEqual(obj._roi_key, _list)

    def test_check_types_roi_key__w_str(self):
        _str = 'Test, Test2'
        obj = RoiSliceManager()
        obj._roi_key = _str
        obj._check_types_roi_key()
        self.assertIsInstance(obj._roi_key, list)

    def test_check_types_roi_key__w_tuple(self):
        _roi = ('Test', 'Test2')
        obj = RoiSliceManager()
        obj._roi_key = _roi
        obj._check_types_roi_key()
        self.assertEqual(obj._roi_key, list(_roi))

    def test_check_types_roi_key__w_set(self):
        _roi = {'Test', 'Test2'}
        obj = RoiSliceManager()
        obj._roi_key = _roi
        with self.assertRaises(ValueError):
            obj._check_types_roi_key()

    def test_convert_str_roi_key_to_list__simple(self):
        _roi = '7, 1234, Test2'
        _list = [item.strip() for item in _roi.split(',')]
        obj = RoiSliceManager()
        obj._roi_key = _roi
        obj._convert_str_roi_key()
        self.assertEqual(obj._roi_key, _list)

    def test_convert_str_roi_key_to_list__slices(self):
        _roi = 'slice(1, 4, 1), slice(0, 4)'
        _list = [item.strip() for item in _roi.split(',')]
        obj = RoiSliceManager()
        obj._roi_key = _roi
        obj._convert_str_roi_key()
        self.assertEqual(obj._roi_key, _list)

    def test_convert_str_roi_key_to_list__with_brackets(self):
        _roi = '(slice(1, 4, 1), slice(0, 4))'
        _list = [item.strip() for item in _roi[1:-1].split(',')]
        obj = RoiSliceManager()
        obj._roi_key = _roi
        obj._convert_str_roi_key()
        self.assertEqual(obj._roi_key, _list)

    def test_convert_str_roi_key_to_list__with_straight_brackets(self):
        _roi = '[slice(1, 4, 1), slice(0, 4)]'
        _list = [item.strip() for item in _roi[1:-1].split(',')]
        obj = RoiSliceManager()
        obj._roi_key = _roi
        obj._convert_str_roi_key()
        self.assertEqual(obj._roi_key, _list)

    def test_convert_str_roi_key_to_list__only_leading_bracket(self):
        _roi = '(slice(1, 4, 1), slice(0, 4)'
        _list = [item.strip() for item in _roi[1:].split(',')]
        obj = RoiSliceManager()
        obj._roi_key = _roi
        obj._convert_str_roi_key()
        self.assertEqual(obj._roi_key, _list)

    def test_convert_str_roi_key_to_list__only_leading_bracket_and_ints(self):
        _roi = '(slice(1, 4, 1), 0, 4'
        _list = [item.strip() for item in _roi[1:].split(',')]
        obj = RoiSliceManager()
        obj._roi_key = _roi
        obj._convert_str_roi_key()
        self.assertEqual(obj._roi_key, _list)

    def test_convert_str_roi_key_to_list__only_trailing_bracket_and_ints(self):
        _roi = '0, 4, slice(1, 4, 1))'
        _list = [item.strip() for item in _roi[:-1].split(',')]
        obj = RoiSliceManager()
        obj._roi_key = _roi
        obj._convert_str_roi_key()
        self.assertEqual(obj._roi_key, _list)

    def test_check_types_roi_key_entries(self):
        obj = RoiSliceManager()
        obj._roi_key = [12, slice(0, 2)]
        obj._check_types_roi_key_entries

    def test_check_types_roi_key_entries__w_float(self):
        obj = self.create_RoiSliceManager()
        obj._roi_key = [12, slice(0, 15), 12.3]
        with self.assertRaises(ValueError):
            obj._check_types_roi_key_entries()

    def test_convert_str_roi_key_entries__int(self):
        _roi = [1, 2, 3, 4]
        _strroi = ', '.join(str(item) for item in _roi)
        obj = self.create_RoiSliceManager(_strroi)
        obj._convert_str_roi_key_entries()
        self.assertEqual(obj._roi_key, _roi)

    def test_convert_str_roi_key_entries__float(self):
        _roi = [1, 2, 3, 4.0]
        _strroi = ', '.join(str(item) for item in _roi)
        obj = self.create_RoiSliceManager(_strroi)
        with self.assertRaises(ValueError):
            obj._convert_str_roi_key_entries()

    def test_convert_str_roi_key_entries__slice_last(self):
        _roi = [1, 2, slice(0, 2)]
        _strroi = ', '.join(str(item) for item in _roi)
        obj = self.create_RoiSliceManager(_strroi)
        obj._convert_str_roi_key_entries()
        self.assertEqual(obj._roi_key, _roi)

    def test_convert_str_roi_key_entries__slice_first(self):
        _roi = [slice(0, 2), 1, 2]
        _strroi = ', '.join(str(item) for item in _roi)
        obj = self.create_RoiSliceManager(_strroi)
        obj._convert_str_roi_key_entries()
        self.assertEqual(obj._roi_key, _roi)

    def test_convert_str_roi_key_entries__2slices(self):
        _roi = [slice(1, 3, 5), slice(0, 2)]
        _strroi = ', '.join(str(item) for item in _roi)
        obj = self.create_RoiSliceManager(_strroi)
        obj._convert_str_roi_key_entries()
        self.assertEqual(obj._roi_key, _roi)

    def test_convert_str_roi_key_entries__2slices_wo_steps(self):
        _strroi = '(slice(1, 5), slice(0, 2))'
        obj = self.create_RoiSliceManager(_strroi)
        obj._convert_str_roi_key_entries()
        self.assertEqual(obj._roi_key, [slice(1, 5), slice(0, 2)])

    def test_convert_str_roi_key_entries__2slices_with_steps(self):
        _strroi = '(slice(1, 5, 2), slice(0, 2, 1))'
        obj = self.create_RoiSliceManager(_strroi)
        obj._convert_str_roi_key_entries()
        self.assertEqual(obj._roi_key, [slice(1, 5, 2), slice(0, 2, 1)])

    def test_check_length_of_roi_key_entries(self):
        _roi = [1, 2, slice(0, 2)]
        obj = self.create_RoiSliceManager(_roi)
        obj._check_length_of_roi_key_entries()

    def test_check_length_of_roi_key_entries__too_long(self):
        _roi = [1, 2, slice(0, 2), 4]
        obj = self.create_RoiSliceManager(_roi)
        with self.assertRaises(ValueError):
            obj._check_length_of_roi_key_entries()

    def test_check_length_of_roi_key_entries__too_short(self):
        _roi = [1, 2, 4]
        obj = self.create_RoiSliceManager(_roi)
        with self.assertRaises(ValueError):
            obj._check_length_of_roi_key_entries()

    def test_convert_roi_key_to_slice_objects__4_ints(self):
        _roi = [1, 5, 0, 7]
        obj = self.create_RoiSliceManager(_roi)
        obj._convert_roi_key_to_slice_objects()
        self.assertEqual(obj._roi,
                         (slice(_roi[0], _roi[1]), slice(_roi[2], _roi[3])))

    def test_convert_roi_key_to_slice_objects__2_slices(self):
        _roi = [slice(0, 5), slice(0, 5)]
        obj = self.create_RoiSliceManager(_roi)
        obj._convert_roi_key_to_slice_objects()
        self.assertEqual(obj._roi, (_roi[0], _roi[1]))

    def test_convert_roi_key_to_slice_objects__ints_and_slice(self):
        _roi = [1, 5, slice(0, 5)]
        obj = self.create_RoiSliceManager(_roi)
        obj._convert_roi_key_to_slice_objects()
        self.assertEqual(obj._roi, (slice(_roi[0], _roi[1]), _roi[2]))

    def test_convert_roi_key_to_slice_objects__slice_and_ints(self):
        _roi = [slice(0, 5), 1, 5]
        obj = self.create_RoiSliceManager(_roi)
        obj._convert_roi_key_to_slice_objects()
        self.assertEqual(obj._roi, (_roi[0], slice(_roi[1], _roi[2])))

    def test_convert_roi_key_to_slice_objects__wrong_order(self):
        _roi = [1, slice(0, 5), 1]
        obj = self.create_RoiSliceManager(_roi)
        with self.assertRaises(ValueError):
            obj._convert_roi_key_to_slice_objects()

    def test_convert_roi_key_to_slice_objects__wrong_trailing_order(self):
        obj = RoiSliceManager()
        obj._roi_key = [slice(0, 5), 1, slice(0, 5)]
        with self.assertRaises(ValueError):
            obj._convert_roi_key_to_slice_objects()

    def test_convert_roi_key_to_slice_objects__wrong_length(self):
        _roi = [1, slice(0, 5)]
        obj = self.create_RoiSliceManager(_roi)
        with self.assertRaises(ValueError):
            obj._convert_roi_key_to_slice_objects()

    def test_full_init(self):
        _roi = [slice(0, 5), 1, 5]
        obj = RoiSliceManager(roi=_roi)
        self.assertEqual(obj._roi, (_roi[0], slice(_roi[1], _roi[2])))

    def test_create_roi_slices(self):
        _roi = [slice(0, 5), 1, 5]
        obj = RoiSliceManager()
        obj._roi_key = _roi
        obj.create_roi_slices()
        self.assertEqual(obj._roi, (_roi[0], slice(_roi[1], _roi[2])))

    def test_roi_getter(self):
        _roi = [slice(0, 5), 1, 5]
        obj = RoiSliceManager(roi=_roi)
        self.assertEqual(obj.roi, (_roi[0], slice(_roi[1], _roi[2])))

    def test_roi_coords_getter(self):
        _roi = [slice(0, 5), 1, 5]
        obj = RoiSliceManager(roi=_roi)
        self.assertEqual(obj.roi_coords,
                         (_roi[0].start, _roi[0].stop, _roi[1], _roi[2]))

    def test_roi_setter_from_list(self):
        _roi = [slice(0, 5), 1, 5]
        obj = RoiSliceManager()
        obj.roi = _roi
        self.assertEqual(obj.roi, (_roi[0], slice(_roi[1], _roi[2])))

    def test_roi_setter_from_entries(self):
        _roi = [slice(0, 5), 1, 5]
        obj = RoiSliceManager()
        obj.roi = _roi[0], _roi[1], _roi[2]
        self.assertEqual(obj.roi, (_roi[0], slice(_roi[1], _roi[2])))

    def test_roi_setter_from_str(self):
        _roi = [slice(0, 5), 1, 5]
        obj = RoiSliceManager()
        obj.roi = str(_roi)
        self.assertEqual(obj.roi, (_roi[0], slice(_roi[1], _roi[2])))

    def test_roi_setter__None(self):
        _roi = None
        obj = RoiSliceManager()
        obj.roi = _roi
        self.assertEqual(obj.roi, None)

    def test_roi_setter__again_from_None(self):
        _roi = [slice(0, 5), 1, 5]
        obj = RoiSliceManager()
        obj.roi = None
        obj.roi = _roi[0], _roi[1], _roi[2]
        self.assertEqual(obj.roi, (_roi[0], slice(_roi[1], _roi[2])))

    def test_roi_setter__again_from_roi(self):
        obj = RoiSliceManager()
        obj.roi = [slice(0, 5), 1, 5]
        obj.roi = None
        self.assertEqual(obj.roi, None)

    def test_merge_rois__two_normal_rois_with_new_start(self):
        obj = RoiSliceManager()
        obj.roi = [slice(0, 111, None), slice(0, 111, None)]
        _roi2 = (slice(1, 111), slice(1, 111))
        obj.apply_second_roi(_roi2)
        for _axis in [0, 1]:
            self.assertEqual(obj.roi[_axis].start, 1)
            self.assertEqual(obj.roi[_axis].stop, 111)

    def test_merge_rois__two_normal_rois_with_ranges(self):
        _start1 = (0, 0)
        _stop1 = (111, 123)
        _start2 = (7, 43)
        _stop2 = (97, 98)
        obj = RoiSliceManager()
        obj.roi = [slice(_start1[0], _stop1[0]),
                   slice(_start1[1], _stop1[1])]
        _roi2 = [slice(_start2[0], _stop2[0]),
                 slice(_start2[1], _stop2[1])]
        obj.apply_second_roi(_roi2)
        for _axis in [0, 1]:
            self.assertEqual(obj.roi[_axis].start,
                             _start1[_axis] + _start2[_axis])
            self.assertEqual(obj.roi[_axis].stop,
                             min(_stop1[_axis], _stop2[_axis]))

    def test_merge_rois__two_normal_rois_with_ranges_and_offset(self):
        _start1 = (12, 6)
        _stop1 = (111, 123)
        _start2 = (7, 43)
        _stop2 = (97, 98)
        obj = RoiSliceManager()
        obj.roi = [slice(_start1[0], _stop1[0]),
                   slice(_start1[1], _stop1[1])]
        _roi2 = [slice(_start2[0], _stop2[0]),
                 slice(_start2[1], _stop2[1])]
        obj.apply_second_roi(_roi2)
        for _axis in [0, 1]:
            self.assertEqual(
                obj.roi[_axis].start, _start1[_axis] + _start2[_axis])
            self.assertEqual(
                obj.roi[_axis].stop,
                min(_stop1[_axis], _start1[_axis] + _stop2[_axis]))

    def test_merge_rois__two_rois_with_negative_stop(self):
        _y1 = (12, -3)
        _x1 = (6, 123)
        _y2 = (7, 97)
        _x2 = (43, -4)
        obj = RoiSliceManager(roi=[slice(*_y1), slice(*_x1)])
        _roi2 = [slice(*_y2), slice(*_x2)]
        with self.assertRaises(TypeError):
            obj.apply_second_roi(_roi2)
        self.assertEqual(obj.roi, (slice(*_y1), slice(*_x1)))

    def test_merge_rois__two_rois_with_negative_stop_and_shape(self):
        _y1 = (12, -3)
        _x1 = (6, 123)
        _y2 = (7, 97)
        _x2 = (43, -4)
        _shape = (150, 150)
        obj = RoiSliceManager(roi=[slice(*_y1), slice(*_x1)],
                              input_shape=_shape)
        _roi2 = [slice(*_y2), slice(*_x2)]
        _roi2 = _y2 + _x2
        obj.apply_second_roi(_roi2)
        _new_y = (_y1[0] + _y2[0], _y2[1] + _y1[0])
        _new_x = (_x1[0] + _x2[0], _x1[1] + _x2[1])
        self.assertEqual(obj.roi[0].start, _new_y[0])
        self.assertEqual(obj.roi[0].stop, _new_y[1])
        self.assertEqual(obj.roi[1].start, _new_x[0])
        self.assertEqual(obj.roi[1].stop, _new_x[1])

    def test_merge_rois__two_rois_with_None_and_shape(self):
        _y1 = (12, -3)
        _x1 = (6, None)
        _y2 = (None, 97)
        _x2 = (43, -4)
        _shape = (150, 150)
        obj = RoiSliceManager(roi=[slice(*_y1), slice(*_x1)],
                              input_shape=_shape)
        _roi2 = [slice(*_y2), slice(*_x2)]
        _roi2 = _y2 + _x2
        obj.apply_second_roi(_roi2)
        _new_y = (_y1[0] + 0, _y2[1] + _y1[0])
        _new_x = (_x1[0] + _x2[0], _shape[1] + _x2[1])
        self.assertEqual(obj.roi[0].start, _new_y[0])
        self.assertEqual(obj.roi[0].stop, _new_y[1])
        self.assertEqual(obj.roi[1].start, _new_x[0])
        self.assertEqual(obj.roi[1].stop, _new_x[1])

    def test_modulate_roi_keys_1d__all_positive(self):
        _roi = (slice(3, 7),)
        _shape = (12,)
        obj = RoiSliceManager(dim=1)
        obj._roi = _roi
        obj._input_shape = _shape
        obj._modulate_roi_keys()
        self.assertEqual(_roi, obj.roi)

    def test_modulate_roi_keys_1d__all_positive_and_larger_than_shape(self):
        _roi = (slice(1, 16),)
        _shape = (12,)
        obj = RoiSliceManager(dim=1)
        obj._roi = _roi
        obj._input_shape = _shape
        obj._modulate_roi_keys()
        self.assertEqual(obj.roi[0], slice(_roi[0].start, _shape[0]))

    def test_modulate_roi_keys_1d__with_None_key_and_shape(self):
        _roi = (slice(None, 7),)
        _shape = (12,)
        obj = RoiSliceManager(dim=1)
        obj._roi = _roi
        obj._input_shape = _shape
        obj._modulate_roi_keys()
        self.assertEqual(obj.roi[0], slice(0, 7))

    def test_modulate_roi_keys_1d__negative_final_value(self):
        _roi = (slice(1, -1),)
        _shape = (12,)
        obj = RoiSliceManager(dim=1)
        obj._roi = _roi
        obj._input_shape = _shape
        obj._modulate_roi_keys()
        self.assertEqual(obj.roi[0], slice(_roi[0].start, _shape[0] - 1))

    def test_modulate_roi_keys_1d__negative_value(self):
        _roi = (slice(-5, -2),)
        _shape = (12,)
        obj = RoiSliceManager(dim=1)
        obj._roi = _roi
        obj._input_shape = _shape
        obj._modulate_roi_keys()
        self.assertEqual(obj.roi[0],
                         slice(_roi[0].start + _shape[0],
                               _roi[0].stop + _shape[0]))

    def test_check_length_of_roi_key_entries_1d(self):
        _roi = [slice(0, 2)]
        obj = self.create_RoiSliceManager1d(_roi)
        obj._check_length_of_roi_key_entries()

    def test_check_length_of_roi_key_entries_1d__too_long(self):
        _roi = [1, slice(0, 2)]
        obj = self.create_RoiSliceManager1d(_roi)
        with self.assertRaises(ValueError):
            obj._check_length_of_roi_key_entries()

    def test_check_length_of_roi_key_entries_1d__too_short(self):
        _roi = [1]
        obj = self.create_RoiSliceManager1d(_roi)
        with self.assertRaises(ValueError):
            obj._check_length_of_roi_key_entries()

    def test_convert_roi_key_to_slice_objects_1d__2_ints(self):
        _roi = [1, 5]
        obj = self.create_RoiSliceManager1d(_roi)
        obj._convert_roi_key_to_slice_objects()
        self.assertEqual(obj._roi, (slice(_roi[0], _roi[1]), ))

    def test_convert_roi_key_to_slice_objects_1d__1_slice(self):
        _roi = [slice(0, 5)]
        obj = self.create_RoiSliceManager1d(_roi)
        obj._convert_roi_key_to_slice_objects()
        self.assertEqual(obj._roi, (_roi[0], ))

    def test_convert_roi_key_to_slice_objects_1d__wrong_length(self):
        _roi = [1, slice(0, 5)]
        obj = self.create_RoiSliceManager1d(_roi)
        with self.assertRaises(ValueError):
            obj._convert_roi_key_to_slice_objects()

    def test_full_init_1d(self):
        _roi = [slice(0, 5)]
        obj = RoiSliceManager(roi=_roi, dim=1)
        self.assertEqual(obj._roi, (_roi[0], ))

    def test_create_roi_slices_1d(self):
        _roi = [slice(0, 5)]
        obj = RoiSliceManager(dim=1)
        obj._roi_key = _roi
        obj.create_roi_slices()
        self.assertEqual(obj._roi, (_roi[0],))

    def test_roi_getter_1d(self):
        _roi = [slice(0, 5)]
        obj = RoiSliceManager(roi=_roi, dim=1)
        self.assertEqual(obj.roi, (_roi[0], ))

    def test_roi_coords_getter_1d(self):
        _roi = [1, 5]
        obj = RoiSliceManager(roi=_roi, dim=1)
        self.assertEqual(obj.roi_coords, (_roi[0], _roi[1]))

    def test_roi_setter_from_list_1d(self):
        _roi = [1, 5]
        obj = RoiSliceManager(dim=1)
        obj.roi = _roi
        self.assertEqual(obj.roi, (slice(_roi[0], _roi[1]), ))

    def test_roi_setter_from_entries_1d(self):
        _roi = [1, 5]
        obj = RoiSliceManager(dim=1)
        obj.roi = _roi[0], _roi[1]
        self.assertEqual(obj.roi, (slice(_roi[0], _roi[1]), ))

    def test_roi_setter_from_str_1d(self):
        _roi = [1, 5]
        obj = RoiSliceManager(dim=1)
        obj.roi = str(_roi)
        self.assertEqual(obj.roi, (slice(_roi[0], _roi[1]), ))

    def test_roi_setter_1d__None(self):
        _roi = None
        obj = RoiSliceManager(dim=1)
        obj.roi = _roi
        self.assertEqual(obj.roi, None)

    def test_roi_setter_1d__again_from_None(self):
        _roi = [1, 5]
        obj = RoiSliceManager(dim=1)
        obj.roi = None
        obj.roi = _roi[0], _roi[1]
        self.assertEqual(obj.roi, (slice(_roi[0], _roi[1]), ))

    def test_roi_setter_1d__again_from_roi(self):
        obj = RoiSliceManager(dim=1)
        obj.roi = [1, 5]
        obj.roi = None
        self.assertEqual(obj.roi, None)

    def test_merge_rois_1d__two_normal_rois_with_new_start(self):
        obj = RoiSliceManager(dim=1)
        obj.roi = [slice(0, 111, None), ]
        _roi2 = (slice(1, 111), )
        obj.apply_second_roi(_roi2)
        self.assertEqual(obj.roi[0].start, 1)
        self.assertEqual(obj.roi[0].stop, 111)

    def test_merge_rois_1d__two_normal_rois_with_ranges(self):
        _start1 = (0, 10)
        _stop1 = (111, 123)
        obj = RoiSliceManager(dim=1)
        obj.roi = [slice(_start1[0], _stop1[0])]
        _roi2 = [slice(_start1[1], _stop1[1])]
        obj.apply_second_roi(_roi2)
        self.assertEqual(obj.roi[0].start, _start1[0] + _start1[1])
        self.assertEqual(obj.roi[0].stop, min(_stop1[0], _stop1[1]))

    def test_merge_rois_1d__two_normal_rois_with_ranges_and_offset(self):
        _start1 = (12, 6)
        _stop1 = (111, 123)
        obj = RoiSliceManager(dim=1)
        obj.roi = [slice(_start1[0], _stop1[0])]
        _roi2 = [slice(_start1[1], _stop1[1])]
        obj.apply_second_roi(_roi2)
        self.assertEqual(obj.roi[0].start, _start1[0] + _start1[1])
        self.assertEqual(obj.roi[0].stop,
                         min(_stop1[0], _start1[0] + _stop1[1]))

    def test_merge_rois_1d__two_rois_with_None_start(self):
        _x1 = (None, 123)
        _x2 = (43, -2)
        obj = RoiSliceManager(roi=[slice(*_x1)], dim=1)
        _roi2 = [slice(*_x2)]
        with self.assertRaises(TypeError):
            obj.apply_second_roi(_roi2)
        self.assertEqual(obj.roi, (slice(*_x1), ))

    def test_merge_rois_1d__two_rois_with_negative_stop_and_shape(self):
        _x1 = (6, 123)
        _x2 = (43, -4)
        _shape = (150, 150)
        obj = RoiSliceManager(roi=[slice(*_x1)], input_shape=_shape, dim=1)
        obj.apply_second_roi(_x2)
        _new_x = (_x1[0] + _x2[0], _x1[1] + _x2[1])
        self.assertEqual(obj.roi[0].start, _new_x[0])
        self.assertEqual(obj.roi[0].stop, _new_x[1])

    def test_merge_rois_1d__two_rois_with_None_and_shape(self):
        _x1 = (6, None)
        _x2 = (43, -4)
        _shape = (150, 150)
        obj = RoiSliceManager(roi=[slice(*_x1)], input_shape=_shape, dim=1)
        obj.apply_second_roi(_x2)
        _new_x = (_x1[0] + _x2[0], _shape[1] + _x2[1])
        self.assertEqual(obj.roi[0].start, _new_x[0])
        self.assertEqual(obj.roi[0].stop, _new_x[1])


if __name__ == "__main__":
    unittest.main()
