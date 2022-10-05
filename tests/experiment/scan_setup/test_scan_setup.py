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

import numpy as np

from pydidas.core import UserConfigError
from pydidas.core.utils import get_random_string
from pydidas.experiment import SetupScan
from pydidas.experiment.setup_scan.setup_scan import _SetupScan


class TestSetupScan(unittest.TestCase):
    def setUp(self):
        self._scan_shape = (5, 7, 3, 2)
        self._scan_delta = (0.1, 0.5, 1, 1.5)
        self._scan_offset = (3, -1, 0, 0.5)

    def tearDown(self):
        ...

    def set_scan_params(self, _scan):
        _scan.set_param_value("scan_dim", 4)
        for index, val in enumerate(self._scan_shape):
            _scan.set_param_value(f"scan_dim{index}_n_points", val)
        for index, val in enumerate(self._scan_delta):
            _scan.set_param_value(f"scan_dim{index}_delta", val)
        for index, val in enumerate(self._scan_offset):
            _scan.set_param_value(f"scan_dim{index}_offset", val)

    def get_scan_range(self, dim):
        return np.linspace(
            self._scan_offset[dim],
            (
                self._scan_offset[dim]
                + (self._scan_shape[dim] - 1) * self._scan_delta[dim]
            ),
            num=self._scan_shape[dim],
        )

    def test_setup(self):
        # assert no Exception in setUp method.
        pass

    def test_init(self):
        SCAN = _SetupScan()
        self.assertIsInstance(SCAN, _SetupScan)

    def test_init_singleton(self):
        SCAN = SetupScan()
        self.assertIsInstance(SCAN, _SetupScan)

    def test_n_total(self):
        SCAN = _SetupScan()
        self.set_scan_params(SCAN)
        self.assertEqual(SCAN.n_points, np.prod(self._scan_shape))

    def test_shape(self):
        SCAN = _SetupScan()
        self.set_scan_params(SCAN)
        self.assertEqual(SCAN.shape, self._scan_shape)

    def test_ndim(self):
        SCAN = _SetupScan()
        self.set_scan_params(SCAN)
        self.assertEqual(SCAN.ndim, 4)

    def test_get_range_for_dim__wrong_dim(self):
        SCAN = _SetupScan()
        self.set_scan_params(SCAN)
        with self.assertRaises(UserConfigError):
            SCAN.get_range_for_dim(5)

    def test_get_range_for_dim__empty_dim(self):
        SCAN = _SetupScan()
        _range = SCAN.get_range_for_dim(1)
        self.assertIsInstance(_range, np.ndarray)

    def test_get_range_for_dim__normal(self):
        _index = 1
        SCAN = _SetupScan()
        self.set_scan_params(SCAN)
        _range = SCAN.get_range_for_dim(_index)
        _target = self.get_scan_range(_index)
        self.assertTrue(np.equal(_range, _target).all())

    def test_get_metadata_for_dim(self):
        SCAN = _SetupScan()
        self.set_scan_params(SCAN)
        for _index in range(4):
            _unit = get_random_string(5)
            _label = get_random_string(20)
            SCAN.set_param_value(f"scan_dim{_index}_unit", _unit)
            SCAN.set_param_value(f"scan_dim{_index}_label", _label)
            _scanlabel, _scanunit, _range = SCAN.get_metadata_for_dim(_index)
            self.assertEqual(_scanlabel, _label)
            self.assertEqual(_unit, _scanunit)
            self.assertTrue(np.equal(self.get_scan_range(_index), _range).all())

    def test_get_frame_position_in_scan__zero(self):
        SCAN = _SetupScan()
        self.set_scan_params(SCAN)
        _index = SCAN.get_frame_position_in_scan(0)
        self.assertEqual(_index, (0, 0, 0, 0))

    def test_get_frame_position_in_scan__inscan(self):
        SCAN = _SetupScan()
        self.set_scan_params(SCAN)
        _pos = tuple(i - 1 for i in self._scan_shape)
        _tmpshape = self._scan_shape + (1,)
        _n = np.sum(
            [
                _pos[i] * np.prod(_tmpshape[i + 1 :])
                for i in range(SCAN.get_param_value("scan_dim"))
            ]
        )
        _index = SCAN.get_frame_position_in_scan(_n)
        self.assertEqual(_index, _pos)

    def test_get_frame_position_in_scan__negative(self):
        SCAN = _SetupScan()
        self.set_scan_params(SCAN)
        with self.assertRaises(UserConfigError):
            SCAN.get_frame_position_in_scan(-1)

    def test_get_frame_position_in_scan__too_large(self):
        SCAN = _SetupScan()
        self.set_scan_params(SCAN)
        with self.assertRaises(UserConfigError):
            SCAN.get_frame_position_in_scan(np.prod(self._scan_shape))

    def test_get_frame_position_in_scan__multiplicity_gt_one(self):
        SCAN = _SetupScan()
        self.set_scan_params(SCAN)
        SCAN.set_param_value("scan_multiplicity", 3)
        _pos = tuple(i - 1 for i in self._scan_shape)
        _tmpshape = self._scan_shape + (3,)
        _n = np.sum(
            [
                _pos[i] * np.prod(_tmpshape[i + 1 :])
                for i in range(SCAN.get_param_value("scan_dim"))
            ]
        )
        _index = SCAN.get_frame_position_in_scan(_n)
        self.assertEqual(_index, _pos)

    def test_get_frame_number_from_scan_indices__zero(self):
        SCAN = _SetupScan()
        self.set_scan_params(SCAN)
        _index = SCAN.get_frame_number_from_scan_indices((0, 0, 0, 0))
        self.assertEqual(_index, 0)

    def test_get_frame_number_from_scan_indices__negative(self):
        SCAN = _SetupScan()
        self.set_scan_params(SCAN)
        with self.assertRaises(UserConfigError):
            SCAN.get_frame_number_from_scan_indices((0, -1, 0, 0))

    def test_get_frame_number_from_scan_indices__inscan(self):
        _indices = (2, 1, 2, 1)
        _frame = (
            _indices[3]
            + self._scan_shape[3] * _indices[2]
            + np.prod(self._scan_shape[2:]) * _indices[1]
            + np.prod(self._scan_shape[1:]) * _indices[0]
        )
        SCAN = _SetupScan()
        self.set_scan_params(SCAN)
        _index = SCAN.get_frame_number_from_scan_indices(_indices)
        self.assertEqual(_index, _frame)

    def test_get_frame_number_from_scan_indices__multiplicity_gt_one(self):
        _indices = (2, 1, 2, 1)
        _frame = (
            _indices[3]
            + self._scan_shape[3] * _indices[2]
            + np.prod(self._scan_shape[2:]) * _indices[1]
            + np.prod(self._scan_shape[1:]) * _indices[0]
        ) * 3
        SCAN = _SetupScan()
        self.set_scan_params(SCAN)
        SCAN.set_param_value("scan_multiplicity", 3)
        _index = SCAN.get_frame_number_from_scan_indices(_indices)
        self.assertEqual(_index, _frame)

    def test_update_from_dictionary__missing_dim(self):
        _scan = {"scan_title": get_random_string(8), "scan_dim": 2}
        SCAN = _SetupScan()
        with self.assertRaises(KeyError):
            SCAN.update_from_dictionary(_scan)

    def test_update_from_dictionary__empty_input(self):
        _title = get_random_string(8)
        SCAN = _SetupScan()
        SCAN.set_param_value("scan_title", _title)
        SCAN.update_from_dictionary({})
        self.assertEqual(SCAN.get_param_value("scan_title"), _title)

    def test_update_from_dictionary__all_entries_present(self):
        _scan = {
            "scan_title": get_random_string(8),
            "scan_dim": 2,
            "scan_base_directory": "/dummy",
            "scan_name_pattern": "test_###",
            "scan_start_index": 1,
            "scan_index_stepping": 1,
            "scan_multiplicity": 1,
            "scan_multi_image_handling": "Sum",
            0: {
                "label": get_random_string(5),
                "unit": get_random_string(3),
                "delta": 1,
                "offset": -5,
                "n_points": 42,
            },
            1: {
                "label": get_random_string(5),
                "unit": get_random_string(3),
                "delta": 3,
                "offset": 12,
                "n_points": 8,
            },
        }
        SCAN = _SetupScan()
        SCAN.update_from_dictionary(_scan)
        self.assertEqual(SCAN.get_param_value("scan_title"), _scan["scan_title"])
        self.assertEqual(SCAN.get_param_value("scan_dim"), _scan["scan_dim"])
        for _dim in [0, 1]:
            for _entry in ["label", "unit", "offset", "delta", "n_points"]:
                self.assertEqual(
                    _scan[_dim][_entry],
                    SCAN.get_param_value(f"scan_dim{_dim}_{_entry}"),
                )


if __name__ == "__main__":
    unittest.main()
