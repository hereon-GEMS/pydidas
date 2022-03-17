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
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"

import unittest
import tempfile
import os
import shutil

from pydidas.core.utils import get_pydidas_module_dir


class TestGetModuleDir(unittest.TestCase):

    def setUp(self):
        self._path = get_pydidas_module_dir(__file__)
        self._dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self._dir)
    def test_get_pydidas_module_dir__empty_path(self):
        with self.assertRaises(IOError):
            get_pydidas_module_dir('')

    def test_get_pydidas_module_dir__file(self):
        _new = os.path.join(self._path, 'pydidas', '_exceptions.py')
        _p = get_pydidas_module_dir(_new)
        self.assertIsInstance(_p, str)

    def test_get_pydidas_module_dir__main_directory(self):
        _new = os.path.join(self._path, 'pydidas')
        _p = get_pydidas_module_dir(_new)
        self.assertIsInstance(_p, str)

    def test_get_pydidas_module_dir__nonexisting_subdirectory(self):
        _new = os.path.join(self._path, 'pydidas', 'test', 'path')
        _p = get_pydidas_module_dir(_new)
        self.assertIsInstance(_p, str)

    def test_get_pydidas_module_dir__top_directory(self):
        _new = os.path.join(os.path.dirname(self._path))
        _p = get_pydidas_module_dir(_new)
        self.assertIsInstance(_p, str)

    def test_get_pydidas_module_dir__current_file(self):
        _new = os.path.join(__file__)
        _p = get_pydidas_module_dir(_new)
        self.assertIsInstance(_p, str)

    def test_get_pydidas_module_dir__random_start(self):
        _new = tempfile.mkdtemp()
        with self.assertRaises(FileNotFoundError):
            get_pydidas_module_dir(_new)


if __name__ == "__main__":
    unittest.main()
