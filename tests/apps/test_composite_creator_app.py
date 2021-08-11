# This file is part of pydidas.

# pydidas is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# Foobar is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with Foobar.  If not, see <http://www.gnu.org/licenses/>.

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

from pydidas.apps import CompositeCreatorApp
from pydidas.core import (ParameterCollection,
                          get_generic_parameter, CompositeImage)


class TestCompositeCreatorApp(unittest.TestCase):

    def setUp(self):
        self._path = tempfile.mkdtemp()
        self._fname = lambda i: Path(os.path.join(self._path,
                                                  f'test{i:02d}.npy'))
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
        CompositeCreatorApp.parse_func = lambda x: {}
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

    def test_creation_with_cmdargs(self):
        CompositeCreatorApp.parse_func = lambda x: {'binning': 4}
        app = CompositeCreatorApp()
        self.assertEqual(app.get_param_value('binning'), 4)

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

    def test_wait_for_image(self):
        _last_file = os.path.join(self._path, 'test_10.h5')
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
        app._image_metadata.update()
        app._check_and_set_bg_file()
        _image = app._config['bg_image']
        self.assertTrue((_image.array == self._data[0]).all())

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
                  app.get_param_value('composite_nx') * (self._img_shape[1] -5))
        self.assertEqual(app.composite.shape, _shape)


if __name__ == "__main__":
    unittest.main()
