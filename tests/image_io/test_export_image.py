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
__copyright__ = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.0.1"
__maintainer__ = "Malte Storm"
__status__ = "Development"


import os
import unittest
import tempfile
import shutil

import numpy as np

from pydidas.image_io import export_image
from pydidas.image_io import ImageReaderCollection


ImageReader = ImageReaderCollection()


class TestExportImage(unittest.TestCase):

    def setUp(self):
        self._path = tempfile.mkdtemp()
        self._array = np.random.random((30, 30))

    def tearDown(self):
        shutil.rmtree(self._path)
        del self._path

    def test_npy_export(self):
        _name = f'{self._path}/test.npy'
        export_image(self._array, _name)
        self.assertTrue(os.path.isfile(_name))

    def test_hdf5_export(self):
        _name = f'{self._path}/test.h5'
        export_image(self._array, _name)
        self.assertTrue(os.path.isfile(_name))

    def test_binary_export(self):
        _name = f'{self._path}/test.bin'
        export_image(self._array, _name)
        self.assertTrue(os.path.isfile(_name))

    def test_tiff_export(self):
        _name = f'{self._path}/test.tif'
        export_image(self._array, _name)
        self.assertTrue(os.path.isfile(_name))

    def test_png_export(self):
        _name = f'{self._path}/test.png'
        export_image(self._array, _name)
        self.assertTrue(os.path.isfile(_name))


if __name__ == "__main__":
    unittest.main()
