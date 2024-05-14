# This file is part of pydidas.
#
# Copyright 2023 - 2024, Helmholtz-Zentrum Hereon
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
__copyright__ = "Copyright 2023 - 2024, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"


import os
import shutil
import tempfile
import time
import unittest
from pathlib import Path

import h5py
import numpy as np
from qtpy import QtTest

from pydidas import IS_QT6
from pydidas.apps import CompositeCreatorApp
from pydidas.core import (
    Dataset,
    ParameterCollection,
    PydidasQsettings,
    UserConfigError,
    get_generic_parameter,
)
from pydidas.managers import CompositeImageManager


class TestCompositeCreatorApp(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._path = Path(tempfile.mkdtemp())
        cls._img_shape = (10, 10)
        cls._n_total = 50
        cls._n_files = 10
        cls._data = np.random.random((cls._n_total,) + cls._img_shape)
        for i in range(cls._n_total):
            np.save(cls._fname(i), cls._data[i])
        cls._hdf5_fnames = [
            cls._path.joinpath(f"test_{i:03d}.h5") for i in range(cls._n_files)
        ]
        _n_per_file = int(cls._n_total / cls._n_files)
        for i in range(cls._n_files):
            with h5py.File(cls._hdf5_fnames[i], "w") as f:
                f["/entry/data/data"] = cls._data[
                    slice(i * _n_per_file, (i + 1) * _n_per_file)
                ]

        cls._q_settings = PydidasQsettings()
        cls._border = cls._q_settings.value("user/mosaic_border_width", int)
        cls._bgvalue = cls._q_settings.value("user/mosaic_border_value", float)
        _mask = np.zeros(cls._img_shape, dtype=np.bool_)
        _maskfile = cls._path.joinpath("mask.npy")
        np.save(_maskfile, _mask)
        cls._maskfile = _maskfile

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls._path)
        cls._q_settings = PydidasQsettings()

    @classmethod
    def _fname(cls, i: int):
        return cls._path.joinpath(f"test{i:02d}.npy")

    def get_default_app(self):
        self._ny = 5
        self._nx = self._n_total // self._ny + int(
            np.ceil((self._n_total % self._ny) / self._ny)
        )
        setattr(CompositeCreatorApp, "parse_func", lambda obj: {})
        app = CompositeCreatorApp()
        app.set_param_value("first_file", self._fname(0))
        app.set_param_value("last_file", self._fname(self._n_total - 1))
        app.set_param_value("composite_nx", self._nx)
        app.set_param_value("composite_ny", self._ny)
        app.set_param_value("use_roi", True)
        app.set_param_value("roi_xlow", 5)
        app._image_metadata.update(filename=self._fname(0))
        app._filelist.update()
        return app

    def create_single_composite_and_insert_image(self, app):
        _image = np.random.random(self._img_shape)
        app._composite = CompositeImageManager(
            image_shape=_image.shape, composite_nx=1, composite_ny=1
        )
        app._composite.insert_image(_image, 0)
        return _image

    @staticmethod
    def create_full_composite(app):
        app._image_metadata.update()
        app._composite = CompositeImageManager(
            image_shape=app._image_metadata.final_shape,
            composite_nx=app.get_param_value("composite_nx"),
            composite_ny=app.get_param_value("composite_ny"),
            composite_dir=app.get_param_value("composite_dir"),
            datatype=app._image_metadata.datatype,
        )

    @staticmethod
    def set_bg_params(app, bg_fname):
        app.set_param_value("use_bg_file", True)
        app.set_param_value("bg_file", bg_fname)
        app._image_metadata.update()

    def test_creation(self):
        app = CompositeCreatorApp()
        self.assertIsInstance(app, CompositeCreatorApp)

    def test_creation_with_args(self):
        _nx = get_generic_parameter("composite_nx")
        _nx.value = 10
        _ny = get_generic_parameter("composite_ny")
        _ny.value = 5
        _dir = get_generic_parameter("composite_dir")
        _dir.value = "y"
        _args = ParameterCollection(_nx, _ny, _dir)
        app = CompositeCreatorApp(_args)
        self.assertEqual(app.get_param_value("composite_nx"), _nx.value)
        self.assertEqual(app.get_param_value("composite_ny"), _ny.value)
        self.assertEqual(app.get_param_value("composite_dir"), "y")

    def test_creation_with_cmdargs(self):
        CompositeCreatorApp.parse_func = lambda x: {"binning": 4}
        app = CompositeCreatorApp()
        self.assertEqual(app.get_param_value("binning"), 4)

    def test_composite_property(self):
        _image = np.random.random((10, 10))
        _composite = CompositeImageManager(
            image_shape=_image.shape, composite_nx=1, composite_ny=1
        )
        _composite.insert_image(_image, 0)
        app = CompositeCreatorApp()
        app._composite = _composite
        _composite_image = app.composite
        self.assertTrue(np.isclose(_composite_image, _image).all())

    def test_composite_property_no_composite(self):
        app = CompositeCreatorApp()
        self.assertIsNone(app.composite)

    def test_export_image_png(self):
        app = self.get_default_app()
        app.run()
        _path = os.path.join(self._path, "test_image.png")
        app.export_image(_path)
        self.assertTrue(os.path.exists(_path))

    def test_export_image_npy(self):
        app = self.get_default_app()
        app.run()
        _path = os.path.join(self._path, "test_image.npy")
        app.export_image(_path)
        _data = np.load(_path)
        self.assertTrue((_data == app.composite).all())

    def test_multiprocessing_store_results(self):
        app = self.get_default_app()
        _image = np.random.random(self._img_shape)
        app._composite = CompositeImageManager(
            image_shape=_image.shape, composite_nx=1, composite_ny=1
        )
        _spy = QtTest.QSignalSpy(app.updated_composite)
        app.multiprocessing_store_results(0, _image)
        time.sleep(0.02)
        self.assertTrue(np.isclose(app.composite, _image).all())
        _spy_result = _spy.count() if IS_QT6 else len(_spy)
        self.assertEqual(_spy_result, 1)

    def test_multiprocessing_store_results__with_bg(self):
        _image = np.random.random(self._img_shape)
        app = self.get_default_app()
        app.set_param_value("use_bg_file", True)
        app._bg_image = _image
        app._composite = CompositeImageManager(
            image_shape=_image.shape, composite_nx=1, composite_ny=1
        )
        _spy = QtTest.QSignalSpy(app.updated_composite)
        app.multiprocessing_store_results(0, _image)
        time.sleep(0.02)
        self.assertTrue((app.composite == 0).all())
        _spy_result = _spy.count() if IS_QT6 else len(_spy)
        self.assertEqual(_spy_result, 1)

    def test_multiprocessing_store_results__as_slave(self):
        app = self.get_default_app()
        app.slave_mode = True
        _spy = QtTest.QSignalSpy(app.updated_composite)
        app.multiprocessing_store_results(0, 0)
        time.sleep(0.02)
        _spy_result = _spy.count() if IS_QT6 else len(_spy)
        self.assertEqual(_spy_result, 0)

    def test_apply_thresholds__plain(self):
        app = self.get_default_app()
        _image = self.create_single_composite_and_insert_image(app)
        app.apply_thresholds()
        self.assertTrue(np.isclose(app.composite, _image).all())

    def test_apply_thresholds__with_thresholds(self):
        _thresh_low = 0.3
        _thresh_high = 0.6
        app = self.get_default_app()
        _ = self.create_single_composite_and_insert_image(app)
        app.set_param_value("use_thresholds", True)
        app.set_param_value("threshold_low", _thresh_low)
        app.set_param_value("threshold_high", _thresh_high)
        app.apply_thresholds()
        self.assertEqual(np.where(app.composite < _thresh_low)[0].size, 0)
        self.assertEqual(np.where(app.composite > _thresh_high)[0].size, 0)

    def test_apply_thresholds__with_kwargs(self):
        _thresh_low = 0.3
        _thresh_high = 0.6
        app = self.get_default_app()
        _ = self.create_single_composite_and_insert_image(app)
        app.apply_thresholds(low=_thresh_low, high=_thresh_high)
        self.assertEqual(np.where(app.composite < _thresh_low)[0].size, 0)
        self.assertEqual(np.where(app.composite > _thresh_high)[0].size, 0)

    def test_multiprocessing_post_run(self):
        app = self.get_default_app()
        app.multiprocessing_post_run()
        # assert does not raise an Error

    def test_apply_mask__no_mask(self):
        app = CompositeCreatorApp()
        _image = np.random.random((50, 50))
        _new_image = app._CompositeCreatorApp__apply_mask(_image)
        self.assertTrue(np.isclose(_image, _new_image).all())

    def test_apply_mask__with_mask_and_finite_mask_val(self):
        _shape = (50, 50)
        rng = np.random.default_rng(12345)
        _mask = rng.integers(low=0, high=2, size=_shape)
        _val = rng.random() * 1e3
        app = CompositeCreatorApp()
        app._det_mask = _mask
        app.set_param_value("detector_mask_val", _val)
        _image = Dataset(np.random.random(_shape))
        _new_image = app._CompositeCreatorApp__apply_mask(_image)
        _delta = _new_image - _image
        self.assertTrue((_new_image.array[_mask == 1] == _val).all())
        self.assertTrue((_delta.array[_mask == 0] == 0).all())

    def test_apply_mask__with_mask_and_nan_mask_val(self):
        _shape = (50, 50)
        _val = np.nan
        rng = np.random.default_rng(12345)
        _mask = rng.integers(low=0, high=2, size=_shape)
        app = CompositeCreatorApp()
        app._det_mask = _mask
        app.set_param_value("detector_mask_val", _val)
        _image = Dataset(np.random.random(_shape))
        _new_image = app._CompositeCreatorApp__apply_mask(_image)
        self.assertTrue(np.isnan(_new_image[_mask == 1]).all())

    def test_multiprocessing_func(self):
        app = self.get_default_app()
        app._config["current_fname"] = self._hdf5_fnames[0]
        app._config["current_kwargs"] = dict(dataset="/entry/data/data", indices=(0,))
        _image = app.multiprocessing_func(0)
        self.assertTrue((_image == self._data[0]).all())

    def test_image_exists_check(self):
        _last_file = os.path.join(self._fname(20))
        app = self.get_default_app()
        app.run()
        self.assertTrue(app._image_exists_check(_last_file, timeout=0.1))

    def test_image_exists_check__no_file(self):
        app = CompositeCreatorApp()
        self.assertFalse(app._image_exists_check("", timeout=0.1))

    def test_image_exists_check__wrong_size(self):
        _last_file = os.path.join(self._path, "test_bg.npy")
        np.save(_last_file, np.ones((2, 2)))
        app = CompositeCreatorApp()
        self.assertFalse(app._image_exists_check(_last_file, timeout=0.1))

    def test_multiprocessing_carryon(self):
        app = self.get_default_app()
        self.assertTrue(app.multiprocessing_carryon())

    def test_multiprocessing_carryon__live(self):
        _last_file = self._fname(10)
        app = self.get_default_app()
        app.run()
        app.set_param_value("live_processing", True)
        app._config["current_fname"] = _last_file
        self.assertTrue(app.multiprocessing_carryon())

    def test_multiprocessing_carryon__no_file(self):
        _last_file = self._fname(80)
        app = self.get_default_app()
        app.run()
        app.set_param_value("live_processing", True)
        app._config["current_fname"] = _last_file
        self.assertFalse(app.multiprocessing_carryon())

    def test_multiprocessing_store_with_bg(self):
        _bg_fname = os.path.join(self._path, "bg.npy")
        np.save(_bg_fname, np.ones((10, 10)))
        app = self.get_default_app()
        app.set_param_value("use_bg_file", True)
        app.set_param_value("bg_file", _bg_fname)
        app.run()
        self.assertTrue((app._composite.image <= self._bgvalue).all())

    def test_store_args_for_read_image__hdf5(self):
        app = self.get_default_app()
        app.set_param_value("hdf5_key", "/entry/data/data")
        app.set_param_value("first_file", self._hdf5_fnames[0])
        app.set_param_value("last_file", Path())
        app._filelist.update()
        app._image_metadata.update(filename=self._hdf5_fnames[0])
        _index = 3
        app._store_args_for_read_image(_index)
        self.assertEqual(app._config["current_fname"], self._hdf5_fnames[0])
        self.assertEqual(app._config["current_kwargs"]["indices"], (_index,))
        self.assertEqual(app._config["current_kwargs"]["dataset"], "/entry/data/data")
        self.assertEqual(app._config["current_kwargs"]["binning"], 1)

    def test_store_args_for_read_image__npy(self):
        app = self.get_default_app()
        app._filelist.update()
        app._image_metadata.update()
        _index = 7
        app._store_args_for_read_image(_index)
        self.assertEqual(app._config["current_fname"], self._fname(_index))
        self.assertEqual(app._config["current_kwargs"]["binning"], 1)

    def test_multiprocessing_pre_cycle__no_files(self):
        app = CompositeCreatorApp()
        with self.assertRaises(UserConfigError):
            app.multiprocessing_pre_cycle(0)

    def test_multiprocessing_pre_cycle(self):
        app = CompositeCreatorApp()
        app.set_param_value("first_file", self._fname(0))
        app.set_param_value("last_file", self._fname(self._n_total - 1))
        app.prepare_run()
        app.multiprocessing_pre_cycle(0)
        # assert does not raise an error

    def test_multiprocessing_get_tasks__empty(self):
        app = CompositeCreatorApp()
        with self.assertRaises(KeyError):
            app.multiprocessing_get_tasks()

    def test_multiprocessing_get_tasks__tasks_defined(self):
        _tasks = [1, 2, 3, 4]
        app = CompositeCreatorApp()
        app._config["mp_tasks"] = _tasks
        _newtasks = app.multiprocessing_get_tasks()
        self.assertEqual(_tasks, _newtasks)

    def test_check_and_update_composite_image__no_composite_yet(self):
        app = self.get_default_app()
        app._CompositeCreatorApp__update_composite_image_params()
        self.assertIsInstance(app._composite.image, np.ndarray)

    def test_check_and_update_composite_image__redo(self):
        app = self.get_default_app()
        app._CompositeCreatorApp__update_composite_image_params()
        app._CompositeCreatorApp__update_composite_image_params()
        self.assertIsInstance(app._composite, CompositeImageManager)

    def test_check_and_update_composite_image__new_img_shape(self):
        app = self.get_default_app()
        app._CompositeCreatorApp__update_composite_image_params()
        _old_shape = app.composite.shape
        _img_shape2 = (self._img_shape[0] + 2, self._img_shape[1] + 2)
        _data2 = np.random.random((self._n_total,) + _img_shape2)
        for i in range(self._n_total):
            np.save(self._fname(i + self._n_total), _data2[i])
        app.set_param_value("first_file", self._fname(self._n_total))
        app.set_param_value("last_file", self._fname(2 * self._n_total - 1))
        app._image_metadata.update(filename=self._fname(self._n_total))
        app._CompositeCreatorApp__update_composite_image_params()
        _new_shape = app.composite.shape
        self.assertEqual(_old_shape[0] + 2 * self._ny, _new_shape[0])
        self.assertEqual(_old_shape[1] + 2 * self._nx, _new_shape[1])

    def test_check_and_update_composite_image__new_order(self):
        app = self.get_default_app()
        app._CompositeCreatorApp__update_composite_image_params()
        app.set_param_value("composite_nx", self._ny)
        app.set_param_value("composite_ny", self._nx)
        app._CompositeCreatorApp__update_composite_image_params()
        _new_shape = app.composite.shape
        _img_shape = app._image_metadata.final_shape
        _target_y = (_img_shape[0] + self._border) * self._nx - self._border
        _target_x = (_img_shape[1] + self._border) * self._ny - self._border
        self.assertEqual(_new_shape[0], _target_y)
        self.assertEqual(_new_shape[1], _target_x)

    def test_check_and_set_bg_file__with_fname(self):
        app = self.get_default_app()
        self.set_bg_params(app, self._fname(0))
        app._check_and_set_bg_file()
        _image = app._bg_image
        self.assertTrue(
            np.allclose(_image.array, self._data[0][app._image_metadata.roi])
        )

    def test_check_and_set_bg_file__with_hdf5_bg(self):
        app = self.get_default_app()
        self.set_bg_params(app, self._hdf5_fnames[0])
        app._check_and_set_bg_file()
        _image = app._bg_image
        self.assertTrue(
            np.allclose(_image.array, self._data[0][app._image_metadata.roi])
        )

    def test_check_and_set_bg_file__wrong_size(self):
        app = self.get_default_app()
        np.save(
            self._fname(999), np.zeros((self._img_shape[0] - 2, self._img_shape[1] - 2))
        )
        self.set_bg_params(app, self._fname(999))
        with self.assertRaises(UserConfigError):
            app._check_and_set_bg_file()

    def test_verify_total_number_of_images_in_composite__plain(self):
        app = self.get_default_app()
        app._CompositeCreatorApp__verify_number_of_images_fits_composite()
        # assert does not raise UserConfigError

    def test_verify_total_number_of_images_in_composite__nx_default(self):
        app = self.get_default_app()
        app.set_param_value("composite_nx", -1)
        app._CompositeCreatorApp__verify_number_of_images_fits_composite()
        self.assertEqual(app.get_param_value("composite_nx"), self._nx)

    def test_verify_total_number_of_images_in_composite__ny_default(self):
        app = self.get_default_app()
        app.set_param_value("composite_ny", -1)
        app._CompositeCreatorApp__verify_number_of_images_fits_composite()
        self.assertEqual(app.get_param_value("composite_ny"), self._ny)

    def test_verify_total_number_of_images_in_composite__too_small(self):
        app = self.get_default_app()
        app.set_param_value("composite_nx", 2)
        app.set_param_value("composite_ny", 2)
        with self.assertRaises(UserConfigError):
            app._CompositeCreatorApp__verify_number_of_images_fits_composite()

    def test_verify_total_number_of_images_in_composite__too_large(self):
        app = self.get_default_app()
        app.set_param_value("composite_nx", 20)
        app.set_param_value("composite_ny", 20)
        with self.assertRaises(UserConfigError):
            app._CompositeCreatorApp__verify_number_of_images_fits_composite()

    def test_get_detector_mask__no_file(self):
        app = CompositeCreatorApp()
        app._store_detector_mask()
        _mask = app._det_mask
        self.assertIsNone(_mask)

    def test_get_detector_mask__wrong_file(self):
        app = CompositeCreatorApp()
        with open(self._maskfile, "w") as f:
            f.write("this is not a numpy file.")
        app._store_detector_mask()
        _mask = app._det_mask
        self.assertIsNone(_mask)

    def test_get_detector_mask__with_binning(self):
        app = CompositeCreatorApp()
        app.set_param_value("binning", 2)
        app.set_param_value("use_detector_mask", True)
        app.set_param_value("detector_mask_file", self._maskfile)
        app._store_detector_mask()
        _mask = app._det_mask
        _binned_shape = (self._img_shape[0] // 2, self._img_shape[1] // 2)
        self.assertEqual(_mask.shape, _binned_shape)

    def test_get_detector_mask__with_roi(self):
        app = CompositeCreatorApp()
        app.set_param_value("roi_xlow", 5)
        app.set_param_value("use_roi", True)
        app.set_param_value("first_file", self._hdf5_fnames[0])
        app.set_param_value("use_detector_mask", True)
        app.set_param_value("detector_mask_file", self._maskfile)
        app._image_metadata.update(filename=self._hdf5_fnames[0])
        app._store_detector_mask()
        _mask = app._det_mask
        _target_shape = (self._img_shape[0], self._img_shape[1] - 5)
        self.assertEqual(_mask.shape, _target_shape)

    def test_get_detector_mask__with_roi_and_binning(self):
        app = CompositeCreatorApp()
        app.set_param_value("roi_xlow", 4)
        app.set_param_value("use_roi", True)
        app.set_param_value("binning", 2)
        app.set_param_value("first_file", self._hdf5_fnames[0])
        app.set_param_value("use_detector_mask", True)
        app.set_param_value("detector_mask_file", self._maskfile)
        app._image_metadata.update(filename=self._hdf5_fnames[0])
        app._store_detector_mask()
        _mask = app._det_mask
        self.assertEqual(_mask.shape, app._image_metadata.final_shape)

    def test_prepare_run__plain(self):
        app = self.get_default_app()
        app.prepare_run()
        # assert does not raise an error

    def test_prepare_run__with_bg_file(self):
        app = self.get_default_app()
        self.set_bg_params(app, self._fname(0))
        app.prepare_run()
        self.assertIsInstance(app._bg_image, np.ndarray)

    def test_prepare_run__with_thresholds(self):
        _thresh_low = -12
        _thresh_high = 42
        app = self.get_default_app()
        app.set_param_value("use_thresholds", True)
        app.set_param_value("threshold_low", _thresh_low)
        app.set_param_value("threshold_high", _thresh_high)
        app.prepare_run()
        self.assertEqual(app._composite.get_param_value("threshold_low"), _thresh_low)
        self.assertEqual(app._composite.get_param_value("threshold_high"), _thresh_high)

    def test_prepare_run__slave_mode(self):
        app = self.get_default_app()
        app.slave_mode = True
        app.prepare_run()
        self.assertIsNone(app._composite)

    def test_multiprocessing_pre_run(self):
        app = self.get_default_app()
        app.multiprocessing_pre_run()
        self.assertTrue(app._config["run_prepared"])
        self.assertIsNotNone(app._config["mp_tasks"])


if __name__ == "__main__":
    unittest.main()
