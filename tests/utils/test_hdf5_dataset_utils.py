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

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.0.1"
__maintainer__ = "Malte Storm"
__status__ = "Development"

import unittest
import tempfile
import shutil
import os
from pathlib import Path

import h5py
import numpy as np

from pydidas.utils.hdf5_dataset_utils import (
    _get_hdf5_file_and_dataset_names, get_hdf5_metadata,
    hdf5_dataset_check, get_hdf5_populated_dataset_keys)


class Test_file_checks(unittest.TestCase):

    def setUp(self):
        self._path = tempfile.mkdtemp()
        self._fname = lambda s: os.path.join(self._path, f'test{s}.h5')
        self._ref = f'{self._fname(1)}:///test/path/data'
        self._data = np.random.random((10, 10, 10, 10))
        self._fulldsets = ['/test/path/data', '/test/path/to/data',
                           '/test/other/path/data']
        self._2ddsets =  ['/test/path/data2', '/test/other/data']
        with h5py.File(self._fname('data'), 'w') as _file:
            _file.create_group('ext')
            _file['ext'].create_group('path')
            _file['ext/path'].create_dataset('data', data=self._data)
        with h5py.File(self._fname(1), 'w') as _file:
            _file.create_group('test')
            _file['test'].create_group('path')
            _file['test/path'].create_group('to')
            _file['test'].create_group('other')
            _file['test/other'].create_group('path')
            for dset in self._fulldsets:
                _file[dset] = self._data
            for dset in self._2ddsets:
                _file[dset] = self._data[0, 0]
            _file['test/other/extdata'] = h5py.ExternalLink(
                self._fname('data'), '/ext/path/data')
        self._fulldsets += ['/test/other/extdata']

    def tearDown(self):
        shutil.rmtree(self._path)

    def test_get_hdf5_file_and_dataset_names_wrong_type(self):
        _name = 123
        _dset = '/test/dset'
        with self.assertRaises(TypeError):
            _get_hdf5_file_and_dataset_names(_name, _dset)

    def test_get_hdf5_file_and_dataset_names_Path_type(self):
        _name = Path('c:/test/path/testfile.h5')
        _dset = '/test/dset'
        _newname, _newdset = _get_hdf5_file_and_dataset_names(_name, _dset)
        self.assertEqual(_name, Path(_newname))
        self.assertEqual(_dset, _newdset)

    def test_get_hdf5_file_and_dataset_names(self):
        _name = 'c:/test/path/testfile.h5'
        _dset = '/test/dset'
        _newname, _newdset = _get_hdf5_file_and_dataset_names(_name, _dset)
        self.assertEqual(_name, _newname)
        self.assertEqual(_dset, _newdset)

    def test_get_hdf5_file_and_dataset_names_joint(self):
        _name = 'c:/test/path/testfile.h5'
        _dset = '/test/dset'
        _option = f'{_name}://{_dset}'
        _newname, _newdset = _get_hdf5_file_and_dataset_names(_option)
        self.assertEqual(_name, _newname)
        self.assertEqual(_dset, _newdset)

    def test_get_hdf5_file_and_dataset_names_only_fname(self):
        _name = 'c:/test/path/testfile.h5'
        with self.assertRaises(KeyError):
            _get_hdf5_file_and_dataset_names(_name)

    def test_get_hdf5_metadata_meta_wrong_type(self):
        with self.assertRaises(TypeError):
            get_hdf5_metadata(self._ref, 123)

    def test_get_hdf5_metadata_meta_str(self):
        _res = get_hdf5_metadata(self._ref, 'nokey')
        self.assertEqual(_res, dict())

    def test_get_hdf5_metadata_meta_shape(self):
        _shape = get_hdf5_metadata(self._ref, 'shape')
        self.assertEqual(_shape, self._data.shape)

    def test_get_hdf5_metadata_meta_dtype(self):
        dtype = get_hdf5_metadata(self._ref, 'dtype')
        self.assertEqual(dtype, self._data.dtype)

    def test_get_hdf5_metadata_meta_size(self):
        size = get_hdf5_metadata(self._ref, 'size')
        self.assertEqual(size, self._data.size)

    def test_get_hdf5_metadata_meta_ndim(self):
        ndim = get_hdf5_metadata(self._ref, 'ndim')
        self.assertEqual(ndim, self._data.ndim)

    def test_get_hdf5_metadata_meta_nbytes(self):
        nbytes = get_hdf5_metadata(self._ref, 'nbytes')
        self.assertEqual(nbytes, self._data.nbytes)

    def test_get_hdf5_metadata_meta_wrong_key(self):
        with self.assertRaises(KeyError):
            get_hdf5_metadata(self._ref + '/more', 'dtype')

    def test_get_hdf5_metadata_meta_multiples(self):
        _res = get_hdf5_metadata(self._ref, ('ndim', 'size'))
        self.assertEqual(_res, dict(ndim=self._data.ndim,
                                    size=self._data.size))

    def test_hdf5_dataset_check_no_dset(self):
        self.assertFalse(hdf5_dataset_check('something'))

    def test_hdf5_dataset_check_simple(self):
        with h5py.File(self._fname(2), 'w') as _file:
            _file.create_group('test')
            _file['test'].create_dataset('data', data=self._data)
            self.assertTrue(hdf5_dataset_check(_file['test/data']))

    def test_hdf5_dataset_check_dim(self):
        with h5py.File(self._fname(2), 'w') as _file:
            _file.create_group('test')
            _file['test'].create_dataset('data', data=self._data)
            self.assertFalse(hdf5_dataset_check(_file['test/data'],
                                                min_dim=5))

    def test_hdf5_dataset_check_size(self):
        with h5py.File(self._fname(2), 'w') as _file:
            _file.create_group('test')
            _file['test'].create_dataset('data', data=self._data)
            self.assertFalse(hdf5_dataset_check(_file['test/data'],
                                                min_size=50000))

    def test_hdf5_dataset_check_ignoreList(self):
        with h5py.File(self._fname(2), 'w') as _file:
            _file.create_group('test')
            _file['test'].create_dataset('data', data=self._data)
            self.assertFalse(hdf5_dataset_check(_file['test/data'],
                                                ignoreList=('test/data')))

    def test_get_hdf5_populated_dataset_keys_str(self):
        _res = get_hdf5_populated_dataset_keys(self._fname(1))
        self.assertEqual(set(_res), set(self._fulldsets))

    def test_get_hdf5_populated_dataset_keys_path(self):
        _res = get_hdf5_populated_dataset_keys(Path(self._fname(1)))
        self.assertEqual(set(_res), set(self._fulldsets))

    def test_get_hdf5_populated_dataset_keys_h5py_file(self):
        with h5py.File(self._fname(1), 'r') as _file:
            _res = get_hdf5_populated_dataset_keys(_file)
        self.assertEqual(set(_res), set(self._fulldsets))

    def test_get_hdf5_populated_dataset_keys_h5py_dset(self):
        with h5py.File(self._fname(1), 'r') as _file:
            _res = get_hdf5_populated_dataset_keys(_file['test'])
        self.assertEqual(set(_res), set(self._fulldsets))

    def test_get_hdf5_populated_dataset_keys_smaller_dim(self):
        _res = get_hdf5_populated_dataset_keys(self._fname(1), min_dim=1)
        self.assertEqual(set(_res), set(self._fulldsets + self._2ddsets))

    def test_get_hdf5_populated_dataset_keys_larger_size(self):
        _res = get_hdf5_populated_dataset_keys(self._fname(1), min_dim=1,
                                               min_size=50000)
        self.assertEqual(set(_res), set())

    def test_get_hdf5_populated_dataset_keys_medium_size(self):
        _res = get_hdf5_populated_dataset_keys(self._fname(1), min_dim=1,
                                               min_size=1000)
        self.assertEqual(set(_res), set(self._fulldsets))


if __name__ == "__main__":
    unittest.main()
