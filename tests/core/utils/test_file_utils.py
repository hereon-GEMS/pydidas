# This file is part of pydidas.
#
# Copyright 2023, Helmholtz-Zentrum Hereon
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
__copyright__ = "Copyright 2023, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"


import copy
import os
import random
import shutil
import sys
import tempfile
import unittest
from collections.abc import Iterable
from pathlib import Path

from pydidas.core import UserConfigError
from pydidas.core.utils import (
    find_valid_python_files,
    flatten,
    get_extension,
    get_file_naming_scheme,
    get_random_string,
)


class Test_file_utils(unittest.TestCase):
    def setUp(self):
        self._path = Path(tempfile.mkdtemp())
        self._good_filenames = ["test.py", "test_2.py", "test3.py"]
        self._bad_filenames = [
            ".test.py",
            "__test.py",
            "test.txt",
            "another_test.pyc",
            "compiled.py~",
        ]
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
            _dir = path.joinpath(get_random_string(8))
            os.makedirs(_dir)
            with open(_dir.joinpath("__init__.py"), "w") as f:
                f.write(" ")
            if depth > 1:
                _dirs += self.create_dir_tree(_dir, width=width, depth=depth - 1)
            else:
                _dirs += [_dir]
        return _dirs

    def populate_with_python_files(self, dirs):
        self._class_names = []
        if not isinstance(dirs, Iterable):
            dirs = [dirs]
        for _dir in dirs:
            for _name in self._good_filenames:
                with open(_dir.joinpath(_name), "w") as f:
                    f.write(self.get_random_class_def(store_name=True))
            for _name in self._bad_filenames:
                with open(_dir.joinpath(_name), "w") as f:
                    f.write(self.get_random_class_def())

    def get_random_class_def(self, store_name=False):
        _plugin = random.choice(["InputPlugin", "ProcPlugin", "OutputPlugin"])
        _name = get_random_string(11)
        _str = (
            "from pydidas.plugins import InputPlugin, ProcPlugin, "
            f"OutputPlugin\n\nclass {_name.upper()}({_plugin}):"
            "\n    basic_plugin = False"
            f'\n    plugin_name = "{_name}"'
            "\n\n    def __init__(self, **kwargs: dict):"
            "\n        super().__init__(**kwargs)"
            f"\n\nclass {get_random_string(11)}:"
            "\n    ..."
        )
        if store_name:
            self._class_names.append(_name.upper())
        return _str

    def test_find_valid_python_files__no_path(self):
        _files = find_valid_python_files(self._path)
        self.assertEqual(_files, [])

    def test_find_valid_python_files__simple_path(self):
        self.populate_with_python_files(self._path)
        _files = set(find_valid_python_files(self._path))
        _target = set(
            [Path(os.path.join(self._path, _file)) for _file in self._good_filenames]
        )
        self.assertEqual(_files, _target)

    def test_find_valid_python_files__path_tree(self):
        _dirs = self.create_python_file_tree()
        _files = set(find_valid_python_files(self._path))
        _target = set(
            flatten(
                [
                    [Path(_dir.joinpath(_file)) for _file in self._good_filenames]
                    for _dir in _dirs
                ]
            )
        )
        self.assertEqual(_files, _target)

    def test_find_valid_python_files__single_file(self):
        _path = self._path.joinpath(self._good_filenames[0])
        with open(_path, "w") as _f:
            _f.write(self.get_random_class_def())
        _files = find_valid_python_files(_path)
        self.assertEqual(_files, [_path])

    def test_find_valid_python_files__bad_filename(self):
        for _name in self._bad_filenames:
            _path = self._path.joinpath(_name)
            with open(_path, "w") as _f:
                _f.write(self.get_random_class_def())
            _files = find_valid_python_files(_path)
            self.assertEqual(_files, [])

    def test_get_extension__empty_path(self):
        _ext = get_extension("")
        self.assertEqual(_ext, "")

    def test_get_extension__no_file_extension(self):
        _ext = get_extension("test/to/some/dir")
        self.assertEqual(_ext, "")

    def test_get_extension__generic(self):
        _input_ext = "extension"
        _ext = get_extension(f"test/to/some/dir/file.{_input_ext}")
        self.assertEqual(_ext, _input_ext)

    def test_get_file_naming_scheme(self):
        _index0 = 0
        _index1 = 7
        _file1 = f"/foo/path/test_0000_file_{_index0:03d}.txt"
        _file2 = f"/foo/path/test_0000_file_{_index1:03d}.txt"
        _fnames, _range = get_file_naming_scheme(_file1, _file2)
        self.assertEqual(_range[0], _index0)
        self.assertEqual(_range[-1], _index1)
        self.assertEqual(_fnames.format(index=0).replace("\\", "/"), _file1)

    def test_get_file_naming_scheme__wrong_ext(self):
        _index0 = 0
        _index1 = 7
        _file1 = f"/foo/path/test_0000_file_{_index0:03d}.txt"
        _file2 = f"/foo/path/test_0000_file_{_index1:03d}.text"
        with self.assertRaises(UserConfigError):
            _fnames, _range = get_file_naming_scheme(_file1, _file2)

    def test_get_file_naming_scheme__wrong_length(self):
        _index0 = 0
        _index1 = 7
        _file1 = f"/foo/path/test_0000_file_{_index0:03d}.txt"
        _file2 = f"/foo/path/test_0000_file_{_index1:03d}_test.txt"
        with self.assertRaises(UserConfigError):
            _fnames, _range = get_file_naming_scheme(_file1, _file2)

    def test_get_file_naming_scheme__wrong_length_ii(self):
        _index0 = 0
        _index1 = 7
        _file1 = f"/foo/path/test_0000_file_{_index0:03d}.txt"
        _file2 = f"/foo/path/test_0000_file_{_index1:05d}.txt"
        with self.assertRaises(UserConfigError):
            _fnames, _range = get_file_naming_scheme(_file1, _file2)

    def test_get_file_naming_scheme__wrong_number_length_with_ignore(self):
        _index0 = 0
        _index1 = 7
        _file1 = f"/foo/path/test_0000_file_{_index0:d}.txt"
        _file2 = f"/foo/path/test_0000_file_{_index1:03d}.txt"
        _fnames, _range = get_file_naming_scheme(
            _file1, _file2, ignore_leading_zeros=True
        )
        self.assertEqual(_fnames.format(index=0).replace("\\", "/"), _file1)

    def test_get_file_naming_scheme__wrong_number_length(self):
        _index0 = 0
        _index1 = 7
        _file1 = f"/foo/path/test_0000_file_{_index0:d}.txt"
        _file2 = f"/foo/path/test_0000_file_{_index1:03d}_test.txt"
        with self.assertRaises(UserConfigError):
            _fnames, _range = get_file_naming_scheme(_file1, _file2)

    def test_get_file_naming_scheme__too_many_changes(self):
        _index0 = 0
        _index1 = 7
        _file1 = f"/foo/path/test_0000_file_{_index0:03d}.txt"
        _file2 = f"/foo/path/test_0001_file_{_index1:03d}.txt"
        with self.assertRaises(UserConfigError):
            _fnames, _range = get_file_naming_scheme(_file1, _file2)


if __name__ == "__main__":
    unittest.main()
