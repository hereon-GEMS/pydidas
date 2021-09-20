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

__author__      = "Malte Storm"
__copyright__   = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.0.1"
__maintainer__ = "Malte Storm"
__status__ = "Development"

import unittest
from pathlib import Path

from pydidas.core import HdfKey


class TestHdfKey(unittest.TestCase):

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
