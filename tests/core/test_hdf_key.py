"""
Unittests for the CompositeImage class from the pydidas.core module.
"""

import os
import unittest
import tempfile
import shutil
from pathlib import Path

import numpy as np
from PyQt5 import QtCore

from pydidas.core import HdfKey
from pydidas._exceptions import AppConfigError

class TestGetGenericParameter(unittest.TestCase):

    def setUp(self):
        ...

    def tearDown(self):
        ...

    def test_creation(self):
        key = HdfKey('test')
        self.assertIsInstance(key, HdfKey)

    def test_hdf5_filename(self):
        key = HdfKey('test')
        self.assertIsNone(key.hdf5_filename)

    def test_hdf5_filename_setter(self):
        _path = 'test_path'
        key = HdfKey('test')
        key.hdf5_filename = _path
        self.assertEqual(key.hdf5_filename, Path(_path))

    def test_hdf5_filename_setter_wrong_type(self):
        _path = 123.4
        key = HdfKey('test')
        with self.assertRaises(TypeError):
            key.hdf5_filename = _path

if __name__ == "__main__":
    unittest.main()
