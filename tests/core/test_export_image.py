"""
Unittests for the CompositeImage class from the pydidas.core module.
"""

import os
import unittest
import tempfile
import shutil

import numpy as np
from PyQt5 import QtCore

from pydidas.core.export_image_func import export_image
from pydidas._exceptions import AppConfigError

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
