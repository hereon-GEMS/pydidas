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
import tempfile
import shutil
import os

import h5py
import numpy as np

from pydidas.image_io.low_level_readers.read_hdf5_slice import (
    read_hdf5_slice, get_selection)


class TestReadHdf5Slice(unittest.TestCase):

    def setUp(self):
        self._path = tempfile.mkdtemp()
        self._fname = os.path.join(self._path, 'test.h5')
        self._img_shape = (10, 10, 10, 10)
        self._data = np.random.random(self._img_shape)
        with h5py.File(self._fname, 'w') as _file:
            _file.create_group('test')
            _file['test'].create_dataset('path', self._data.shape,
                                         chunks=(1, 5, 5, 10), dtype='f8')
            _file['test/path'][:] = self._data

    def tearDown(self):
        shutil.rmtree(self._path)

    def test_get_selection_None(self):
        _size = 14
        _entry = None
        _val = get_selection(_entry, _size)
        self.assertEqual(_val, (0, _size))

    def test_get_selection_list_len1(self):
        _size = 14
        _entry = [2]
        _val = get_selection(_entry, _size)
        self.assertEqual(_val, (2, 3))

    def test_get_selection_tuple_len1(self):
        _size = 14
        _entry = (2)
        _val = get_selection(_entry, _size)
        self.assertEqual(_val, (2, 3))

    def test_get_selection_list_len2(self):
        _size = 14
        _entry = [2, 7]
        _val = get_selection(_entry, _size)
        self.assertEqual(_val, tuple(_entry))

    def test_get_selection_tuple_len2(self):
        _size = 14
        _entry = (2, 7)
        _val = get_selection(_entry, _size)
        self.assertEqual(_val, _entry)

    def test_get_selection_int(self):
        _size = 14
        _entry = 3
        _val = get_selection(_entry, _size)
        self.assertEqual(_val, (_entry, _entry + 1))

    def test_get_selection_float(self):
        _size = 14
        _entry = 3.0
        with self.assertRaises(ValueError):
            get_selection(_entry, _size)

    def test_read_all(self):
        data = read_hdf5_slice(self._fname, 'test/path', [])
        self.assertEqual(data.shape, self._data.shape)
        self.assertTrue((data == self._data).all())

    def test_read_some(self):
        data = read_hdf5_slice(self._fname, 'test/path', [None, [1, 8], 5])
        self.assertEqual(data.shape, (10, 7, 1, 10))
        self.assertTrue((data == self._data[:, 1:8, 5:6, :]).all())


if __name__ == "__main__":
    unittest.main()
