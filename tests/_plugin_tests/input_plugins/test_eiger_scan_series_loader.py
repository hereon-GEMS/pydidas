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

import os
import unittest
import tempfile
import shutil
import pickle

import numpy as np
import h5py

from pydidas.core import UserConfigError, Parameter, Dataset
from pydidas.core.utils import get_random_string
from pydidas.contexts import ScanContext
from pydidas.plugins import PluginCollection, BasePlugin


COLLECTION = PluginCollection()
SCAN = ScanContext()


class TestEigerScanSeriesLoader(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._path = tempfile.mkdtemp()
        cls._img_shape = (10, 10)
        cls._n_per_file = 13
        cls._n_files = 11
        cls._n = cls._n_files * cls._n_per_file
        cls._fname_i0 = 2
        cls._params = {
            "eiger_dir": "eiger9m",
            "eiger_filename_suffix": "_data.h5",
            "hdf5_key": "/entry/data/data",
            "images_per_file": -1,
        }
        cls._data = np.repeat(
            np.arange(cls._n, dtype=np.uint16), np.prod(cls._img_shape)
        ).reshape((cls._n,) + cls._img_shape)

        cls._hdf5_fnames = []
        for i in range(cls._n_files):
            _dir = os.path.join(
                cls._path, f"test_{i + cls._fname_i0:05d}", cls._params["eiger_dir"]
            )
            os.makedirs(_dir)
            _fname = os.path.join(
                _dir,
                f"test_{i + cls._fname_i0:05d}" + cls._params["eiger_filename_suffix"],
            )
            cls._hdf5_fnames.append(_fname)
            _slice = slice(i * cls._n_per_file, (i + 1) * cls._n_per_file, 1)
            with h5py.File(_fname, "w") as f:
                f[cls._params["hdf5_key"]] = cls._data[_slice]

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls._path)

    def setUp(self):
        SCAN.restore_all_defaults(True)
        SCAN.set_param_value("scan_name_pattern", "test_#####")
        SCAN.set_param_value("scan_base_directory", self._path)
        SCAN.set_param_value("scan_start_index", self._fname_i0)

    def tearDown(self):
        SCAN.restore_all_defaults(True)

    def create_standard_plugin(self):
        plugin = COLLECTION.get_plugin_by_name("EigerScanSeriesLoader")()
        for _key, _val in self._params.items():
            plugin.set_param_value(_key, _val)
        return plugin

    def get_index_in_file(self, index):
        return index % self._n_per_file

    def test_creation(self):
        plugin = COLLECTION.get_plugin_by_name("EigerScanSeriesLoader")()
        self.assertIsInstance(plugin, BasePlugin)

    def test_pre_execute__no_input(self):
        plugin = COLLECTION.get_plugin_by_name("EigerScanSeriesLoader")()
        with self.assertRaises(UserConfigError):
            plugin.pre_execute()

    def test_pre_execute__simple(self):
        plugin = self.create_standard_plugin()
        plugin.pre_execute()
        self.assertEqual(plugin._image_metadata.final_shape, self._img_shape)

    def test_pre_execute__no_images_per_file_set(self):
        plugin = self.create_standard_plugin()
        plugin.set_param_value("images_per_file", -1)
        plugin.pre_execute()
        self.assertEqual(plugin._image_metadata.final_shape, self._img_shape)
        self.assertEqual(plugin._config["images_per_file"], self._n_per_file)

    def test_execute__no_input(self):
        plugin = COLLECTION.get_plugin_by_name("EigerScanSeriesLoader")(
            images_per_file=1
        )
        with self.assertRaises(UserConfigError):
            plugin.execute(0)

    def test_execute__simple(self):
        plugin = self.create_standard_plugin()
        _index = 0
        plugin.pre_execute()
        _data, kwargs = plugin.execute(_index)
        self.assertTrue((_data == _index).all())
        self.assertEqual(kwargs["frame"], self.get_index_in_file(_index))
        self.assertEqual(_data.metadata["frame"], [self.get_index_in_file(_index)])

    def test_execute__with_roi(self):
        plugin = self.create_standard_plugin()
        plugin.set_param_value("use_roi", True)
        plugin.set_param_value("roi_yhigh", 5)
        _index = 2
        plugin.pre_execute()
        _data, kwargs = plugin.execute(_index)
        self.assertTrue((_data == _index).all())
        self.assertEqual(kwargs["frame"], self.get_index_in_file(_index))
        self.assertEqual(_data.metadata["frame"], [self.get_index_in_file(_index)])
        self.assertEqual(
            _data.shape, (plugin.get_param_value("roi_yhigh"), self._img_shape[1])
        )

    def test_execute__get_all_frames(self):
        plugin = self.create_standard_plugin()
        plugin.pre_execute()
        for _index in range(self._n):
            _data, kwargs = plugin.execute(_index)
            self.assertTrue((_data == _index).all())
            self.assertEqual(kwargs["frame"], self.get_index_in_file(_index))
            self.assertEqual(_data.metadata["frame"], [self.get_index_in_file(_index)])

    def test_pickle(self):
        plugin = self.create_standard_plugin()
        _new_params = {get_random_string(6): get_random_string(12) for i in range(7)}
        for _key, _val in _new_params.items():
            plugin.add_param(Parameter(_key, str, _val))
        plugin2 = pickle.loads(pickle.dumps(plugin))
        for _key in plugin.params:
            self.assertEqual(
                plugin.get_param_value(_key), plugin2.get_param_value(_key)
            )

    def test_get_frame__no_preexec(self):
        plugin = self.create_standard_plugin()
        with self.assertRaises(UserConfigError):
            plugin.get_frame(0)

    def test_get_frame__w_preexec(self):
        plugin = self.create_standard_plugin()
        plugin.pre_execute()
        _data, kwargs = plugin.get_frame(0)
        self.assertIsInstance(_data, Dataset)
        self.assertTrue(np.allclose(_data, 0))

    def test_get_filename(self):
        _index = 5
        plugin = self.create_standard_plugin()
        plugin.pre_execute()
        _fname = plugin.get_filename(_index * self._n_per_file)
        self.assertEqual(_fname, self._hdf5_fnames[_index])


if __name__ == "__main__":
    unittest.main()
