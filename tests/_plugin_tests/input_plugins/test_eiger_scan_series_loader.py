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

from pydidas.core import AppConfigError, Parameter
from pydidas.core.utils import get_random_string
from pydidas.plugins import PluginCollection, BasePlugin


COLLECTION = PluginCollection()


class TestEigerScanSeriesLoader(unittest.TestCase):
    def setUp(self):
        self._path = tempfile.mkdtemp()
        self._img_shape = (10, 10)
        self._n_per_file = 13
        self._n_files = 11
        self._fname_i0 = 2
        self._pattern = "test_{:05d}"
        self._suffix = "_data.h5"
        self._eiger_key = "eiger9m"
        self._n = self._n_files * self._n_per_file
        self._hdf5key = "/entry/data/data"
        self._data = np.zeros(((self._n,) + self._img_shape), dtype=np.uint16)
        for index in range(self._n):
            self._data[index] = index

        self._hdf5_fnames = []
        for i in range(self._n_files):
            _dir = os.path.join(
                self._path, self._pattern.format(i + self._fname_i0), self._eiger_key
            )
            os.makedirs(_dir)
            _fname = os.path.join(
                _dir, self._pattern.format(i + self._fname_i0) + self._suffix
            )
            self._hdf5_fnames.append(_fname)
            _slice = slice(i * self._n_per_file, (i + 1) * self._n_per_file, 1)
            with h5py.File(_fname, "w") as f:
                f[self._hdf5key] = self._data[_slice]

    def tearDown(self):
        shutil.rmtree(self._path)

    def create_plugin_with_filelist(self):
        plugin = COLLECTION.get_plugin_by_name("EigerScanSeriesLoader")()
        plugin.set_param_value("directory_path", self._path)
        plugin.set_param_value("filename_pattern", "test_#####")
        plugin.set_param_value("eiger_key", self._eiger_key)
        plugin.set_param_value("filename_suffix", self._suffix)
        plugin.set_param_value("first_index", self._fname_i0)
        plugin.set_param_value("hdf5_key", self._hdf5key)
        return plugin

    def get_index_in_file(self, index):
        return index % self._n_per_file

    def test_creation(self):
        plugin = COLLECTION.get_plugin_by_name("EigerScanSeriesLoader")()
        self.assertIsInstance(plugin, BasePlugin)

    def test_pre_execute__no_input(self):
        plugin = COLLECTION.get_plugin_by_name("EigerScanSeriesLoader")()
        with self.assertRaises(AppConfigError):
            plugin.pre_execute()

    def test_pre_execute__simple(self):
        plugin = self.create_plugin_with_filelist()
        plugin.pre_execute()
        self.assertEqual(plugin._image_metadata.final_shape, self._img_shape)

    def test_pre_execute__no_images_per_file_set(self):
        plugin = self.create_plugin_with_filelist()
        plugin.set_param_value("images_per_file", -1)
        plugin.pre_execute()
        self.assertEqual(plugin._image_metadata.final_shape, self._img_shape)
        self.assertEqual(plugin.get_param_value("images_per_file"), self._n_per_file)

    def test_execute__no_input(self):
        plugin = COLLECTION.get_plugin_by_name("EigerScanSeriesLoader")(
            images_per_file=1
        )
        with self.assertRaises(TypeError):
            plugin.execute(0)

    def test_execute__simple(self):
        plugin = self.create_plugin_with_filelist()
        _index = 0
        plugin.pre_execute()
        _data, kwargs = plugin.execute(_index)
        self.assertTrue((_data == _index).all())
        self.assertEqual(kwargs["frame"], self.get_index_in_file(_index))
        self.assertEqual(_data.metadata["frame"], [self.get_index_in_file(_index)])

    def test_execute__with_roi(self):
        plugin = self.create_plugin_with_filelist()
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
        plugin = self.create_plugin_with_filelist()
        plugin.pre_execute()
        for _index in range(self._n):
            _data, kwargs = plugin.execute(_index)
            self.assertTrue((_data == _index).all())
            self.assertEqual(kwargs["frame"], self.get_index_in_file(_index))
            self.assertEqual(_data.metadata["frame"], [self.get_index_in_file(_index)])

    def test_pickle(self):
        plugin = self.create_plugin_with_filelist()
        _new_params = {get_random_string(6): get_random_string(12) for i in range(7)}
        for _key, _val in _new_params.items():
            plugin.add_param(Parameter(_key, str, _val))
        plugin2 = pickle.loads(pickle.dumps(plugin))
        for _key in plugin.params:
            self.assertEqual(
                plugin.get_param_value(_key), plugin2.get_param_value(_key)
            )

    def test_calculate_result_shape(self):
        plugin = self.create_plugin_with_filelist()
        plugin.calculate_result_shape()
        self.assertEqual(plugin._original_input_shape, self._img_shape)

    def test_get_first_file_size(self):
        plugin = self.create_plugin_with_filelist()
        self.assertEqual(
            plugin.get_first_file_size(), os.stat(self._hdf5_fnames[0]).st_size
        )


if __name__ == "__main__":
    unittest.main()
