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

__author__      = "Malte Storm"
__copyright__   = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.0.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"

import os
import unittest
import tempfile
import shutil
from pathlib import Path

import numpy as np
import h5py
from PyQt5 import QtCore

from pydidas.apps import CompositeCreatorApp
from pydidas.core import (ParameterCollection, Dataset,
                          get_generic_parameter, CompositeImage)
from pydidas._exceptions import AppConfigError

class TestCompositeCreatorApp(unittest.TestCase):

    def setUp(self):
        self._path = tempfile.mkdtemp()
        self._fname = lambda i: Path(os.path.join(self._path,
                                                  f'test{i:02d}.npy'))
        self._img_shape = (10, 10)
        self._n = 50
        self._data = np.random.random((self._n,) + self._img_shape)
        for i in range(self._n):
            np.save(self._fname(i), self._data[i])
        self._hdf5_fnames = [Path(os.path.join(self._path,
                                               f'test_{i:03d}.h5'))
                             for i in range(10)]
        for i in range(10):
            with h5py.File(self._hdf5_fnames[i], 'w') as f:
                f['/entry/data/data'] = self._data
        q_settings = QtCore.QSettings('Hereon', 'pydidas')
        self._border = int(q_settings.value('global/mosaic_border_width'))
        self._bgvalue = float(q_settings.value('global/mosaic_border_value'))
        self._globalmask = q_settings.value('global/det_mask')
        _mask = np.zeros((self._img_shape), dtype=np.bool_)
        _maskfile = Path(os.path.join(self._path, 'mask.npy'))
        np.save(_maskfile, _mask)
        q_settings.setValue('global/det_mask', _maskfile)
        self._maskfile = _maskfile

    def tearDown(self):
        q_settings = QtCore.QSettings('Hereon', 'pydidas')
        q_settings.setValue('global/det_mask', self._globalmask)
        shutil.rmtree(self._path)

    def get_default_app(self):
        self._ny = 5
        self._nx = (self._n // self._ny
                    + int(np.ceil((self._n % self._ny) / self._ny)))
        def parser(obj):
            return {}
        CompositeCreatorApp.parse_func = parser
        app = CompositeCreatorApp()
        app.set_param_value('first_file', self._fname(0))
        app.set_param_value('last_file', self._fname(self._n - 1))
        app.set_param_value('composite_nx', self._nx)
        app.set_param_value('composite_ny', self._ny)
        app.set_param_value('use_roi', True)
        app.set_param_value('roi_xlow', 5)
        return app

    def set_bg_params(self, app, bg_fname):
        app.set_param_value('first_file', self._hdf5_fnames[0])
        app.set_param_value('composite_nx', 8)
        app.set_param_value('composite_ny', 9)
        app.set_param_value('use_bg_file', True)
        app.set_param_value('bg_file', bg_fname)
        app._image_metadata.update()

    def test_creation(self):
        app = CompositeCreatorApp()
        self.assertIsInstance(app, CompositeCreatorApp)

    def test_creation_with_args(self):
        _nx = get_generic_parameter('composite_nx')
        _nx.value = 10
        _ny = get_generic_parameter('composite_ny')
        _ny.value = 5
        _dir = get_generic_parameter('composite_dir')
        _dir.value = 'y'
        _args = ParameterCollection(_nx, _ny, _dir)
        app = CompositeCreatorApp(_args)
        self.assertEqual(app.get_param_value('composite_nx'), _nx.value)
        self.assertEqual(app.get_param_value('composite_ny'), _ny.value)
        self.assertEqual(app.get_param_value('composite_dir'), 'y')

    def test_creation_with_cmdargs(self):
        CompositeCreatorApp.parse_func = lambda x: {'binning': 4}
        app = CompositeCreatorApp()
        self.assertEqual(app.get_param_value('binning'), 4)

    def test_multiprocessing_get_tasks(self):
        app = CompositeCreatorApp()
        with self.assertRaises(KeyError):
            app.multiprocessing_get_tasks()

    def test_multiprocessing_post_run(self):
        _outname = os.path.join(self._path, 'test_results.npy')
        app = self.get_default_app()
        app.set_param_value('output_fname', _outname)
        app.run()
        self.assertTrue(os.path.exists(_outname))

    def test_multiprocessing_carryon(self):
        _last_file = self._fname(10)
        app = self.get_default_app()
        app.run()
        app.set_param_value('live_processing', True)
        app._config['current_fname'] = _last_file
        self.assertTrue(app.multiprocessing_carryon())

    def test_multiprocessing_carryon_no_file(self):
        _last_file = self._fname(80)
        app = self.get_default_app()
        app.run()
        app.set_param_value('live_processing', True)
        app._config['current_fname'] = _last_file
        self.assertFalse(app.multiprocessing_carryon())

    def test_multiprocessing_store_with_bg(self):
        _bg_fname = os.path.join(self._path, 'bg.npy')
        np.save(_bg_fname, np.ones((10, 10)))
        app = self.get_default_app()
        app.set_param_value('use_bg_file', True)
        app.set_param_value('bg_file', _bg_fname)
        app.run()
        self.assertTrue((app._composite.image <= self._bgvalue).all())

    def test_live_processing_filelist(self):
        _last_file = os.path.join(self._path, 'test_010.h5')
        app = CompositeCreatorApp()
        app.set_param_value('first_file', self._hdf5_fnames[0])
        app.set_param_value('last_file', _last_file)
        app.set_param_value('live_processing', True)
        app._filelist.update()
        _app_file = app._filelist.get_filename(0)
        self.assertEqual(_app_file, self._hdf5_fnames[0])
        self.assertEqual(app._filelist.n_files, 11)

    def test_image_exists_check_no_file(self):
        _last_file = os.path.join(self._path, 'test_10.h5')
        app = CompositeCreatorApp()
        self.assertFalse(app._image_exists_check(_last_file, timeout=0.1))

    def test_image_exists_check_wrong_size(self):
        _last_file = os.path.join(self._path, 'test_bg.npy')
        np.save(_last_file, np.ones((2, 2)))
        app = CompositeCreatorApp()
        self.assertFalse(app._image_exists_check(_last_file, timeout=0.1))

    def test_image_exists_check(self):
        _last_file = os.path.join(self._fname(20))
        app = self.get_default_app()
        app.run()
        self.assertTrue(app._image_exists_check(_last_file, timeout=0.1))

    def test_check_and_set_bg_file_with_fname(self):
        app = CompositeCreatorApp()
        self.set_bg_params(app, self._fname(0))
        app._check_and_set_bg_file()
        _image = app._config['bg_image']
        self.assertTrue((_image.array == self._data[0]).all())

    def test_check_and_set_bg_file_with_hdf5_bg(self):
        app = CompositeCreatorApp()
        self.set_bg_params(app, self._hdf5_fnames[0])
        app._check_and_set_bg_file()
        _image = app._config['bg_image']
        self.assertTrue((_image.array == self._data[0]).all())

    def test_check_and_set_bg_file_wrong_size(self):
        app = CompositeCreatorApp()
        np.save(self._fname(999), np.zeros((self._img_shape[0] + 2,
                                            self._img_shape[1] + 2)))
        self.set_bg_params(app, self._fname(999))
        with self.assertRaises(AppConfigError):
            app._check_and_set_bg_file()

    def test_get_detector_mask__no_file(self):
        app = CompositeCreatorApp()
        app.q_settings.setValue('global/det_mask', 'no/such/file.tif')
        _mask = app._CompositeCreatorApp__get_detector_mask()
        self.assertIsNone(_mask)

    def test_get_detector_mask__wrong_file(self):
        app = CompositeCreatorApp()
        with open(self._maskfile, 'w') as f:
            f.write('this is not a numpy file.')
        _mask = app._CompositeCreatorApp__get_detector_mask()
        self.assertIsNone(_mask)

    def test_get_detector_mask__binning(self):
        app = CompositeCreatorApp()
        app.set_param_value('binning', 2)
        _mask = app._CompositeCreatorApp__get_detector_mask()
        _binned_shape = (self._img_shape[0] // 2, self._img_shape[1] // 2)
        self.assertEqual(_mask.shape, _binned_shape)

    def test_get_detector_mask__roi(self):
        app = CompositeCreatorApp()
        app.set_param_value('roi_xlow', 5)
        app.set_param_value('use_roi', True)
        app.set_param_value('first_file', self._hdf5_fnames[0])
        app._image_metadata.update()
        _mask = app._CompositeCreatorApp__get_detector_mask()
        _target_shape = (self._img_shape[0], self._img_shape[1] - 5)
        self.assertEqual(_mask.shape, _target_shape)

    def test_get_detector_mask__roi_and_binning(self):
        app = CompositeCreatorApp()
        app.set_param_value('roi_xlow', 4)
        app.set_param_value('use_roi', True)
        app.set_param_value('binning', 2)
        app.set_param_value('first_file', self._hdf5_fnames[0])
        app._image_metadata.update()
        _mask = app._CompositeCreatorApp__get_detector_mask()
        self.assertEqual(_mask.shape, app._image_metadata.final_shape)

    def test_apply_mask__no_mask(self):
        app = CompositeCreatorApp()
        app._config['det_mask'] = None
        _image = np.random.random((50, 50))
        _newimage = app._CompositeCreatorApp__apply_mask(_image)
        self.assertTrue((_image == _newimage).all())

    def test_apply_mask__with_mask_and_no_value(self):
        _shape = ((50, 50))
        rng = np.random.default_rng(12345)
        _mask = rng.integers(low=0, high=2, size=_shape)
        app = CompositeCreatorApp()
        app._config['det_mask'] = _mask
        app._config['det_mask_val'] = None
        _image = np.random.random(_shape)
        with self.assertRaises(AppConfigError):
            app._CompositeCreatorApp__apply_mask(_image)

    def test_apply_mask__with_mask_and_finite_mask_val(self):
        _shape = ((50, 50))
        rng = np.random.default_rng(12345)
        _mask = rng.integers(low=0, high=2, size=_shape)
        _val = rng.random() * 1e3
        app = CompositeCreatorApp()
        app._config['det_mask'] = _mask
        app._config['det_mask_val'] = _val
        _image = Dataset(np.random.random(_shape))
        _newimage = app._CompositeCreatorApp__apply_mask(_image)
        _delta = _newimage - _image
        self.assertTrue((_newimage[_mask == 1] == _val).all())
        self.assertTrue((_delta[_mask == 0] == 0).all())

    def test_apply_mask__with_mask_and_nan_mask_val(self):
        _shape = ((50, 50))
        _val = np.nan
        rng = np.random.default_rng(12345)
        _mask = rng.integers(low=0, high=2, size=_shape)
        app = CompositeCreatorApp()
        app._config['det_mask'] = _mask
        app._config['det_mask_val'] = _val
        _image = Dataset(np.random.random(_shape))
        _newimage = app._CompositeCreatorApp__apply_mask(_image)
        self.assertTrue(np.isnan(_newimage[_mask == 1]).all())

    def test_check_composite_dims(self):
        app = self.get_default_app()
        app.prepare_run()
        app._check_composite_dims()

    def test_check_composite_dims_nx(self):
        app = self.get_default_app()
        app.set_param_value('composite_nx', -1)
        app.prepare_run()

    def test_check_composite_dims_ny(self):
        app = self.get_default_app()
        app.set_param_value('composite_ny', -1)
        app.prepare_run()

    def test_check_composite_dims_too_small(self):
        app = self.get_default_app()
        app.set_param_value('composite_nx', 2)
        app.set_param_value('composite_ny', 2)
        with self.assertRaises(AppConfigError):
            app.prepare_run()

    def test_check_composite_dims_too_large(self):
        app = self.get_default_app()
        app.set_param_value('composite_nx', 20)
        app.set_param_value('composite_ny', 20)
        with self.assertRaises(AppConfigError):
            app.prepare_run()

    def test_prepare_run(self):
        app = self.get_default_app()
        app.prepare_run()
        _composite = app._composite
        self.assertIsInstance(_composite, CompositeImage)

    def test_prepare_run_as_slave(self):
        app = self.get_default_app()
        app.slave_mode = True
        app.prepare_run()
        self.assertIsNone(app._composite)

    def test_run(self):
        app = self.get_default_app()
        app.run()
        _xsize = 5
        _ysize = 10
        _data = np.zeros((_ysize * 5 + self._border * 4,
                          _xsize * 10 + self._border * 9)) + self._bgvalue
        for i in range(50):
            _nx = i % 10
            _ny = i // 10
            _ix = slice((_xsize + self._border) * _nx,
                        (_xsize + self._border) * _nx + _xsize)
            _iy = slice((_ysize + self._border) * _ny,
                        (_ysize + self._border) * _ny + _ysize)
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
        _shape = (app.get_param_value('composite_ny') *
                  (self._img_shape[0] + self._border) - self._border,
                  app.get_param_value('composite_nx') *
                  (self._img_shape[1] -5 + self._border) - self._border)
        self.assertEqual(app.composite.shape, _shape)

    def test__check_and_update_composite_image(self):
        app = self.get_default_app()
        _nx = self._ny
        _ny = self._nx
        app.prepare_run()
        _img_shape2 = (12, 12)
        _data2 = np.random.random((self._n,) + _img_shape2)
        for i in range(self._n):
            np.save(self._fname(i + self._n), _data2[i])
        app.set_param_value('composite_nx', _nx)
        app.set_param_value('composite_ny', _ny)
        app.set_param_value('first_file', self._fname(self._n))
        app.set_param_value('last_file', self._fname(2 * self._n - 1))
        app.prepare_run()
        _shape = app._image_metadata.final_shape
        _size = (_shape[0] * app.get_param_value('composite_ny')
                  + (app.get_param_value('composite_ny') - 1) * self._border,
                  _shape[1] * app.get_param_value('composite_nx')
                  + (app.get_param_value('composite_nx') - 1) * self._border)
        self.assertEqual(app._image_metadata.final_shape, (12, 7))
        self.assertEqual(app._composite.shape, _size)


if __name__ == "__main__":
    unittest.main()
