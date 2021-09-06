# This file is part of pydidas.

# pydidas is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# Pydidas is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with Pydidas. If not, see <http://www.gnu.org/licenses/>.

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

import numpy as np
import fabio

from pydidas.image_io import ImageReaderFactory
from pydidas.image_io.implementations.fabio_reader import FabioReader


class TestFabioReader(unittest.TestCase):

    def setUp(self):
        self._path = tempfile.mkdtemp()
        self._fname = os.path.join(self._path, 'test.edf')
        self._img_shape = (10, 10)
        self._data = np.random.random(self._img_shape)
        _file = fabio.edfimage.EdfImage(self._data)
        _file.write(self._fname)

    def tearDown(self):
        shutil.rmtree(self._path)

    def test_get_instance(self):
        obj = ImageReaderFactory().get_reader(self._fname)
        self.assertIsInstance(obj, FabioReader)

    def test_read_image(self):
        obj = ImageReaderFactory().get_reader(self._fname)
        img = obj.read_image(self._fname)
        self.assertTrue((img == self._data).all())


if __name__ == "__main__":
    unittest.main()
