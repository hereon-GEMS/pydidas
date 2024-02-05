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


import shutil
import tempfile
import unittest
from pathlib import Path

import numpy as np
import skimage.io

from pydidas.core import FileReadError
from pydidas.core.constants import TIFF_EXTENSIONS
from pydidas.data_io.implementations.tiff_io import TiffIo


class TestTiffIo(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._path = Path(tempfile.mkdtemp())
        cls._fname = cls._path.joinpath("test.tif")
        cls._data_shape = (12, 13)
        cls._data = np.random.random(cls._data_shape)
        cls._index = 0
        skimage.io.imsave(cls._fname, cls._data)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls._path)

    @classmethod
    def get_fname(cls):
        cls._index += 1
        return f"test_name{cls._index:03d}.tif"

    def setUp(self):
        self._target_roi = (slice(0, 5, None), slice(0, 5, None))

    def tearDown(self): ...

    def test_class_extensions(self):
        for _ext in TIFF_EXTENSIONS:
            self.assertIn(_ext, TiffIo.extensions_export)
            self.assertIn(_ext, TiffIo.extensions_import)

    def test_import_from_file__default(self):
        _data = TiffIo.import_from_file(self._fname)
        self.assertTrue(np.allclose(_data, self._data))

    def test_import_from_file__wrong_name(self):
        with self.assertRaises(FileReadError):
            TiffIo.import_from_file(self._fname.joinpath("dummy"))

    def test_import_from_file__wrong_type(self):
        with open(self._fname, "w") as f:
            f.write("now it's just an ASCII text file.")
        with self.assertRaises(FileReadError):
            TiffIo.import_from_file(self._fname)

    def test_export_to_file__file_exists(self):
        with self.assertRaises(FileExistsError):
            TiffIo.export_to_file(self._fname, self._data)

    def test_export_to_file__file_exists_and_overwrite(self):
        _fname = self._path.joinpath(self.get_fname())
        TiffIo.export_to_file(_fname, self._data)
        TiffIo.export_to_file(_fname, self._data[:11], overwrite=True)
        _data = TiffIo.import_from_file(_fname)
        self.assertEqual(_data.shape, (11,) + self._data_shape[1:])

    def test_export_to_file__simple(self):
        _fname = self._path.joinpath(self.get_fname())
        TiffIo.export_to_file(_fname, self._data)
        _data = TiffIo.import_from_file(_fname)
        self.assertTrue(np.allclose(_data, self._data))

    def test_export_to_file__8bit_int(self):
        _fname = self._path.joinpath(self.get_fname())
        _raw = (np.random.random((11, 12, 13)) * 125).astype(np.int8)
        TiffIo.export_to_file(_fname, _raw)
        _data = TiffIo.import_from_file(_fname)
        self.assertTrue(np.allclose(_data, _raw))
        self.assertEqual(_raw.dtype, _data.dtype)

    def test_export_to_file__8bit_uint(self):
        _fname = self._path.joinpath(self.get_fname())
        _raw = (np.random.random((11, 12, 13)) * 125).astype(np.uint8)
        TiffIo.export_to_file(_fname, _raw)
        _data = TiffIo.import_from_file(_fname)
        self.assertTrue(np.allclose(_data, _raw))
        self.assertEqual(_raw.dtype, _data.dtype)

    def test_export_to_file__16bit_int(self):
        _fname = self._path.joinpath(self.get_fname())
        _raw = (np.random.random((11, 12, 13)) * 1257).astype(np.int16)
        TiffIo.export_to_file(_fname, _raw)
        _data = TiffIo.import_from_file(_fname)
        self.assertTrue(np.allclose(_data, _raw))
        self.assertEqual(_raw.dtype, _data.dtype)

    def test_export_to_file__16bit_uint(self):
        _fname = self._path.joinpath(self.get_fname())
        _raw = (np.random.random((11, 12, 13)) * 1257).astype(np.uint16)
        TiffIo.export_to_file(_fname, _raw)
        _data = TiffIo.import_from_file(_fname)
        self.assertTrue(np.allclose(_data, _raw))
        self.assertEqual(_raw.dtype, _data.dtype)

    def test_export_to_file__32bit_int(self):
        _fname = self._path.joinpath(self.get_fname())
        _raw = (np.random.random((11, 12, 13)) * 12573).astype(np.int32)
        TiffIo.export_to_file(_fname, _raw)
        _data = TiffIo.import_from_file(_fname)
        self.assertTrue(np.allclose(_data, _raw))
        self.assertEqual(_raw.dtype, _data.dtype)

    def test_export_to_file__32bit_uint(self):
        _fname = self._path.joinpath(self.get_fname())
        _raw = (np.random.random((11, 12, 13)) * 12573).astype(np.uint32)
        TiffIo.export_to_file(_fname, _raw)
        _data = TiffIo.import_from_file(_fname)
        self.assertTrue(np.allclose(_data, _raw))
        self.assertEqual(_raw.dtype, _data.dtype)

    def test_export_to_file__16bit_float(self):
        _fname = self._path.joinpath(self.get_fname())
        _raw = (np.random.random((11, 12, 13))).astype(np.float16)
        TiffIo.export_to_file(_fname, _raw)
        _data = TiffIo.import_from_file(_fname)
        self.assertTrue(np.allclose(_data, _raw))
        self.assertEqual(_raw.dtype, _data.dtype)

    def test_export_to_file__32bit_float(self):
        _fname = self._path.joinpath(self.get_fname())
        _raw = (np.random.random((11, 12, 13))).astype(np.float32)
        TiffIo.export_to_file(_fname, _raw)
        _data = TiffIo.import_from_file(_fname)
        self.assertTrue(np.allclose(_data, _raw))
        self.assertEqual(_raw.dtype, _data.dtype)

    def test_export_to_file__64bit_float(self):
        _fname = self._path.joinpath(self.get_fname())
        _raw = (np.random.random((11, 12, 13))).astype(np.float64)
        TiffIo.export_to_file(_fname, _raw)
        _data = TiffIo.import_from_file(_fname)
        self.assertTrue(np.allclose(_data, _raw))
        self.assertEqual(_data.dtype, np.float32)

    def test_export_to_file__1282bit_float(self):
        _fname = self._path.joinpath(self.get_fname())
        _raw = (np.random.random((11, 12, 13))).astype(np.longfloat)
        TiffIo.export_to_file(_fname, _raw)
        _data = TiffIo.import_from_file(_fname)
        self.assertTrue(np.allclose(_data, _raw))
        self.assertEqual(_data.dtype, np.float32)


if __name__ == "__main__":
    unittest.main()
