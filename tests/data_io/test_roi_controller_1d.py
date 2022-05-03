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

from pydidas.data_io import RoiController1d


class TestRoiController1d(unittest.TestCase):

    def setUp(self):
        self._target_roi = (slice(0, 5, None))

    def tearDown(self):
        ...

    def create_RoiController1d(self, _roi=None):
        obj = RoiController1d()
        if _roi is not None:
            obj._roi_key = copy.copy(_roi)
        obj._check_types_roi_key()
        return obj

    def test_creation(self):
        obj = RoiController1d()
        self.assertIsInstance(obj, RoiController1d)

    def test_modulate_roi_keys__all_positive(self):
        _roi = (slice(3, 7),)
        _shape = (12,)
        obj = RoiController1d()
        obj._roi = _roi
        obj._input_shape = _shape
        obj._modulate_roi_keys()
        self.assertEqual(_roi, obj.roi)

    def test_modulate_roi_keys__all_positive_and_larger_than_shape(self):
        _roi = (slice(1,16),)
        _shape = (12,)
        obj = RoiController1d()
        obj._roi = _roi
        obj._input_shape = _shape
        obj._modulate_roi_keys()
        self.assertEqual(obj.roi[0], slice(_roi[0].start, _shape[0]))

    def test_modulate_roi_keys__with_None_key_and_shape(self):
        _roi = (slice(None, 7),)
        _shape = (12,)
        obj = RoiController1d()
        obj._roi = _roi
        obj._input_shape = _shape
        obj._modulate_roi_keys()
        self.assertEqual(obj.roi[0], slice(0, 7))

    def test_modulate_roi_keys__negative_final_value(self):
        _roi = (slice(1, -1),)
        _shape = (12,)
        obj = RoiController1d()
        obj._roi = _roi
        obj._input_shape = _shape
        obj._modulate_roi_keys()
        self.assertEqual(obj.roi[0], slice(_roi[0].start, _shape[0] - 1))

    def test_modulate_roi_keys__negative_value(self):
        _roi = (slice(-5, -2),)
        _shape = (12,)
        obj = RoiController1d()
        obj._roi = _roi
        obj._input_shape = _shape
        obj._modulate_roi_keys()
        self.assertEqual(obj.roi[0],
                          slice(_roi[0].start + _shape[0],
                                _roi[0].stop + _shape[0]))

    def test_check_length_of_roi_key_entries(self):
        _roi = [slice(0, 2)]
        obj = self.create_RoiController1d(_roi)
        obj._check_length_of_roi_key_entries()

    def test_check_length_of_roi_key_entries__too_long(self):
        _roi = [1, slice(0, 2)]
        obj = self.create_RoiController1d(_roi)
        with self.assertRaises(ValueError):
            obj._check_length_of_roi_key_entries()

    def test_check_length_of_roi_key_entries__too_short(self):
        _roi = [1]
        obj = self.create_RoiController1d(_roi)
        with self.assertRaises(ValueError):
            obj._check_length_of_roi_key_entries()

    def test_convert_roi_key_to_slice_objects__2_ints(self):
        _roi = [1, 5]
        obj = self.create_RoiController1d(_roi)
        obj._convert_roi_key_to_slice_objects()
        self.assertEqual(obj._roi, (slice(_roi[0], _roi[1]), ))

    def test_convert_roi_key_to_slice_objects__1_slice(self):
        _roi = [slice(0, 5)]
        obj = self.create_RoiController1d(_roi)
        obj._convert_roi_key_to_slice_objects()
        self.assertEqual(obj._roi, (_roi[0], ))

    def test_convert_roi_key_to_slice_objects__wrong_length(self):
        _roi = [1, slice(0, 5)]
        obj = self.create_RoiController1d(_roi)
        with self.assertRaises(ValueError):
            obj._convert_roi_key_to_slice_objects()

    def test_full_init(self):
        _roi = [slice(0, 5)]
        obj = RoiController1d(roi=_roi)
        self.assertEqual(obj._roi, (_roi[0], ))

    def test_create_roi_slices(self):
        _roi = [slice(0, 5)]
        obj = RoiController1d()
        obj._roi_key = _roi
        obj.create_roi_slices()
        self.assertEqual(obj._roi, (_roi[0],))

    def test_roi_getter(self):
        _roi = [slice(0, 5)]
        obj = RoiController1d(roi=_roi)
        self.assertEqual(obj.roi, (_roi[0], ))

    def test_roi_coords_getter(self):
        _roi = [1, 5]
        obj = RoiController1d(roi=_roi)
        self.assertEqual(obj.roi_coords, (_roi[0], _roi[1]))

    def test_roi_setter_from_list(self):
        _roi = [1, 5]
        obj = RoiController1d()
        obj.roi = _roi
        self.assertEqual(obj.roi, (slice(_roi[0], _roi[1]), ))

    def test_roi_setter_from_entries(self):
        _roi = [1, 5]
        obj = RoiController1d()
        obj.roi = _roi[0], _roi[1]
        self.assertEqual(obj.roi, (slice(_roi[0], _roi[1]), ))

    def test_roi_setter_from_str(self):
        _roi = [1, 5]
        obj = RoiController1d()
        obj.roi = str(_roi)
        self.assertEqual(obj.roi, (slice(_roi[0], _roi[1]), ))

    def test_roi_setter__None(self):
        _roi = None
        obj = RoiController1d()
        obj.roi = _roi
        self.assertEqual(obj.roi, None)

    def test_roi_setter__again_from_None(self):
        _roi = [1, 5]
        obj = RoiController1d()
        obj.roi = None
        obj.roi = _roi[0], _roi[1]
        self.assertEqual(obj.roi, (slice(_roi[0], _roi[1]), ))

    def test_roi_setter__again_from_roi(self):
        obj = RoiController1d()
        obj.roi = [1, 5]
        obj.roi = None
        self.assertEqual(obj.roi, None)

    def test_merge_rois__two_normal_rois_with_new_start(self):
        obj = RoiController1d()
        obj.roi = [slice(0, 111, None), ]
        _roi2 = (slice(1, 111), )
        obj.apply_second_roi(_roi2)
        self.assertEqual(obj.roi[0].start, 1)
        self.assertEqual(obj.roi[0].stop, 111)

    def test_merge_rois__two_normal_rois_with_ranges(self):
        _start1 = (0, 10)
        _stop1 = (111, 123)
        obj = RoiController1d()
        obj.roi = [slice(_start1[0], _stop1[0])]
        _roi2 = [slice(_start1[1], _stop1[1])]
        obj.apply_second_roi(_roi2)
        self.assertEqual(obj.roi[0].start,
                          _start1[0] + _start1[1])
        self.assertEqual(obj.roi[0].stop,
                          min(_stop1[0], _stop1[1]))

    def test_merge_rois__two_normal_rois_with_ranges_and_offset(self):
        _start1 = (12, 6)
        _stop1 = (111, 123)
        obj = RoiController1d()
        obj.roi = [slice(_start1[0], _stop1[0])]
        _roi2 = [slice(_start1[1], _stop1[1])]
        obj.apply_second_roi(_roi2)
        self.assertEqual(obj.roi[0].start,
                          _start1[0] + _start1[1])
        self.assertEqual(obj.roi[0].stop,
                          min(_stop1[0], _start1[0] + _stop1[1]))

    def test_merge_rois__two_rois_with_None_start(self):
        _x1 = (None, 123)
        _x2 = (43, -2)
        obj = RoiController1d(roi=[slice(*_x1)])
        _roi2 = [slice(*_x2)]
        with self.assertRaises(TypeError):
            obj.apply_second_roi(_roi2)
        self.assertEqual(obj.roi, (slice(*_x1), ))

    def test_merge_rois__two_rois_with_negative_stop_and_shape(self):
        _x1 = (6, 123)
        _x2 = (43, -4)
        _shape = (150, 150)
        obj = RoiController1d(roi=[slice(*_x1)], input_shape=_shape)
        obj.apply_second_roi(_x2)
        _new_x = (_x1[0] + _x2[0], _x1[1] + _x2[1])
        self.assertEqual(obj.roi[0].start, _new_x[0])
        self.assertEqual(obj.roi[0].stop, _new_x[1])

    def test_merge_rois__two_rois_with_None_and_shape(self):
        _x1 = (6, None)
        _x2 = (43, -4)
        _shape = (150, 150)
        obj = RoiController1d(roi=[slice(*_x1)], input_shape=_shape)
        obj.apply_second_roi(_x2)
        _new_x = (_x1[0] + _x2[0], _shape[1] + _x2[1])
        self.assertEqual(obj.roi[0].start, _new_x[0])
        self.assertEqual(obj.roi[0].stop, _new_x[1])


if __name__ == "__main__":
    unittest.main()
