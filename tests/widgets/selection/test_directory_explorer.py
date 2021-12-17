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
__copyright__ = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.0.1"
__maintainer__ = "Malte Storm"
__status__ = "Development"

import unittest
import os

from PyQt5 import QtWidgets, QtCore

from pydidas.widgets.selection import DirectoryExplorer


# class TestDirectoryExplorer(unittest.TestCase):

#     def setUp(self):
#         self.q_app = QtWidgets.QApplication([])
#         self.widgets = []

#     def tearDown(self):
#         del self.q_app

#     def test_init(self):
#         obj = DirectoryExplorer()
#         self.assertIsInstance(obj, DirectoryExplorer)

#     def test_sizeHint(self):
#         obj = DirectoryExplorer()
#         self.assertIsInstance(obj.sizeHint(), QtCore.QSize)

#     def test_expand_to_path(self):
#         _path = os.path.dirname(__file__)
#         obj = DirectoryExplorer()
#         obj._DirectoryExplorer__expand_to_path(_path)
#         while os.path.isdir(_path):
#             print(_path)
#             _index = obj._filemodel.index(_path)
#             self.assertTrue(obj.isExpanded(_index))
#             if _path == os.path.dirname(_path):
#                 break
#             _path = os.path.dirname(_path)


# if __name__ == "__main__":
#     unittest.main()
