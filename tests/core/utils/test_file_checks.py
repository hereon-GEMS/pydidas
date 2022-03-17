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
import shutil
import os

import numpy as np
import h5py

from pydidas.core import AppConfigError
from pydidas.core.utils.file_checks import (
    check_hdf5_key_exists_in_file, check_file_exists, file_is_writable,
    verify_files_in_same_directory, verify_files_of_range_are_same_size)


class TestFileCheckFunctions(unittest.TestCase):

    def setUp(self):
        self._path = tempfile.mkdtemp()
        self._no_fname = os.path.join(self._path, 'test.npy')
        self._hdf5_fname = os.path.join(self._path, 'test01.h5')
        with h5py.File(self._hdf5_fname, 'w') as _file:
            _file['test/path/data'] = [1, 2, 3, 4, 5]

    def tearDown(self):
        shutil.rmtree(self._path)

    def test_check_hdf5_key_exists_in_file(self):
        check_hdf5_key_exists_in_file(self._hdf5_fname, 'test/path/data')

    def test_check_hdf5_key_exists_in_file_group_not_dset(self):
        with self.assertRaises(AppConfigError):
            check_hdf5_key_exists_in_file(self._hdf5_fname, 'test/path')

    def test_check_hdf5_key_exists_in_file_wrong_key(self):
        with self.assertRaises(AppConfigError):
            check_hdf5_key_exists_in_file(self._hdf5_fname, 'no/dataset')

    def test_check_file_exists(self):
        check_file_exists(self._hdf5_fname)

    def test_check_file_exists_dir(self):
        with self.assertRaises(AppConfigError):
            check_file_exists(self._path)

    def test_check_file_exists_nofile(self):
        with self.assertRaises(AppConfigError):
            check_file_exists(self._no_fname)

    def test_verify_files_in_same_directory_simple(self):
        verify_files_in_same_directory(self._no_fname, self._hdf5_fname)

    def test_verify_files_in_same_directory_2nd_fname_only(self):
        verify_files_in_same_directory(self._no_fname, 'test.txt')

    def test_verify_files_in_same_directory_not_true(self):
        with self.assertRaises(AppConfigError):
            verify_files_in_same_directory(self._no_fname, 'some/thing.txt')

    def test_verify_files_of_range_are_same_size_correct(self):
        _data = np.random.random((10, 10))
        _fnames = [ f'test{i:02d}.npy' for i in range(10)]
        for _name in _fnames:
            np.save(os.path.join(self._path, _name), _data)
        verify_files_of_range_are_same_size(self._path, _fnames)

    def test_verify_files_of_range_are_same_size_wrong(self):
        _data = np.random.random((10, 10))
        _fnames = [ f'test{i:02d}.npy' for i in range(10)]
        for i, _name in enumerate(_fnames):
            np.save(os.path.join(self._path, _name), _data[:i, :i])
        with self.assertRaises(AppConfigError):
            verify_files_of_range_are_same_size(self._path, _fnames)

    def test_file_is_writable_simple(self):
        self.assertFalse(file_is_writable(self._hdf5_fname))

    def test_file_is_writable_overwrite(self):
        self.assertTrue(file_is_writable(self._hdf5_fname, True))

    def test_file_is_writable_w_writable_dir(self):
        self.assertTrue(file_is_writable(self._no_fname))

    def test_file_is_writable_w_dir(self):
        self.assertTrue(file_is_writable(self._path))


if __name__ == "__main__":
    unittest.main()
