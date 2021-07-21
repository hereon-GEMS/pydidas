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
import tempfile
import shutil
import os

import h5py
import numpy as np

from pydidas.image_io import ImageReaderFactory
from pydidas.image_io.implementations.hdf5_reader import Hdf5Reader


class TestHdf5Reader(unittest.TestCase):

    def setUp(self):
        self._path = tempfile.mkdtemp()
        self._fname = os.path.join(self._path, 'test.h5')
        self._img_shape = (10, 10, 10)
        self._data = np.random.random(self._img_shape)
        with h5py.File(self._fname, 'w') as _file:
            _file['test/path'] = self._data

    def tearDown(self):
        shutil.rmtree(self._path)

    def test_get_instance(self):
        obj = ImageReaderFactory().get_reader(self._fname)
        self.assertIsInstance(obj, Hdf5Reader)

    def test_read_image_missing_dset(self):
        obj = ImageReaderFactory().get_reader(self._fname)
        with self.assertRaises(KeyError):
            obj.read_image(self._fname)

    def test_read_image_plain(self):
        obj = ImageReaderFactory().get_reader(self._fname)
        img = obj.read_image(self._fname, dataset='test/path')
        self.assertTrue((img.array == self._data[0]).all())

    def test_read_image_other_axis(self):
        obj = ImageReaderFactory().get_reader(self._fname)
        img = obj.read_image(self._fname, dataset='test/path', axis=1)
        self.assertTrue((img.array == self._data[:,0]).all())

    def test_read_image_other_frame(self):
        obj = ImageReaderFactory().get_reader(self._fname)
        img = obj.read_image(self._fname, dataset='test/path', frame=4)
        self.assertTrue((img.array == self._data[4]).all())

if __name__ == "__main__":
    unittest.main()
