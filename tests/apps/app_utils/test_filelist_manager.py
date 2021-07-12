
import copy
import os
import unittest
import tempfile
import shutil
from pathlib import Path
import sys
import numpy as np
import h5py


from pydidas.apps.app_utils import FilelistManager
from pydidas.core import (ParameterCollection, Parameter,
                          get_generic_parameter, CompositeImage)
from pydidas._exceptions import AppConfigError

class TestFilelistManager(unittest.TestCase):

    def setUp(self):
        self._path = tempfile.mkdtemp()
        self._fname = lambda i: Path(os.path.join(self._path, f'test{i:02d}.npy'))
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

    def test__update_params(self):
        fm = FilelistManager()
        fm._update_params(None, self._fname(0), None, None)
        self.assertEqual(fm.get_param_value('first_file'), Path())
        self.assertEqual(fm.get_param_value('last_file'), self._fname(0))

    def test__update_params_ii(self):
        fm = FilelistManager()
        fm._update_params(self._fname(0), self._fname(50), False, 2)
        self.assertEqual(fm.get_param_value('first_file'), self._fname(0))
        self.assertEqual(fm.get_param_value('last_file'), self._fname(50))
        self.assertEqual(fm.get_param_value('live_processing'), False)
        self.assertEqual(fm.get_param_value('file_stepping'), 2)

    def test__check_files_wrong_name(self):
        fm = FilelistManager()
        fm.set_param_value('first_file', self._fname(100))
        with self.assertRaises(AppConfigError):
            fm._check_files()

    def test__check_files_wrong_dir(self):
        fm = FilelistManager()
        fm.set_param_value('first_file', self._fname(0))
        fm.set_param_value('last_file', '/foo/bar/dummy.npy')
        with self.assertRaises(AppConfigError):
            fm._check_files()

    def test__check_files_all_good(self):
        fm = FilelistManager()
        fm.set_param_value('first_file', self._fname(0))
        fm.set_param_value('last_file', self._fname(50))

    def test__check_only_first_file_selected_true(self):
        fm = FilelistManager()
        fm.set_param_value('first_file', self._fname(0))
        self.assertTrue(fm._check_only_first_file_selected())

    def test__check_only_first_file_selected_false(self):
        fm = FilelistManager()
        fm.set_param_value('first_file', self._fname(0))
        fm.set_param_value('last_file', self._fname(50))
        self.assertFalse(fm._check_only_first_file_selected())

    def test__create_one_file_list(self):
        fm = FilelistManager()
        fm.set_param_value('first_file', self._fname(0))
        fm._create_one_file_list()
        self.assertEqual(fm._config['n_files'], 1)
        self.assertEqual(fm._config['file_list'], [self._fname(0)])

    def test__create_filelist_static(self):
        fm = FilelistManager()
        fm.set_param_value('first_file', self._fname(0))
        fm.set_param_value('last_file', self._fname(49))
        fm._create_filelist_static()
        self.assertEqual(fm._config['n_files'], 50)
        self.assertListEqual(fm._config['file_list'], [self._fname(i) for i in range(50)])

    def test__create_filelist_static_stepping(self):
        _stepping = 7
        fm = FilelistManager()
        fm.set_param_value('first_file', self._fname(0))
        fm.set_param_value('last_file', self._fname(49))
        fm.set_param_value('file_stepping', _stepping)
        fm._create_filelist_static()
        self.assertEqual(fm._config['n_files'], int(np.ceil(50 / _stepping)))
        self.assertListEqual(fm._config['file_list'],
                             [self._fname(i) for i in range(0, 50, _stepping)])

    def test__get_live_processing_naming_scheme(self):
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

    def test__get_live_processing_naming_scheme_wrong_ext(self):
        _index0 = 0
        _index1 = 7
        fm = FilelistManager()
        fm.set_param_value('first_file',
                           f'/foo/path/test_0000_file_{_index0:03d}.txt')
        fm.set_param_value('last_file',
                           f'/foo/path/test_0000_file_{_index1:03d}.text')
        with self.assertRaises(AppConfigError):
            _fnames, _range = fm._get_live_processing_naming_scheme()

    def test__get_live_processing_naming_scheme_wrong_length(self):
        _index0 = 0
        _index1 = 7
        fm = FilelistManager()
        fm.set_param_value('first_file',
                           f'/foo/path/test_0000_file_{_index0:03d}.txt')
        fm.set_param_value('last_file',
                           f'/foo/path/test_0000_file_{_index1:03d}_test.txt')
        with self.assertRaises(AppConfigError):
            _fnames, _range = fm._get_live_processing_naming_scheme()

    def test__get_live_processing_naming_scheme_wrong_length_ii(self):
        _index0 = 0
        _index1 = 7
        fm = FilelistManager()
        fm.set_param_value('first_file',
                           f'/foo/path/test_0000_file_{_index0:03d}.txt')
        fm.set_param_value('last_file',
                           f'/foo/path/test_0000_file_{_index1:05d}.txt')
        with self.assertRaises(AppConfigError):
            _fnames, _range = fm._get_live_processing_naming_scheme()

    def test__get_live_processing_naming_scheme_too_many_changes(self):
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
