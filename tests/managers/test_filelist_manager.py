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
__version__ = "0.1.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"


import copy
import os
import unittest
import tempfile
import shutil
from pathlib import Path

import numpy as np

from pydidas.core import get_generic_parameter, AppConfigError
from pydidas.managers import FilelistManager


class TestFilelistManager(unittest.TestCase):

    def setUp(self):
        self._path = tempfile.mkdtemp()
        self._fname = lambda i: Path(os.path.join(self._path,
                                                  f'test_{i:02d}.npy'))
        self._img_shape = (10, 10)
        self._data = np.random.random((50,) + self._img_shape)
        for i in range(50):
            np.save(self._fname(i), self._data[i])
        for i in range(50, 60):
            np.save(self._fname(i), np.random.random((20, 20)))

    def tearDown(self):
        shutil.rmtree(self._path)

    def test_creation(self):
        fm = FilelistManager()
        self.assertIsInstance(fm, FilelistManager)

    def test_creation_with_params(self):
        p = get_generic_parameter('file_stepping')
        p.value = 4
        fm = FilelistManager(p)
        self.assertIsInstance(fm, FilelistManager)
        self.assertEqual(fm.get_param_value('file_stepping'), 4)

    def test_n_files_None(self):
        fm = FilelistManager()
        self.assertEqual(fm.n_files, 0)

    def test_n_files(self):
        _n = 123
        fm = FilelistManager()
        fm._config['n_files'] = _n
        self.assertEqual(fm.n_files, _n)

    def test_get_config(self):
        fm = FilelistManager()
        cfg = fm.get_config()
        self.assertIsInstance(cfg, dict)

    def test_property_filesize(self):
        fm = FilelistManager()
        fm.update(self._fname(0), self._fname(40), False, 2)
        self.assertEqual(fm.filesize, os.stat(self._fname(0)).st_size)

    def test_update_params(self):
        fm = FilelistManager()
        fm._update_params(None, self._fname(0), None, None)
        self.assertEqual(fm.get_param_value('first_file'), Path())
        self.assertEqual(fm.get_param_value('last_file'), self._fname(0))

    def test_update_params_ii(self):
        fm = FilelistManager()
        fm._update_params(self._fname(0), self._fname(50), False, 2)
        self.assertEqual(fm.get_param_value('first_file'), self._fname(0))
        self.assertEqual(fm.get_param_value('last_file'), self._fname(50))
        self.assertEqual(fm.get_param_value('live_processing'), False)
        self.assertEqual(fm.get_param_value('file_stepping'), 2)

    def test_check_files_wrong_name(self):
        fm = FilelistManager()
        fm.set_param_value('first_file', self._fname(100))
        with self.assertRaises(AppConfigError):
            fm._check_files()

    def test_check_files_wrong_dir(self):
        fm = FilelistManager()
        fm.set_param_value('first_file', self._fname(0))
        fm.set_param_value('last_file', '/foo/bar/dummy.npy')
        with self.assertRaises(AppConfigError):
            fm._check_files()

    def test_check_files_all_good(self):
        fm = FilelistManager()
        fm.set_param_value('first_file', self._fname(0))
        fm.set_param_value('last_file', self._fname(50))

    def test_check_only_first_file_selected_true(self):
        fm = FilelistManager()
        fm.set_param_value('first_file', self._fname(0))
        self.assertTrue(fm._check_only_first_file_selected())

    def test_check_only_first_file_selected_false(self):
        fm = FilelistManager()
        fm.set_param_value('first_file', self._fname(0))
        fm.set_param_value('last_file', self._fname(50))
        self.assertFalse(fm._check_only_first_file_selected())

    def test_create_one_file_list(self):
        fm = FilelistManager()
        fm.set_param_value('first_file', self._fname(0))
        fm._create_one_file_list()
        self.assertEqual(fm._config['n_files'], 1)
        self.assertEqual(fm._config['file_list'], [self._fname(0)])

    def test_create_filelist_with_live(self):
        fm = FilelistManager()
        fm.set_param_value('first_file', self._fname(0))
        fm.set_param_value('last_file', self._fname(49))
        fm.set_param_value('live_processing', True)
        fm._create_filelist()
        self.assertEqual(fm._config['n_files'], 50)
        self.assertListEqual(fm._config['file_list'], [self._fname(i) for i in range(50)])

    def test_create_filelist_static(self):
        fm = FilelistManager()
        fm.set_param_value('first_file', self._fname(0))
        fm.set_param_value('last_file', self._fname(49))
        fm._create_filelist_static()
        self.assertEqual(fm._config['n_files'], 50)
        self.assertListEqual(fm._config['file_list'], [self._fname(i) for i in range(50)])

    def test_create_filelist_static_stepping(self):
        _stepping = 7
        fm = FilelistManager()
        fm.set_param_value('first_file', self._fname(0))
        fm.set_param_value('last_file', self._fname(49))
        fm.set_param_value('file_stepping', _stepping)
        fm._create_filelist_static()
        self.assertEqual(fm._config['n_files'], int(np.ceil(50 / _stepping)))
        self.assertListEqual(fm._config['file_list'],
                             [self._fname(i) for i in range(0, 50, _stepping)])

    def test_get_live_processing_naming_scheme(self):
        _index0 = 0
        _index1 = 7
        fm = FilelistManager()
        fm.set_param_value('first_file',
                           f'/foo/path/test_0000_file_{_index0:03d}.txt')
        fm.set_param_value('last_file',
                           f'/foo/path/test_0000_file_{_index1:03d}.txt')
        _fnames, _range = fm._get_live_processing_naming_scheme()
        self.assertEqual(_range[0], _index0)
        self.assertEqual(_range[-1], _index1)
        self.assertEqual(Path(_fnames.format(index=0)),
                          fm.get_param_value('first_file'))

    def test_get_live_processing_naming_scheme_wrong_ext(self):
        _index0 = 0
        _index1 = 7
        fm = FilelistManager()
        fm.set_param_value('first_file',
                           f'/foo/path/test_0000_file_{_index0:03d}.txt')
        fm.set_param_value('last_file',
                           f'/foo/path/test_0000_file_{_index1:03d}.text')
        with self.assertRaises(AppConfigError):
            _fnames, _range = fm._get_live_processing_naming_scheme()

    def test_get_live_processing_naming_scheme_wrong_length(self):
        _index0 = 0
        _index1 = 7
        fm = FilelistManager()
        fm.set_param_value('first_file',
                           f'/foo/path/test_0000_file_{_index0:03d}.txt')
        fm.set_param_value('last_file',
                           f'/foo/path/test_0000_file_{_index1:03d}_test.txt')
        with self.assertRaises(AppConfigError):
            _fnames, _range = fm._get_live_processing_naming_scheme()

    def test_get_live_processing_naming_scheme_wrong_length_ii(self):
        _index0 = 0
        _index1 = 7
        fm = FilelistManager()
        fm.set_param_value('first_file',
                           f'/foo/path/test_0000_file_{_index0:03d}.txt')
        fm.set_param_value('last_file',
                           f'/foo/path/test_0000_file_{_index1:05d}.txt')
        with self.assertRaises(AppConfigError):
            _fnames, _range = fm._get_live_processing_naming_scheme()

    def test_get_live_processing_naming_scheme_too_many_changes(self):
        _index0 = 0
        _index1 = 7
        fm = FilelistManager()
        fm.set_param_value('first_file',
                           f'/foo/path/test_0000_file_{_index0:03d}.txt')
        fm.set_param_value('last_file',
                           f'/foo/path/test_0001_file_{_index1:03d}.txt')
        with self.assertRaises(AppConfigError):
            _fnames, _range = fm._get_live_processing_naming_scheme()

    def test_update_params(self):
        fm = FilelistManager()
        fm.update(self._fname(0), self._fname(49))
        self.assertEqual(fm._config['n_files'], 50)

    def test_get_filename(self):
        fm = FilelistManager()
        fm.update(self._fname(0), self._fname(49))
        self.assertEqual(fm._config['n_files'], 50)
        self.assertEqual(len(fm._config['file_list']), 50)
        self.assertEqual(self._fname(10), fm.get_filename(10))

    def test_get_filename_empty_list(self):
        fm = FilelistManager()
        with self.assertRaises(AppConfigError):
            fm.get_filename(0)

    def test_get_filename_out_of_range(self):
        fm = FilelistManager()
        fm.update(self._fname(0), self._fname(49))
        with self.assertRaises(AppConfigError):
            fm.get_filename(80)

    def test_copy(self):
        fm = FilelistManager()
        fm.set_param_value('first_file', self._fname(0))
        fm.update()
        fm2 = copy.copy(fm)
        self.assertIsInstance(fm2, FilelistManager)
        self.assertNotEqual(fm.params, fm2.params)
        self.assertEqual(fm.get_param_value('first_file'),
                         fm2.get_param_value('first_file'))

    def test_reset(self):
        fm = FilelistManager()
        fm.update(self._fname(0), self._fname(49))
        fm.reset()
        self.assertEqual(fm._config['n_files'], 0)
        self.assertEqual(len(fm._config['file_list']), 0)


if __name__ == "__main__":
    unittest.main()
