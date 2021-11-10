
import unittest
import copy
import numpy as np

from pydidas.image_io import rebin2d, rebin
from pydidas.core import Dataset


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
