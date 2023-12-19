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


import shutil
import tempfile
import unittest
from pathlib import Path

import numpy as np

from pydidas.core import FileReadError
from pydidas.core.constants import NUMPY_EXTENSIONS
from pydidas.data_io.implementations.numpy_io import NumpyIo


class TestNumpyIo(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._path = Path(tempfile.mkdtemp())
        cls._fname = cls._path.joinpath("test.npy")
        cls._data_shape = (12, 13, 14, 15)
        cls._data = np.random.random(cls._data_shape)
        np.save(cls._fname, cls._data)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls._path)

    def setUp(self):
        self._target_roi = (slice(0, 5, None), slice(0, 5, None))

    def tearDown(self):
        ...

    def test_class_extensions(self):
        for _ext in NUMPY_EXTENSIONS:
            self.assertIn(_ext, NumpyIo.extensions_export)
            self.assertIn(_ext, NumpyIo.extensions_import)

    def test_import_from_file__default(self):
        _data = NumpyIo.import_from_file(self._fname)
        self.assertTrue(np.allclose(_data, self._data))

    def test_import_from_file__wrong_name(self):
        with self.assertRaises(FileReadError):
            NumpyIo.import_from_file(self._fname.joinpath("dummy"), datatype=np.float64)

    def test_import_from_file__wrong_type(self):
        _fname_new = self._path.joinpath("test2.dat")
        with open(_fname_new, "w") as f:
            f.write("now it's just an ASCII text file.")
        with self.assertRaises(FileReadError):
            NumpyIo.import_from_file(_fname_new, datatype=np.float64)

    def test_export_to_file__file_exists(self):
        with self.assertRaises(FileExistsError):
            NumpyIo.export_to_file(self._fname, self._data)

    def test_export_to_file__file_exists_and_overwrite(self):
        _fname = self._path.joinpath("test_new.npy")
        NumpyIo.export_to_file(_fname, self._data)
        NumpyIo.export_to_file(_fname, self._data[:11], overwrite=True)
        _data = NumpyIo.import_from_file(_fname)
        self.assertEqual(_data.shape, (11,) + self._data_shape[1:])

    def test_export_to_file__simple(self):
        _fname = self._path.joinpath("test_fname.npy")
        NumpyIo.export_to_file(_fname, self._data)
        _data = NumpyIo.import_from_file(_fname)
        self.assertTrue(np.allclose(_data, self._data))


if __name__ == "__main__":
    unittest.main()
