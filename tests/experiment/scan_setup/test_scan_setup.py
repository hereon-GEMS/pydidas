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
__version__ = "0.1.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"


import unittest

import numpy as np

from pydidas.core.utils import get_random_string
from pydidas.experiment import ScanSetup
from pydidas.experiment.scan_setup.scan_setup import _ScanSetup


class TestScanSetup(unittest.TestCase):

    def setUp(self):
        self._scan_shape = (5, 7, 3, 2)
        self._scan_delta = (0.1, 0.5, 1, 1.5)
        self._scan_offset = (3, -1, 0, 0.5)

    def tearDown(self):
        ...

    def set_scan_params(self, _scan_settings):
        _scan_settings.set_param_value('scan_dim', 4)
        for index, val in enumerate(self._scan_shape):
            _scan_settings.set_param_value(f'n_points_{index + 1}', val)
        for index, val in enumerate(self._scan_delta):
            _scan_settings.set_param_value(f'delta_{index + 1}', val)
        for index, val in enumerate(self._scan_offset):
            _scan_settings.set_param_value(f'offset_{index + 1}', val)

    def get_scan_range(self, dim):
        return np.linspace(
            self._scan_offset[dim],
            (self._scan_offset[dim] + (self._scan_shape[dim] - 1)
             * self._scan_delta[dim]), num=self._scan_shape[dim])

    def test_setup(self):
        # assert no Exception in setUp method.
        pass

    def test_init(self):
        SCAN = _ScanSetup()
        self.assertIsInstance(SCAN, _ScanSetup)

    def test_init_singleton(self):
        SCAN = ScanSetup()
        self.assertIsInstance(SCAN, _ScanSetup)

    def test_n_total(self):
        SCAN = _ScanSetup()
        self.set_scan_params(SCAN)
        self.assertEqual(SCAN.n_total, np.prod(self._scan_shape))

    def test_shape(self):
        SCAN = _ScanSetup()
        self.set_scan_params(SCAN)
        self.assertEqual(SCAN.shape, self._scan_shape)

    def test_ndim(self):
        SCAN = _ScanSetup()
        self.set_scan_params(SCAN)
        self.assertEqual(SCAN.ndim, 4)

    def test_get_range_for_dim__wrong_dim(self):
        SCAN = _ScanSetup()
        self.set_scan_params(SCAN)
        with self.assertRaises(ValueError):
            SCAN.get_range_for_dim(5)

    def test_get_range_for_dim__empty_dim(self):
        SCAN = _ScanSetup()
        _range = SCAN.get_range_for_dim(1)
        self.assertIsInstance(_range, np.ndarray)

    def test_get_range_for_dim__normal(self):
        _index = 1
        SCAN = _ScanSetup()
        self.set_scan_params(SCAN)
        _range = SCAN.get_range_for_dim(_index + 1)
        _target = self.get_scan_range(_index)
        self.assertTrue(np.equal(_range, _target).all())

    def test_get_metadata_for_dim(self):
        _index = 1
        _unit = get_random_string(5)
        _label = get_random_string(20)
        SCAN = _ScanSetup()
        SCAN.set_param_value(f'unit_{_index + 1}', _unit)
        SCAN.set_param_value(f'scan_dir_{_index + 1}', _label)
        self.set_scan_params(SCAN)
        _scanlabel, _scanunit, _range = SCAN.get_metadata_for_dim(_index + 1)
        self.assertEqual(_scanlabel, _label)
        self.assertEqual(_unit, _scanunit)
        self.assertTrue(np.equal(self.get_scan_range(_index), _range).all())

    def test_get_frame_position_in_scan__zero(self):
        SCAN = _ScanSetup()
        self.set_scan_params(SCAN)
        _index = SCAN.get_frame_position_in_scan(0)
        self.assertEqual(_index, (0, 0, 0, 0))

    def test_get_frame_position_in_scan__inscan(self):
        SCAN = _ScanSetup()
        self.set_scan_params(SCAN)
        _pos = tuple(i - 1 for i in self._scan_shape)
        _tmpshape = self._scan_shape + (1, )
        _n = np.sum([_pos[i] * np.prod(_tmpshape[i + 1:])
                     for i in range(SCAN.get_param_value('scan_dim'))])
        _index = SCAN.get_frame_position_in_scan(_n)
        self.assertEqual(_index, _pos)

    def test_get_frame_position_in_scan__negative(self):
        SCAN = _ScanSetup()
        self.set_scan_params(SCAN)
        with self.assertRaises(ValueError):
            SCAN.get_frame_position_in_scan(-1)

    def test_get_frame_position_in_scan__too_large(self):
        SCAN = _ScanSetup()
        self.set_scan_params(SCAN)
        with self.assertRaises(ValueError):
            SCAN.get_frame_position_in_scan(np.prod(self._scan_shape))


if __name__ == "__main__":
    unittest.main()
