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
import os
import shutil

import numpy as np

from pydidas.data_io.implementations.raw_io import RawIo
from pydidas.core.constants import BINARY_EXTENSIONS


class TestRawIo(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._path = tempfile.mkdtemp()
        cls._fname = os.path.join(cls._path, 'test.npy')
        cls._data_shape = (12, 13, 14)
        cls._data = np.random.random(cls._data_shape)
        cls._index = 0
        cls._read_kws = dict(datatype=np.float64, shape=cls._data_shape)
        cls._data.tofile(cls._fname)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls._path)

    @classmethod
    def get_fname(cls):
        cls._index += 1
        return f'test_name{cls._index:03d}.bin'

    def setUp(self):
        self._target_roi = (slice(0, 5, None), slice(0, 5, None))

    def tearDown(self):
        ...

    def test_class_extensions(self):
        for _ext in BINARY_EXTENSIONS:
            self.assertIn(_ext, RawIo.extensions_export)
            self.assertIn(_ext, RawIo.extensions_import)

    def test_import_from_file__default(self):
        _data = RawIo.import_from_file(self._fname, **self._read_kws)
        self.assertTrue(np.allclose(_data, self._data))

    def test_export_to_file__file_exists(self):
        with self.assertRaises(FileExistsError):
            RawIo.export_to_file(self._fname, self._data)

    def test_export_to_file__file_exists_and_overwrite(self):
        _fname = os.path.join(self._path, self.get_fname())
        RawIo.export_to_file(_fname, self._data[:11])
        RawIo.export_to_file(_fname, self._data, overwrite=True)
        _data = RawIo.import_from_file(self._fname, **self._read_kws)
        self.assertEqual(_data.shape, self._data_shape)

    def test_export_to_file__simple(self):
        _fname = os.path.join(self._path, self.get_fname())
        RawIo.export_to_file(_fname, self._data)
        _data = RawIo.import_from_file(_fname, **self._read_kws)
        self.assertTrue(np.allclose(_data, self._data))


if __name__ == "__main__":
    unittest.main()
