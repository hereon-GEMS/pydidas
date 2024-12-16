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


import os
import shutil
import tempfile
import unittest

import numpy as np

from pydidas.core.constants import JPG_EXTENSIONS
from pydidas.data_io.implementations.jpeg_io import JpegIo


class TestJpegIo(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._path = tempfile.mkdtemp()
        cls._fname = os.path.join(cls._path, "test.jpg")
        cls._data_shape = (127, 137)
        cls._data = np.random.random(cls._data_shape)
        cls._index = 0

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls._path)

    @classmethod
    def get_fname(cls):
        cls._index += 1
        return f"test_name{cls._index:03d}.jpg"

    def setUp(self):
        self._target_roi = (slice(0, 5, None), slice(0, 5, None))

    def tearDown(self): ...

    def test_class_extensions(self):
        for _ext in JPG_EXTENSIONS:
            self.assertIn(_ext, JpegIo.extensions_export)

    def test_export_to_file__file_exists(self):
        JpegIo.export_to_file(self._fname, self._data)
        with self.assertRaises(FileExistsError):
            JpegIo.export_to_file(self._fname, self._data)

    def test_export_to_file__file_exists_and_overwrite(self):
        _fname = os.path.join(self._path, self.get_fname())
        JpegIo.export_to_file(_fname, self._data)
        _size = os.stat(_fname).st_size
        JpegIo.export_to_file(_fname, self._data[:57], overwrite=True)
        _size_new = os.stat(_fname).st_size
        self.assertNotEqual(_size, _size_new)

    def test_export_to_file(self):
        _fname = os.path.join(self._path, self.get_fname())
        JpegIo.export_to_file(_fname, self._data)


if __name__ == "__main__":
    unittest.main()
