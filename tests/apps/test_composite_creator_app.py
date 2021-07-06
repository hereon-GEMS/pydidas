
import copy
import os
import unittest
import tempfile
import shutil
from pathlib import Path
import sys
import numpy as np
import h5py


from pydidas.apps import CompositeCreatorApp
from pydidas.core import (ParameterCollection,
                          get_generic_parameter, CompositeImage)
from pydidas._exceptions import AppConfigError

class TestCompositeCreatorApp(unittest.TestCase):

    def setUp(self):
        self._path = tempfile.mkdtemp()
        self._fname = lambda i: Path(os.path.join(self._path, f'test{i:02d}.npy'))
        self._img_shape = (10, 10)
        self._data = np.random.random((50,) + self._img_shape)
        for i in range(50):
            np.save(self._fname(i), self._data[i])
        self._hdf5_fnames = [Path(os.path.join(self._path, f'test_{i:03d}.h5'))
                            for i in range(10)]
        for i in range(10):
            with h5py.File(self._hdf5_fnames[i], 'w') as f:
                f['/entry/data/data'] = self._data

    def tearDown(self):
        shutil.rmtree(self._path)

    def get_default_app(self):
        _ny = 5
        _nx = ((self._data.shape[0] // _ny)
               + np.ceil((self._data.shape[0] % _ny) / _ny).astype(int))
        app = CompositeCreatorApp()
        app.set_param_value('first_file', self._fname(0))
        app.set_param_value('last_file', self._fname(49))
        app.set_param_value('composite_nx', _nx)
        app.set_param_value('composite_ny', _ny)
        app.set_param_value('use_roi', True)
        app.set_param_value('roi_xlow', 5)
        return app

    def test_creation(self):
        app = CompositeCreatorApp()
        self.assertIsInstance(app, CompositeCreatorApp)

    def test_creation_with_cmdline_args(self):
        _argv = copy.copy(sys.argv)
        sys.argv = ['test', '-file_stepping', '5', '-binning', '2',
                    '-first_file', 'testname']
        app = CompositeCreatorApp()
        sys.argv = _argv
        self.assertEqual(app.get_param_value('file_stepping'), 5)
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

    def test_store_image_data_from_file_range(self):
        app = CompositeCreatorApp()
        app.set_param_value('first_file', self._fname(0))
        app.set_param_value('last_file', self._fname(4))
        app.set_param_value('composite_nx', 3)
        app.set_param_value('composite_ny', 2)
        app._store_image_data_from_single_image()
        _config = app._config
        self.assertEqual(_config['n_image_per_file'], 1)
        self.assertEqual(_config['raw_img_shape_y'], 10)
        self.assertEqual(_config['raw_img_shape_x'], 10)
        self.assertEqual(_config['datatype'], np.float64)

    def test_store_image_data_from_hdf_file(self):
        app = CompositeCreatorApp()
        app.set_param_value('first_file', self._hdf5_fnames[0])
        app.set_param_value('composite_nx', 8)
        app.set_param_value('composite_ny', 9)
        app._store_image_data_from_hdf5_file()
        _config = app._config
        self.assertEqual(_config['n_image_per_file'], 50)
        self.assertEqual(_config['raw_img_shape_y'], 10)
        self.assertEqual(_config['raw_img_shape_x'], 10)
        self.assertEqual(_config['datatype'], np.float64)

    def test_store_image_data_from_hdf_file_wrong_range(self):
        app = CompositeCreatorApp()
        app.set_param_value('first_file', self._hdf5_fnames[0])
        app.set_param_value('composite_nx', 8)
        app.set_param_value('composite_ny', 9)
        app._store_image_data_from_hdf5_file()
        app.set_param_value('hdf5_first_image_num', 10)
        app.set_param_value('hdf5_last_image_num', -45)
        with self.assertRaises(AppConfigError):
            app._store_image_data_from_hdf5_file()

    def test_live_processing_filelist(self):
        _last_file = os.path.join(self._path, f'test_010.h5')
        app = CompositeCreatorApp()
        app.set_param_value('first_file', self._hdf5_fnames[0])
        app.set_param_value('last_file', _last_file)
        app.set_param_value('live_processing', True)
        app._create_filelist()
        _app_file = app._filelist.get_filename(0)
        self.assertEqual(_app_file, self._hdf5_fnames[0])
        self.assertEqual(app._filelist.n_files, 11)

    def test_wait_for_image(self):
        _last_file = os.path.join(self._path, f'test_10.h5')
        app = CompositeCreatorApp()
        with self.assertRaises(FileNotFoundError):
            app._wait_for_image(_last_file, timeout=0.1)

    def test_check_and_set_bg_file_with_fname(self):
        app = CompositeCreatorApp()
        app.set_param_value('first_file', self._hdf5_fnames[0])
        app.set_param_value('composite_nx', 8)
        app.set_param_value('composite_ny', 9)
        app.set_param_value('use_bg_file', True)
        app.set_param_value('bg_file', self._fname(0))
        app._store_image_data_from_hdf5_file()
        app._process_roi()
        app._check_and_set_bg_file()
        _image = app._config['bg_image']
        self.assertTrue((_image.array == self._data[0]).all())

    def test_check_roi(self):
        app = CompositeCreatorApp()
        app._config['raw_img_shape_x'] = 10
        app._config['raw_img_shape_y'] = 10
        app.set_param_value('use_roi', True)
        app.set_param_value('roi_xlow', 15)
        app.set_param_value('roi_ylow', 1)
        app._check_roi_for_consistency()
        self.assertEqual(app.get_param_value('roi_xlow'), 5)
        self.assertEqual(app.get_param_value('roi_ylow'), 1)

    def test_check_roi_wrong_range(self):
        app = CompositeCreatorApp()
        app._config['raw_img_shape_x'] = 10
        app._config['raw_img_shape_y'] = 10
        app.set_param_value('use_roi', True)
        app.set_param_value('roi_xlow', 15)
        app.set_param_value('roi_ylow', 1)
        app.set_param_value('roi_xhigh', 3)
        with self.assertRaises(AppConfigError):
            app._check_roi_for_consistency()

    def test_prepare_run(self):
        app = self.get_default_app()
        app.prepare_run()
        _composite = app._composite
        self.assertIsInstance(_composite, CompositeImage)

    def test_run(self):
        app = self.get_default_app()
        app.run()
        _data = np.zeros((50, 50))
        for i in range(50):
            _ix = slice(5 * (i % 10), 5 * (i % 10 + 1))
            _iy = slice(10 * (i // 10), 10 * (i // 10 + 1))
            _data[_iy, _ix] = self._data[i, :, 5:]
        self.assertTrue((app.composite == _data).all())

    def test_apply_thresholds_with_kwargs(self):
        app = self.get_default_app()
        app.run()
        app.apply_thresholds(low=0.2, high=0.7)
        self.assertTrue((app.composite >= 0.2).all())
        self.assertTrue((app.composite <= 0.7).all())

    def test_apply_thresholds_with_params(self):
        app = self.get_default_app()
        app.run()
        app.set_param_value('use_thresholds', True)
        app.set_param_value('threshold_low', 0.3)
        app.set_param_value('threshold_high', 0.6)
        app.apply_thresholds()
        self.assertTrue((app.composite >= 0.3).all())
        self.assertTrue((app.composite <= 0.6).all())

    def test_hdf5_file_range(self):
        app = CompositeCreatorApp()
        app.set_param_value('first_file', self._hdf5_fnames[1])
        app.set_param_value('last_file', self._hdf5_fnames[4])
        app.set_param_value('composite_nx', 20)
        app.set_param_value('composite_ny', 10)
        app.run()

    def test_export_image_png(self):
        app = self.get_default_app()
        app.run()
        _path = os.path.join(self._path, 'test_image.png')
        app.export_image(_path)
        self.assertTrue(os.path.exists(_path))

    def test_export_image_npy(self):
        app = self.get_default_app()
        app.run()
        _path = os.path.join(self._path, 'test_image.npy')
        app.export_image(_path)
        _data = np.load(_path)
        self.assertTrue((_data == app.composite).all())

    def test_stepping(self):
        app = self.get_default_app()
        app.set_param_value('file_stepping', 2)
        _nx = np.ceil(app.get_param_value('composite_nx') / 2).astype(int)
        app.set_param_value('composite_nx', _nx)
        app.run()
        _shape = (app.get_param_value('composite_ny') * self._img_shape[0],
                  app.get_param_value('composite_nx') * (self._img_shape[0] -5))
        self.assertEqual(app.composite.shape, _shape)

if __name__ == "__main__":
    unittest.main()
