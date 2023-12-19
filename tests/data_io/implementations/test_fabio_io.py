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

import fabio
import numpy as np

from pydidas.core import FileReadError
from pydidas.data_io.implementations.fabio_io import FabioIo


class TestFabioIo(unittest.TestCase):
    def setUp(self):
        self._path = Path(tempfile.mkdtemp())
        self._fname = self._path.joinpath("test.edf")
        self._img_shape = (10, 10)
        self._data = np.random.random(self._img_shape)
        _file = fabio.edfimage.EdfImage(self._data)
        _file.write(self._fname)

    def tearDown(self):
        shutil.rmtree(self._path)

    def test_import_from_file(self):
        data = FabioIo.import_from_file(self._fname)
        self.assertTrue(np.allclose(data, self._data))

    def test_read_image__wrong_name(self):
        with self.assertRaises(FileReadError):
            FabioIo.import_from_file(self._fname.joinpath("dummy"))

    def test_read_imag__wrong_type(self):
        with open(self._fname, "w") as f:
            f.write("now it's just an ASCII text file.")
        with self.assertRaises(FileReadError):
            FabioIo.import_from_file(self._fname)


if __name__ == "__main__":
    unittest.main()
