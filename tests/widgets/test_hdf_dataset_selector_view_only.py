# This file is part of pydidas.

# pydidas is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# Foobar is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with Foobar.  If not, see <http://www.gnu.org/licenses/>.

"""Unit tests for pydidas modules."""

__author__      = "Malte Storm"
__copyright__   = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.0.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"

import unittest
import string
import random
import os

import numpy as np
from PyQt5 import QtWidgets, QtCore

from pydidas._exceptions import WidgetLayoutError
from pydidas.widgets.hdf5_dataset_selector import Hdf5DatasetSelector


class TestHdfDatasetSelector(unittest.TestCase):

    def setUp(self):
        self.q_app = QtWidgets.QApplication([])
        self.widgets = []

    def tearDown(self):
        del self.q_app

    def test_init(self):
        obj = Hdf5DatasetSelector()
        self.assertIsInstance(obj, Hdf5DatasetSelector)

    # def test_sizeHint(self):
    #     obj = Hdf5DatasetSelector()
    #     self.assertIsInstance(obj.sizeHint(), QtCore.QSize)

    # def test__expand_to_path(self):
    #     _path = os.path.dirname(__file__)
    #     obj = Hdf5DatasetSelector()
    #     obj._Hdf5DatasetSelector__expand_to_path(_path)
    #     while os.path.isdir(_path):
    #         _index = obj._filemodel.index(_path)
    #         self.assertTrue(obj.isExpanded(_index))
    #         if _path == os.path.dirname(_path):
    #             break
    #         _path = os.path.dirname(_path)


if __name__ == "__main__":
    unittest.main()
