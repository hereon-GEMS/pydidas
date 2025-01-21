# This file is part of pydidas.
#
# Copyright 2024 - 2025, Helmholtz-Zentrum Hereon
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
__copyright__ = "Copyright 2024 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"


import multiprocessing as mp
import os
import random
import shutil
import tempfile
import time
import unittest

import h5py
import numpy as np

from pydidas.apps.directory_spy_app import DirectorySpyApp
from pydidas.apps.parsers import directory_spy_app_parser
from pydidas.core import FileReadError, UserConfigError, get_generic_parameter
from pydidas.core.utils import get_random_string


class TestDirectorySpyApp(unittest.TestCase):
    def setUp(self):
        self._path = tempfile.mkdtemp()
        self._pname = "test_12345_#####_suffix.npy"
        _full_path = os.path.join(self._path, self._pname)
        self._glob_str = self._pname.replace("#####", "*")
        self._full_glob_str = _full_path.replace("#####", "*")
        self._shape = (20, 20)
        self._mask = np.asarray(
            [
                random.choice([True, False])
                for _ in range(self._shape[0] * self._shape[1])
            ]
        ).reshape(self._shape)

    def tearDown(self):
        shutil.rmtree(self._path)
        DirectorySpyApp.parse_func = directory_spy_app_parser

    def get_test_image(self, shape=None):
        if shape is None:
            shape = self._shape
        return np.random.random(shape)

    def create_pattern_files(self, pattern=None, n=20):
        if pattern is None:
            pattern = self._pname
        _len_pattern = pattern.count("#")
        pattern = pattern.replace("#" * _len_pattern, "{:0" + str(_len_pattern) + "d}")
        _names = []
        for _index in range(n):
            _data = np.random.random(self._shape)
            _fpath = os.path.join(self._path, pattern.format(_index))
            np.save(_fpath, _data)
            _names.append(_fpath)
            time.sleep(0.005)
        return _names

    def create_temp_mask_file(self):
        self._mask_fname = os.path.join(self._path, "mask.npy")
        np.save(self._mask_fname, self._mask)

    def create_default_app(self):
        app = DirectorySpyApp()
        app.set_param_value("scan_for_all", False)
        app.set_param_value("directory_path", self._path)
        app.set_param_value("filename_pattern", "names_with_###_patterns.tif")
        app.prepare_run()
        app._det_mask = np.zeros(self._shape)
        return app

    def create_hdf5_image(self):
        _fname = self.create_pattern_files(n=1)[0].replace("npy", "h5")
        _dset = "/entry/nodata/data"
        _n = 42
        _data = np.zeros((_n,) + self._shape)
        with h5py.File(_fname, "w") as f:
            f[_dset] = _data
        return _fname, _dset, _data.shape

    def test_creation(self):
        app = DirectorySpyApp()
        self.assertIsInstance(app, DirectorySpyApp)

    def test_testcase_create_pattern_files(self):
        _name = "something_432_####_666.npy"
        _n = 25
        _names = self.create_pattern_files(_name, _n)
        for _index in range(_n):
            _fname = os.path.join(self._path, _name.replace("####", f"{_index:04d}"))
            self.assertTrue(os.path.isfile(_fname))
            self.assertEqual(_fname, _names[_index])

    def test_creation_with_args(self):
        _scan_for_all = get_generic_parameter("scan_for_all")
        _scan_for_all.value = True
        app = DirectorySpyApp(_scan_for_all)
        self.assertTrue(app.get_param_value("scan_for_all"))

    def test_creation_with_cmdargs(self):
        DirectorySpyApp.parse_func = lambda x: {"scan_for_all": True}
        app = DirectorySpyApp()
        self.assertTrue(app.get_param_value("scan_for_all"))

    def test_reset_runtime_vars(self):
        app = DirectorySpyApp()
        app._shared_array = 42
        app._index = np.pi
        app.reset_runtime_vars()
        self.assertIsNone(app._shared_array)
        self.assertEqual(app._index, -1)

    def test_apply_mask__no_mask(self):
        _param = get_generic_parameter("use_detector_mask")
        _param.value = False
        _image = self.get_test_image()
        app = DirectorySpyApp(_param)
        app._det_mask = None
        _new_image = app._apply_mask(_image)
        self.assertTrue(np.allclose(_image, _new_image))

    def test_apply_mask__with_mask(self):
        _val = 42
        app = DirectorySpyApp()
        app._det_mask = self._mask
        app.set_param_value("detector_mask_val", _val)
        _image = self.get_test_image()
        _new_image = app._apply_mask(_image)
        self.assertTrue(np.allclose(_new_image[self._mask], _val))

    def test_get_detector_mask__no_mask(self):
        _param = get_generic_parameter("use_detector_mask")
        _param.value = False
        app = DirectorySpyApp(_param)
        _mask = app._get_detector_mask()
        self.assertIsNone(_mask)

    def test_get_detector_mask__with_mask(self):
        self.create_temp_mask_file()
        app = DirectorySpyApp()
        app.set_param_value("use_detector_mask", True)
        app.set_param_value("detector_mask_file", self._mask_fname)
        _mask = app._get_detector_mask()
        self.assertTrue((_mask == self._mask).all())

    def test_define_path_and_name__scan_for_all(self):
        app = DirectorySpyApp()
        app.set_param_value("scan_for_all", True)
        app.set_param_value("directory_path", self._path)
        app.define_path_and_name()
        self.assertEqual(self._path, app._config["path"])
        self.assertEqual(app._fname(0), "")

    def test_find_current_index__missing_inbetween(self):
        _num = 21
        _names = self.create_pattern_files(n=_num)
        os.remove(_names[-3])
        os.remove(_names[-7])
        app = DirectorySpyApp()
        app._config["path"] = self._path
        app._config["glob_pattern"] = self._glob_str
        app._DirectorySpyApp__find_current_index()
        self.assertEqual(app._index, _num - 1)

    def test_find_current_index__missing_at_start(self):
        _num = 21
        _names = self.create_pattern_files(n=_num)
        for _ in range(4):
            _name = _names.pop(0)
            os.remove(_name)
        app = DirectorySpyApp()
        app._config["path"] = self._path
        app._config["glob_pattern"] = self._glob_str
        app._DirectorySpyApp__find_current_index()
        self.assertEqual(app._index, 20)

    def test_find_current_index__simple(self):
        _num = 21
        _ = self.create_pattern_files(n=_num)
        app = DirectorySpyApp()
        app._config["path"] = self._path
        app._config["glob_pattern"] = self._glob_str
        app._DirectorySpyApp__find_current_index()
        self.assertEqual(app._index, _num - 1)

    def test_find_current_index__empty(self):
        app = DirectorySpyApp()
        app._index = None
        app._config["path"] = self._path
        app._config["glob_pattern"] = "*"
        app._DirectorySpyApp__find_current_index()
        self.assertEqual(app._index, -1)

    def test_find_latest_file_of_pattern__empty(self):
        app = DirectorySpyApp()
        app._config["path"] = self._path
        app._config["glob_pattern"] = self._glob_str
        app._fname = lambda x: self._glob_str.replace("*", "{:05d}").format(x)
        _ret = app._DirectorySpyApp__check_for_new_file_of_pattern()
        self.assertIsNone(app._config["latest_file"])
        self.assertIsNone(app._config["2nd_latest_file"])
        self.assertFalse(_ret)

    def test_find_latest_file_of_pattern__single_file(self):
        _names = self.create_pattern_files(n=1)
        app = DirectorySpyApp()
        app._config["path"] = self._path
        app._config["glob_pattern"] = self._glob_str
        app._fname = lambda x: self._full_glob_str.replace("*", "{:05d}").format(x)
        _ret = app._DirectorySpyApp__check_for_new_file_of_pattern()
        self.assertEqual(app._config["latest_file"], _names[0])
        self.assertIsNone(app._config["2nd_latest_file"])
        self.assertTrue(_ret)

    def test_find_latest_file_of_pattern__multiple_files(self):
        _names = self.create_pattern_files(n=32)
        app = DirectorySpyApp()
        app._config["path"] = self._path
        app._config["glob_pattern"] = self._glob_str
        app._fname = lambda x: self._full_glob_str.replace("*", "{:05d}").format(x)
        _ret = app._DirectorySpyApp__check_for_new_file_of_pattern()
        self.assertEqual(app._config["latest_file"], _names[-1])
        self.assertEqual(app._config["2nd_latest_file"], _names[-2])
        self.assertTrue(_ret)

    def test_find_latest_file_of_pattern__multiple_files_not_starting_with_0(self):
        _names = self.create_pattern_files(n=32)
        for _ in range(4):
            _name = _names.pop(0)
            os.remove(_name)
        app = DirectorySpyApp()
        app._config["path"] = self._path
        app._config["glob_pattern"] = self._glob_str
        app._fname = lambda x: self._full_glob_str.replace("*", "{:05d}").format(x)
        _ret = app._DirectorySpyApp__check_for_new_file_of_pattern()
        self.assertEqual(app._config["latest_file"], _names[-1])
        self.assertEqual(app._config["2nd_latest_file"], _names[-2])
        self.assertTrue(_ret)

    def test_find_latest_file_of_pattern__same_files_again(self):
        _ = self.create_pattern_files(n=32)
        app = DirectorySpyApp()
        app._config["path"] = self._path
        app._config["glob_pattern"] = self._glob_str
        app._fname = lambda x: self._full_glob_str.replace("*", "{:05d}").format(x)
        _ret = app._DirectorySpyApp__check_for_new_file_of_pattern()
        self.assertTrue(_ret)
        _ret = app._DirectorySpyApp__check_for_new_file_of_pattern()
        self.assertFalse(_ret)

    def test_find_latest_file_of_pattern__same_files_with_changed_size(self):
        _names = self.create_pattern_files(n=32)
        app = DirectorySpyApp()
        app._config["path"] = self._path
        app._config["glob_pattern"] = self._glob_str
        app._fname = lambda x: self._full_glob_str.replace("*", "{:05d}").format(x)
        _ret = app._DirectorySpyApp__check_for_new_file_of_pattern()
        self.assertTrue(_ret)
        _ret = app._DirectorySpyApp__check_for_new_file_of_pattern()
        self.assertFalse(_ret)
        with open(_names[-1], "w") as f:
            f.write("other content")
        _ret = app._DirectorySpyApp__check_for_new_file_of_pattern()
        self.assertTrue(_ret)

    def test_find_latest_file_of_pattern__missing_files(self):
        _index = 12
        _names = self.create_pattern_files(n=32)
        os.remove(_names[_index])
        app = DirectorySpyApp()
        app._config["path"] = self._path
        app._config["glob_pattern"] = self._glob_str
        app._fname = lambda x: self._full_glob_str.replace("*", "{:05d}").format(x)
        app._DirectorySpyApp__check_for_new_file_of_pattern()
        self.assertEqual(app._config["latest_file"], _names[_index - 1])
        self.assertEqual(app._config["2nd_latest_file"], _names[_index - 2])

    def test_find_latest_file__empty(self):
        app = DirectorySpyApp()
        app._config["path"] = self._path
        _ret = app._DirectorySpyApp__check_for_new_file()
        self.assertIsNone(app._config["latest_file"])
        self.assertIsNone(app._config["2nd_latest_file"])
        self.assertFalse(_ret)

    def test_find_latest_file__no_files_but_dirs(self):
        os.makedirs(os.path.join(self._path, "dir1"))
        os.makedirs(os.path.join(self._path, "dir2"))
        app = DirectorySpyApp()
        app._config["path"] = self._path
        _ret = app._DirectorySpyApp__check_for_new_file()
        self.assertIsNone(app._config["latest_file"])
        self.assertIsNone(app._config["2nd_latest_file"])
        self.assertFalse(_ret)

    def test_find_latest_file_single_file(self):
        _names = self.create_pattern_files(n=1)
        app = DirectorySpyApp()
        app._config["path"] = self._path
        _ret = app._DirectorySpyApp__check_for_new_file()
        self.assertEqual(app._config["latest_file"], _names[0])
        self.assertIsNone(app._config["2nd_latest_file"])
        self.assertTrue(_ret)

    def test_find_latest_file__multiple_files(self):
        _names = self.create_pattern_files(n=32)
        app = DirectorySpyApp()
        app._config["path"] = self._path
        _ret = app._DirectorySpyApp__check_for_new_file()
        self.assertEqual(app._config["latest_file"], _names[-1])
        self.assertEqual(app._config["2nd_latest_file"], _names[-2])
        self.assertTrue(_ret)

    def test_find_latest_file__same_files_again(self):
        _ = self.create_pattern_files(n=32)
        app = DirectorySpyApp()
        app._config["path"] = self._path
        _ret = app._DirectorySpyApp__check_for_new_file()
        self.assertTrue(_ret)
        _ret = app._DirectorySpyApp__check_for_new_file()
        self.assertFalse(_ret)

    def test_initialize_shared_memory(self):
        app = DirectorySpyApp()
        app.initialize_shared_memory()
        for _key in ["flag", "width", "height"]:
            self.assertIsInstance(
                app._config["shared_memory"][_key], mp.sharedctypes.Synchronized
            )
        self.assertIsInstance(
            app._config["shared_memory"]["array"], mp.sharedctypes.SynchronizedArray
        )

    def test_initialize_arrays_from_shared_memory(self):
        app = DirectorySpyApp()
        app.initialize_shared_memory()
        app._DirectorySpyApp__initialize_array_from_shared_memory()
        self.assertIsInstance(app._shared_array, np.ndarray)
        self.assertEqual(app._shared_array.shape, (10000, 10000))

    def test_load_bg_file__simple(self):
        _fname = self.create_pattern_files(n=1)[0]
        _data = np.load(_fname)
        app = DirectorySpyApp()
        app.set_param_value("bg_file", _fname)
        app._det_mask = np.zeros(self._shape)
        app._load_bg_file()
        self.assertTrue((_data == app._bg_image).all())

    def test_load_bg_file__no_such_file(self):
        _fname = self.create_pattern_files(n=1)[0]
        os.remove(_fname)
        app = DirectorySpyApp()
        app.set_param_value("bg_file", _fname)
        with self.assertRaises(UserConfigError):
            app._load_bg_file()

    def test_load_bg_file__hdf5file(self):
        _fname = self.create_pattern_files(n=1)[0]
        _data = np.load(_fname)
        _dset = "entry/nodata/data"
        with h5py.File(_fname.replace("npy", "h5"), "w") as f:
            f[_dset] = _data[None, :, :]
        app = DirectorySpyApp()
        app.set_param_value("bg_file", _fname.replace("npy", "h5"))
        app.set_param_value("bg_hdf5_key", _dset)
        app._det_mask = np.zeros(self._shape)
        app._load_bg_file()
        self.assertTrue((_data == app._bg_image).all())

    def test_load_bg_file__wrong_shape(self):
        _fname = self.create_pattern_files(n=1)[0]
        np.save(_fname, np.zeros((10, 10, 10)))
        app = DirectorySpyApp()
        app.set_param_value("bg_file", _fname)
        with self.assertRaises(UserConfigError):
            app._load_bg_file()

    def test_define_path_and_name__with_scan_for_all(self):
        app = DirectorySpyApp()
        app.set_param_value("scan_for_all", True)
        app.set_param_value("directory_path", self._path)
        app.define_path_and_name()
        self.assertEqual(app._config["path"], self._path)

    def test_define_path_and_name__with_pattern_no_wildcard(self):
        app = DirectorySpyApp()
        app.set_param_value("scan_for_all", False)
        _pattern = os.path.join(self._path, "names_with_no_pattern123.tif")
        app.set_param_value("filename_pattern", _pattern)
        with self.assertRaises(UserConfigError):
            app.define_path_and_name()

    def test_define_path_and_name__with_pattern_multiple_wildcard(self):
        app = DirectorySpyApp()
        app.set_param_value("scan_for_all", False)
        _pattern = os.path.join(self._path, "names_with_###_patterns_###.tif")
        app.set_param_value("filename_pattern", _pattern)
        with self.assertRaises(UserConfigError):
            app.define_path_and_name()

    def test_define_path_and_name__with_pattern_correct(self):
        app = self.create_default_app()
        _pattern = str(app.get_param_value("filename_pattern"))
        app.define_path_and_name()
        self.assertEqual(app._config["glob_pattern"], _pattern.replace("###", "*"))
        self.assertEqual(
            app._fname(42),
            os.path.join(app._config["path"], _pattern).replace("###", "042"),
        )
        self.assertEqual(app._config["path"], self._path)

    def test_multiprocessing_carryon(self):
        app = self.create_default_app()
        app.prepare_run()
        self.assertFalse(app.multiprocessing_carryon())

    def test_prepare_run__master(self):
        app = self.create_default_app()
        app.prepare_run()
        self.assertIsNotNone(app._fname(42))
        self.assertEqual(app._config["path"], self._path)
        self.assertIsInstance(app._shared_array, np.ndarray)
        self.assertEqual(app._shared_array.shape, (10000, 10000))

    def test_prepare_run__as_clone(self):
        app = self.create_default_app()
        app.prepare_run()
        app_clone = app.copy(clone_mode=True)
        app_clone.prepare_run()
        for _key in ["flag", "width", "height", "array"]:
            self.assertEqual(
                app._config["shared_memory"][_key],
                app_clone._config["shared_memory"][_key],
            )

    def test_multiprocessing_pre_run(self):
        app = self.create_default_app()
        app.multiprocessing_pre_run()
        # these tests are the same as for the prepare_run method:
        self.assertIsNotNone(app._fname(42))
        self.assertEqual(app._config["path"], self._path)
        self.assertIsInstance(app._shared_array, np.ndarray)
        self.assertEqual(app._shared_array.shape, (10000, 10000))

    def test_multiprocessing_post_run(self):
        app = self.create_default_app()
        app.multiprocessing_post_run()
        # assert does not raise an Exception

    def test_multiprocessing_get_tasks(self):
        app = self.create_default_app()
        self.assertEqual(app.multiprocessing_get_tasks(), [])

    def test_multiprocessing_pre_cycle(self):
        app = self.create_default_app()
        app.multiprocessing_pre_cycle(0)
        # assert does not raise an Exception

    def test_update_hdf5_metadata(self):
        _fname, _dset, _shape = self.create_hdf5_image()
        app = self.create_default_app()
        app.set_param_value("hdf5_key", _dset)
        app._DirectorySpyApp__update_hdf5_metadata(_fname)
        _meta = app._DirectorySpyApp__read_image_meta
        self.assertEqual(_meta["indices"], (_shape[0] - 1,))
        self.assertEqual(_meta["dataset"], _dset)

    def test_update_hdf5_metadata__w_slice_ax(self):
        _fname, _dset, _shape = self.create_hdf5_image()
        app = self.create_default_app()
        for _ax in [1, 2]:
            with self.subTest(axis=_ax):
                app.set_param_value("hdf5_key", _dset)
                app.set_param_value("hdf5_slicing_axis", _ax)
                app._DirectorySpyApp__update_hdf5_metadata(_fname)
                _meta = app._DirectorySpyApp__read_image_meta
                self.assertEqual(_meta["indices"], (None,) * _ax + (_shape[1] - 1,))
                self.assertEqual(_meta["dataset"], _dset)

    def test_update_hdf5_metadata__no_slice_ax(self):
        _fname, _dset, _shape = self.create_hdf5_image()
        app = self.create_default_app()
        app.set_param_value("hdf5_key", _dset)
        app.set_param_value("hdf5_slicing_axis", None)
        app._DirectorySpyApp__update_hdf5_metadata(_fname)
        _meta = app._DirectorySpyApp__read_image_meta
        self.assertEqual(_meta["indices"], None)
        self.assertEqual(_meta["dataset"], _dset)

    def test_get_image__simple_image(self):
        app = self.create_default_app()
        _fname = self.create_pattern_files(n=1)[0]
        _data = np.load(_fname)
        _image = app.get_image(_fname)
        self.assertTrue((_data == _image).all())

    def test_get_image__high_dim_image(self):
        app = self.create_default_app()
        _fname = self.create_pattern_files(n=1)[0]
        np.save(_fname, np.zeros((10, 10, 10)))
        with self.assertRaises(UserConfigError):
            app.get_image(_fname)

    def test_get_image__hdf5_image(self):
        _fname, _dset, _shape = self.create_hdf5_image()
        app = self.create_default_app()
        app.set_param_value("hdf5_key", _dset)
        with h5py.File(_fname, "r") as f:
            _data = f[_dset][()]
        _image = app.get_image(_fname)
        self.assertTrue((_data[-1] == _image).all())

    def test_store_image_in_shared_memory(self):
        app = self.create_default_app()
        app.prepare_run()
        _width = 27
        _height = 42
        _image = np.random.random((_height, _width))
        app._DirectorySpyApp__store_image_in_shared_memory(_image)
        self.assertEqual(app._config["shared_memory"]["width"].value, _width)
        self.assertEqual(app._config["shared_memory"]["height"].value, _height)
        self.assertTrue(np.allclose(app._shared_array[:_height, :_width], _image))

    def test_multiprocessing_func__no_files(self):
        app = self.create_default_app()
        with self.assertRaises(UserConfigError):
            app.multiprocessing_func(None)

    def test_multiprocessing_func__last_file_not_readable(self):
        _names = self.create_pattern_files(n=2)
        app = self.create_default_app()
        app._config["latest_file"] = _names[1]
        app._config["2nd_latest_file"] = _names[0]
        with open(_names[1], "w") as f:
            f.write("no image file")
        _index, _fname = app.multiprocessing_func(None)
        self.assertEqual(_fname, _names[0])
        self.assertEqual(app._config["shared_memory"]["width"].value, self._shape[1])
        self.assertEqual(app._config["shared_memory"]["height"].value, self._shape[0])
        self.assertTrue(
            np.allclose(
                app._shared_array[: self._shape[0], : self._shape[1]],
                np.load(_names[0]),
            )
        )

    def test_multiprocessing_func__both_files_not_readable(self):
        _names = self.create_pattern_files(n=2)
        app = self.create_default_app()
        app._config["latest_file"] = _names[1]
        app._config["2nd_latest_file"] = _names[0]
        for _name in _names:
            with open(_name, "w") as f:
                f.write("no image file")
        with self.assertRaises(FileReadError):
            app.multiprocessing_func(None)

    def test_multiprocessing_func__both_files_readable(self):
        _names = self.create_pattern_files(n=2)
        app = self.create_default_app()
        app._config["latest_file"] = _names[1]
        app._config["2nd_latest_file"] = _names[0]
        _index, _fname = app.multiprocessing_func(None)
        self.assertEqual(_fname, _names[1])
        self.assertEqual(app._config["shared_memory"]["width"].value, self._shape[1])
        self.assertEqual(app._config["shared_memory"]["height"].value, self._shape[0])
        self.assertTrue(
            np.allclose(
                app._shared_array[: self._shape[0], : self._shape[1]],
                np.load(_names[1]),
            )
        )

    def test_multiprocessing_func__with_mask(self):
        _names = self.create_pattern_files(n=2)
        self.create_temp_mask_file()
        app = self.create_default_app()
        app._det_mask = self._mask
        app._config["latest_file"] = _names[1]
        _index, _fname = app.multiprocessing_func(None)
        _arr = app._shared_array[: self._shape[0], : self._shape[1]]
        self.assertTrue((_arr[self._mask] == 0).all())

    def test_multiprocessing_func__with_bg_file(self):
        _bg = np.ones(self._shape)
        _bg_fname = os.path.join(self._path, "bg.npy")
        np.save(_bg_fname, _bg)
        _names = self.create_pattern_files(n=2)
        app = self.create_default_app()
        app.set_param_value("use_bg_file", True)
        app.set_param_value("use_detector_mask", False)
        app.set_param_value("bg_file", _bg_fname)
        app._config["latest_file"] = _names[1]
        app.prepare_run()
        app._det_mask = self._mask
        _index, _fname = app.multiprocessing_func(None)
        _arr = app._shared_array[: self._shape[0], : self._shape[1]]
        self.assertTrue((_arr[self._mask] <= 0).all())

    def test_multiprocessing_func__with_disabled_bg_file(self):
        _bg = np.ones(self._shape)
        _bg_fname = os.path.join(self._path, "bg.npy")
        np.save(_bg_fname, _bg)
        _names = self.create_pattern_files(n=2)
        app = self.create_default_app()
        app.set_param_value("bg_file", _bg_fname)
        app._config["latest_file"] = _names[1]
        _index, _fname = app.multiprocessing_func(None)
        _arr = app._shared_array[: self._shape[0], : self._shape[1]]
        self.assertTrue((_arr[self._mask] >= 0).all())

    def test_multiprocessing_store_results(self):
        _names = self.create_pattern_files(n=2)
        app = self.create_default_app()
        app._config["latest_file"] = _names[1]
        app._config["2nd_latest_file"] = _names[0]
        _index, _fname = app.multiprocessing_func(None)
        app.multiprocessing_store_results(_index, _fname)
        self.assertTrue(
            np.allclose(app._DirectorySpyApp__current_image, np.load(_names[1]))
        )
        self.assertEqual(app._DirectorySpyApp__current_fname, _names[1])

    def test_image_property(self):
        app = self.create_default_app()
        _data = np.random.random(self._shape)
        app._DirectorySpyApp__current_image = _data
        self.assertTrue(np.allclose(app.image, _data))

    def test_filename_property(self):
        _name = get_random_string(12)
        app = self.create_default_app()
        app._DirectorySpyApp__current_fname = _name
        self.assertEqual(_name, app.filename)


if __name__ == "__main__":
    unittest.main()
