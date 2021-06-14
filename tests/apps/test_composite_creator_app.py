

import os
import unittest
from pathlib import Path

import numpy as np

import pydidas
from pydidas.apps import CompositeCreatorApp
from pydidas.core import Parameter


class TestCompositeCreatorApp(unittest.TestCase):

    def setUp(self):
        self._path = 'E:\\p03data\\calib_lab6_00001'


    def tearDown(self):
        del self._path

    def testCreation(self):
        app = CompositeCreatorApp()
        self.assertIsInstance(app, CompositeCreatorApp)

    # def test_readImg_tif(self):
    #     with self.assertRaises(OSError):
    #         a = impro.readImg(f"{self.p}/foo.bar")


    # def test_readImg_tif(self):
    #     a = impro.readImg(f"{self.p}/impro_test.tif")
    #     self.assertIsInstance(a, np.ndarray)


    # def test_readImg_npy(self):
    #     a = impro.readImg(f"{self.p}/impro_test.npy")
    #     self.assertIsInstance(a, np.ndarray)


    # def test_readImg_hdf1(self):
    #     a = impro.readImg(f"{self.p}/nx_test.nxs", imageNo=0,
    #                       hdfDatapath='entry1/test2/dset4')
    #     self.assertIsInstance(a, np.ndarray)


    # def test_readImg_hdf2(self):
    #     a = impro.readImg(f"{self.p}/nx_test.nxs", imageNo=3,
    #                       hdfDatapath='entry1/test3/dset5', sinoKW=True)
    #     self.assertIsInstance(a, np.ndarray)


    # def test_readImg_raw(self):
    #     a = impro.readImg(f"{self.p}/impro_test.raw", NpxX=40, NpxY=40)
    #     self.assertIsInstance(a, np.ndarray)


    # def test_readImg_ROI(self):
    #     roi = (slice(5, 10), slice(5, 10))
    #     a = impro.readImg(f"{self.p}/impro_test.tif", ROI=roi)
    #     self.assertEqual(a.shape, (5,5))

if __name__ == "__main__":
    unittest.main()
