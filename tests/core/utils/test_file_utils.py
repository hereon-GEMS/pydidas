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
import random
import tempfile
import shutil
import os
import copy
import sys

from pydidas.core.utils import (find_valid_python_files, flatten_list,
                                get_random_string)


class TestPluginCollection(unittest.TestCase):

    def setUp(self):
        self._path = tempfile.mkdtemp()
        self._good_filenames = ['test.py', 'test_2.py', 'test3.py']
        self._bad_filenames = ['.test.py', '__test.py', 'test.txt',
                               'another_test.pyc', 'compiled.py~']
        self._syspath = copy.copy(sys.path)

    def tearDown(self):
        shutil.rmtree(self._path)
        sys.path = self._syspath

    def create_python_file_tree(self, path=None, depth=3, width=2):
        path = self._path if path is None else path
        _dirs = self.create_dir_tree(path, depth, width)
        self.populate_with_python_files(_dirs)
        return _dirs

    def create_dir_tree(self, path=None, depth=3, width=2):
        _dirs = []
        for _width in range(width):
            _dir = os.path.join(path, get_random_string(8))
            os.makedirs(_dir)
            with open(os.path.join(_dir, '__init__.py'), 'w') as f:
                f.write(' ')
            if depth > 1:
                _dirs += self.create_dir_tree(_dir, width=width, depth=depth-1)
            else:
                _dirs += [_dir]
        return _dirs

    def populate_with_python_files(self, dirs):
        self._class_names = []
        if isinstance(dirs, str):
            dirs = [dirs]
        for _dir in dirs:
            for _name in self._good_filenames:
                with open(os.path.join(_dir, _name), 'w') as f:
                    f.write(self.get_random_class_def(store_name=True))
            for _name in self._bad_filenames:
                with open(os.path.join(_dir, _name), 'w') as f:
                    f.write(self.get_random_class_def())

    def get_random_class_def(self, store_name=False):
        _plugin = random.choice(['InputPlugin', 'ProcPlugin', 'OutputPlugin'])
        _name = get_random_string(11)
        _str = ('from pydidas.plugins import InputPlugin, ProcPlugin, '
                f'OutputPlugin\n\nclass {_name.upper()}({_plugin}):'
                '\n    basic_plugin = False'
                f'\n    plugin_name = "{_name}"'
                '\n\n    def __init__(self, **kwargs):'
                '\n        super().__init__(**kwargs)'
                f'\n\nclass {get_random_string(11)}:'
                '\n    ...')
        if store_name:
            self._class_names.append(_name.upper())
        return _str

    def test_find_files__no_path(self):
        _files = find_valid_python_files(self._path)
        self.assertEqual(_files, [])

    def test_find_files__simple_path(self):
        self.populate_with_python_files(self._path)
        _files = set(find_valid_python_files(self._path))
        _target = set([os.path.join(self._path, _file)
                        for _file in self._good_filenames])
        self.assertEqual(_files, _target)

    def test_find_files__path_tree(self):
        _dirs = self.create_python_file_tree()
        _files = set(find_valid_python_files(self._path))
        _target = set(flatten_list(
            [[os.path.join(_dir, _file)
              for _file in self._good_filenames] for _dir in _dirs]))
        self.assertEqual(_files, _target)


if __name__ == "__main__":
    unittest.main()
