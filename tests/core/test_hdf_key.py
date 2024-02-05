# This file is part of pydidas.
#
# Copyright 2023 - 2024, Helmholtz-Zentrum Hereon
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
__copyright__ = "Copyright 2023 - 2024, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"


import unittest
from pathlib import Path

from pydidas.core import Hdf5key


class TestHdf5key(unittest.TestCase):
    def setUp(self): ...

    def tearDown(self): ...

    def test_creation(self):
        key = Hdf5key("test")
        self.assertIsInstance(key, Hdf5key)

    def test_hdf5_filename(self):
        key = Hdf5key("test")
        self.assertIsNone(key.hdf5_filename)

    def test_hdf5_filename_setter(self):
        _path = "test_path"
        key = Hdf5key("test")
        key.hdf5_filename = _path
        self.assertEqual(key.hdf5_filename, Path(_path))

    def test_hdf5_filename_setter_wrong_type(self):
        _path = 123.4
        key = Hdf5key("test")
        with self.assertRaises(TypeError):
            key.hdf5_filename = _path


if __name__ == "__main__":
    unittest.main()
