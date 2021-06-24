
import copy
import os
import unittest
import tempfile
import shutil
from pathlib import Path
import sys
import numpy as np
import h5py

import pydidas
from pydidas.apps import CompositeCreatorApp
from pydidas.core import (Parameter, ParameterCollection,
                          get_generic_parameter, CompositeImage)
from pydidas._exceptions import AppConfigError

class TestCompositeCreatorApp(unittest.TestCase):

    def setUp(self):
        self._path = tempfile.mkdtemp()
        self._fname = lambda i: os.path.join(self._path, f'test{i:02d}.npy')
        self._data = np.random.random((50, 10, 10))
        for i in range(50):
            np.save(self._fname(i), self._data[i])
        self._hdf_fname = os.path.join(self._path, 'test.h5')
        with h5py.File(self._hdf_fname, 'w') as f:
            f['/entry/data/data'] = self._data

    def tearDown(self):
        shutil.rmtree(self._path)

    def test_creation(self):
        app = CompositeCreatorApp()
        self.assertIsInstance(app, CompositeCreatorApp)

    def test_creation_with_cmdline_args(self):
        _argv = copy.copy(sys.argv)
        sys.argv = ['test', '-stepping', '5', '-binning', '2', '-first_file',
                    'testname']
        app = CompositeCreatorApp()
        sys.argv = _argv
        self.assertEqual(app.get_param_value('stepping'), 5)
        self.assertEqual(app.get_param_value('binning'), 2)
        self.assertEqual(app.get_param_value('first_file'), Path('testname'))

    def test_creation_with_args(self):
        _nx = get_generic_parameter('composite_nx')
        _nx.value = 10
        _ny = get_generic_parameter('composite_ny')
        _ny.value = 5
        _dir = get_generic_parameter('composite_dir')
        _dir.value = 'y'
        _args = ParameterCollection(_nx, _ny, _dir)
        app = CompositeCreatorApp(_args)
        self.assertEqual(app.get_param_value('composite_nx'), 10)
        self.assertEqual(app.get_param_value('composite_ny'), 5)
        self.assertEqual(app.get_param_value('composite_dir'), 'y')

    def test__store_image_data_from_file_range(self):
        app = CompositeCreatorApp()
        app.set_param_value('first_file', self._fname(0))
        app.set_param_value('last_file', self._fname(4))
        app.set_param_value('composite_nx', 3)
        app.set_param_value('composite_ny', 2)
        app._CompositeCreatorApp__store_image_data_from_file_range()
        _config = app._config
        self.assertEqual(_config['n_image'], 5)
        self.assertEqual(_config['raw_img_shape_y'], 10)
        self.assertEqual(_config['raw_img_shape_x'], 10)
        self.assertEqual(_config['datatype'], np.float64)

    def test__store_image_data_from_hdf_file(self):
        app = CompositeCreatorApp()
        app.set_param_value('first_file', self._hdf_fname)
        app.set_param_value('composite_nx', 8)
        app.set_param_value('composite_ny', 9)
        app._CompositeCreatorApp__store_image_data_from_hdf_file()
        _config = app._config
        self.assertEqual(_config['n_image'], 50)
        self.assertEqual(_config['raw_img_shape_y'], 10)
        self.assertEqual(_config['raw_img_shape_x'], 10)
        self.assertEqual(_config['datatype'], np.float64)

    def test__store_image_data_from_hdf_file_wrong_range(self):
        app = CompositeCreatorApp()
        app.set_param_value('first_file', self._hdf_fname)
        app.set_param_value('composite_nx', 8)
        app.set_param_value('composite_ny', 9)
        app._CompositeCreatorApp__store_image_data_from_hdf_file()
        app.set_param_value('hdf_first_image_num', 10)
        app.set_param_value('hdf_last_image_num', -45)
        with self.assertRaises(AppConfigError):
            app._CompositeCreatorApp__store_image_data_from_hdf_file()

    def test_check_files_hdf(self):
        app = CompositeCreatorApp()
        app.set_param_value('first_file', self._hdf_fname)
        app._CompositeCreatorApp__check_files()

    def test___check_and_set_bg_file_with_fname(self):
        app = CompositeCreatorApp()
        app.set_param_value('first_file', self._hdf_fname)
        app.set_param_value('composite_nx', 8)
        app.set_param_value('composite_ny', 9)
        app.set_param_value('use_bg_file', True)
        app.set_param_value('bg_file', self._fname(0))
        app._CompositeCreatorApp__store_image_data_from_hdf_file()
        app._CompositeCreatorApp__process_roi()
        app._CompositeCreatorApp__check_and_set_bg_file()
        _image = app._config['bg_image']
        self.assertTrue((_image.array == self._data[0]).all())

    def test__check_roi(self):
        app = CompositeCreatorApp()
        app._config['raw_img_shape_x'] = 10
        app._config['raw_img_shape_y'] = 10
        app.set_param_value('use_roi', True)
        app.set_param_value('roi_xlow', 15)
        app.set_param_value('roi_ylow', 1)
        app._CompositeCreatorApp__check_roi()
        app.set_param_value('roi_xhigh', 3)
        self.assertEqual(app.get_param_value('roi_xlow'), 5)
        self.assertEqual(app.get_param_value('roi_ylow'), 1)
        self.assertEqual(app.get_param_value('roi_xhigh'), 3)
        self.assertEqual(app.get_param_value('roi_yhigh'), 10)
        with self.assertRaises(AppConfigError):
            app._CompositeCreatorApp__check_roi()

    def test_check_entries(self):
        app = CompositeCreatorApp()
        app.set_param_value('first_file', self._fname(0))
        app.set_param_value('last_file', self._fname(49))
        app.set_param_value('composite_nx', 10)
        app.set_param_value('composite_ny', 5)
        app.set_param_value('use_roi', True)
        app.set_param_value('roi_xlow', 5)
        app.check_entries()


    def test_prepare_run(self):
        app = CompositeCreatorApp()
        app.set_param_value('first_file', self._fname(0))
        app.set_param_value('last_file', self._fname(49))
        app.set_param_value('composite_nx', 10)
        app.set_param_value('composite_ny', 5)
        app.set_param_value('use_roi', True)
        app.set_param_value('roi_xlow', 5)
        app.prepare_run()
        _composite = app._CompositeCreatorApp__composite
        self.assertIsInstance(_composite, CompositeImage)

    def test_apply_thresholds(self):
        ...

    def test_run(self):
        app = CompositeCreatorApp()
        app.set_param_value('first_file', self._fname(0))
        app.set_param_value('last_file', self._fname(49))
        app.set_param_value('composite_nx', 10)
        app.set_param_value('composite_ny', 5)
        app.set_param_value('use_roi', True)
        app.set_param_value('roi_xlow', 5)
        app.run()
        _data = np.zeros((50, 50))
        for i in range(50):
            _ix = slice(5 * (i % 10), 5 * (i % 10 + 1))
            _iy = slice(10 * (i // 10), 10 * (i // 10 + 1))
            _data[_iy, _ix] = self._data[i, :, 5:]
        self.assertTrue((app.composite == _data).all())

    def test_apply_thresholds_with_kwargs(self):
        app = CompositeCreatorApp()
        app.set_param_value('first_file', self._fname(0))
        app.set_param_value('last_file', self._fname(49))
        app.set_param_value('composite_nx', 10)
        app.set_param_value('composite_ny', 5)
        app.set_param_value('use_roi', True)
        app.set_param_value('roi_xlow', 5)
        app.run()
        app.apply_thresholds(low=0.2, high=0.7)
        self.assertTrue((app.composite >= 0.2).all())
        self.assertTrue((app.composite <= 0.7).all())
        app.set_param_value('use_thresholds', True)
        app.set_param_value('threshold_low', 0.3)
        app.set_param_value('threshold_high', 0.6)
        app.apply_thresholds()
        self.assertTrue((app.composite >= 0.3).all())
        self.assertTrue((app.composite <= 0.6).all())

    def test_apply_thresholds_with_params(self):
        app = CompositeCreatorApp()
        app.set_param_value('first_file', self._fname(0))
        app.set_param_value('last_file', self._fname(49))
        app.set_param_value('composite_nx', 10)
        app.set_param_value('composite_ny', 5)
        app.set_param_value('use_roi', True)
        app.set_param_value('roi_xlow', 5)
        app.run()
        app.set_param_value('use_thresholds', True)
        app.set_param_value('threshold_low', 0.3)
        app.set_param_value('threshold_high', 0.6)
        app.apply_thresholds()
        self.assertTrue((app.composite >= 0.3).all())
        self.assertTrue((app.composite <= 0.6).all())

    def test_export_image_png(self):
        app = CompositeCreatorApp()
        app.set_param_value('first_file', self._fname(0))
        app.set_param_value('last_file', self._fname(49))
        app.set_param_value('composite_nx', 10)
        app.set_param_value('composite_ny', 5)
        app.set_param_value('use_roi', True)
        app.set_param_value('roi_xlow', 5)
        app.run()
        _path = os.path.join(self._path, 'test_image.png')
        app.export_image(_path)
        self.assertTrue(os.path.exists(_path))

    def test_export_image_npy(self):
        app = CompositeCreatorApp()
        app.set_param_value('first_file', self._fname(0))
        app.set_param_value('last_file', self._fname(49))
        app.set_param_value('composite_nx', 10)
        app.set_param_value('composite_ny', 5)
        app.set_param_value('use_roi', True)
        app.set_param_value('roi_xlow', 5)
        app.run()
        _path = os.path.join(self._path, 'test_image.npy')
        app.export_image(_path)
        _data = np.load(_path)
        self.assertTrue((_data == app.composite).all())

if __name__ == "__main__":
    unittest.main()
