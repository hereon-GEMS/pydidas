"""
Unittests for the CompositeImage class from the pydidas.core module.
"""

import os
import unittest
import tempfile
import shutil

import numpy as np
from PyQt5 import QtCore

from pydidas.core import Parameter, get_generic_parameter
from pydidas._exceptions import AppConfigError

class TestGetGenericParameter(unittest.TestCase):

    def setUp(self):
        ...

    def tearDown(self):
        ...

    def test_get_param(self):
        _p = get_generic_parameter('first_file')
        self.assertIsInstance(_p, Parameter)

    def test_get_param_wrong_key(self):
        with self.assertRaises(KeyError):
            get_generic_parameter('there_should_be_no_such_key')

if __name__ == "__main__":
    unittest.main()
