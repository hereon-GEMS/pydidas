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


import unittest

import numpy as np

from pydidas.core import Dataset
from pydidas.core.utils import rebin, rebin2d


class TestRebin(unittest.TestCase):
    def setUp(self):
        self._shape = np.array((10, 5, 20, 8, 3))
        self._data = np.random.random(self._shape)
        self._2dshape = np.array((37, 15))
        self._2dimage = np.random.random(self._2dshape)

    def tearDown(self):
        ...

    def test_rebin2d__with_Dataset(self):
        ori = Dataset(np.random.random(self._2dshape))
        img = rebin2d(ori, 2)
        _shape = np.array(img.shape)
        self.assertTrue((_shape == self._2dshape // 2).all())

    def test_2d_bin1(self):
        img = rebin2d(self._2dimage, 1)
        self.assertTrue((img == self._2dimage).all())

    def test_2d_bin2(self):
        img = rebin2d(self._2dimage, 2)
        _shape = np.array(img.shape)
        self.assertTrue((_shape == self._2dshape // 2).all())

    def test_2d_bin3(self):
        img = rebin2d(self._2dimage, 3)
        _shape = np.array(img.shape)
        self.assertTrue((_shape == self._2dshape // 3).all())

    def test_bin1(self):
        data = rebin(self._data, 1)
        self.assertTrue((data == self._data).all())

    def test_bin2(self):
        data = rebin(self._data, 2)
        _shape = np.array(data.shape)
        self.assertTrue((_shape == self._shape // 2).all())

    def test_bin3(self):
        data = rebin(self._data, 3)
        _shape = np.array(data.shape)
        self.assertTrue((_shape == self._shape // 3).all())

    def test_bin7(self):
        data = rebin(self._data, 7)
        _shape = np.array(data.shape)
        _target = np.array([max(s // 7, 1) for s in self._shape])
        self.assertTrue((_shape == _target).all())

    def test_rebin__2d_data_bin1(self):
        data = rebin(self._2dimage, 1)
        self.assertTrue((data == self._2dimage).all())

    def test_rebin_2d_data_bin2(self):
        data = rebin(self._2dimage, 2)
        _shape = np.array(data.shape)
        self.assertTrue((_shape == self._2dshape // 2).all())

    def test_rebin_2d_data_bin3(self):
        data = rebin(self._2dimage, 3)
        _shape = np.array(data.shape)
        self.assertTrue((_shape == self._2dshape // 3).all())

    def test_compare_rebin2d_and_rebin(self):
        data = rebin(self._2dimage, 3)
        img = rebin2d(self._2dimage, 3)
        self.assertTrue(np.allclose(data, img))


if __name__ == "__main__":
    unittest.main()
