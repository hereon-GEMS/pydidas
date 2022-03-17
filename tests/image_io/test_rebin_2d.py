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

import numpy as np

from pydidas.core import Dataset
from pydidas.image_io import rebin2d, rebin


class TestRebin2d(unittest.TestCase):

    def setUp(self):
        self._shape = np.array((10, 5, 20, 8, 3))
        self._data = np.random.random(self._shape)
        self._2dshape = np.array((37, 15))
        self._2dimage = np.random.random(self._2dshape)

    def tearDown(self):
        ...

    def test_rebin2d__with_Dataset(self):
        ori = Dataset((np.random.random(self._2dshape )))
        img = rebin2d(ori, 2)
        _shape = np.array(img.shape)
        self.assertTrue((_shape  == self._2dshape // 2).all())

    def test_2d_bin1(self):
        img = rebin2d(self._2dimage, 1)
        self.assertTrue((img == self._2dimage).all())

    def test_2d_bin2(self):
        img = rebin2d(self._2dimage, 2)
        _shape = np.array(img.shape)
        self.assertTrue((_shape  == self._2dshape // 2).all())

    def test_2d_bin3(self):
        img = rebin2d(self._2dimage, 3)
        _shape = np.array(img.shape)
        self.assertTrue((_shape  == self._2dshape // 3).all())

    def test_bin1(self):
        data = rebin(self._data, 1)
        self.assertTrue((data == self._data).all())

    def test_bin2(self):
        data = rebin(self._data, 2)
        _shape = np.array(data.shape)
        self.assertTrue((_shape  == self._shape // 2).all())

    def test_bin3(self):
        data = rebin(self._data, 3)
        _shape = np.array(data.shape)
        self.assertTrue((_shape  == self._shape // 3).all())

    def test_bin7(self):
        data = rebin(self._data, 7)
        _shape = np.array(data.shape)
        _target = np.array([max(s // 7, 1) for s in self._shape])
        self.assertTrue((_shape  == _target).all())


if __name__ == "__main__":
    unittest.main()
