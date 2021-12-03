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

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.0.1"
__maintainer__ = "Malte Storm"
__status__ = "Development"

import unittest

import numpy as np
np.core.multiarray._reconstruct
from pydidas.image_io import ImageReader


class TestImageReader(unittest.TestCase):

    def setUp(self):
        self._target_roi = (slice(0, 5, None), slice(0, 5, None))

    def tearDown(self):
        ...

    def test_creation(self):
        obj = ImageReader()
        self.assertIsInstance(obj, ImageReader)

    def test_read_image(self):
        obj = ImageReader()
        with self.assertRaises(NotImplementedError):
            obj.read_image('test')

    def test_return_image_no_image(self):
        obj = ImageReader()
        with self.assertRaises(ValueError):
            obj.return_image()

    def test_return_image_plain(self):
        obj = ImageReader()
        obj._image = np.random.random((10, 10))
        _image = obj.return_image()
        self.assertTrue((obj._image == _image).all())

    def test_return_image_w_roi(self):
        _roi = [2, 8, 2, 8]
        obj = ImageReader()
        obj._image = np.random.random((10, 10))
        _cropped_image = obj._image[_roi[0]:_roi[1], _roi[2]:_roi[3]]
        _image = obj.return_image(roi=_roi)
        self.assertTrue((_cropped_image == _image).all())

    def test_return_image_w_return_type(self):
        obj = ImageReader()
        obj._image = np.random.random((10, 10))
        _image = obj.return_image(datatype=np.float32)
        self.assertEqual(_image.dtype, np.float32)

    def test_return_image_w_binning(self):
        obj = ImageReader()
        obj._image = np.random.random((10, 10))
        _image = obj.return_image(binning=2)
        self.assertEqual(_image.shape, (5, 5))

if __name__ == "__main__":
    unittest.main()
