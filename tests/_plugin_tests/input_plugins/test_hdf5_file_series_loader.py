# This file is part of pydidas.
#
# Copyright 2021-, Helmholtz-Zentrum Hereon
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
__copyright__ = "Copyright 2021-, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Development"

import os
import pickle
import shutil
import tempfile
import unittest
from pathlib import Path

import h5py
import numpy as np

from pydidas.contexts import ScanContext
from pydidas.core import Parameter, UserConfigError
from pydidas.core.utils import get_random_string
from pydidas.plugins import BasePlugin, PluginCollection


PLUGIN_COLLECTION = PluginCollection()
SCAN = ScanContext()


class TestHdf5FileSeriesLoader(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._path = tempfile.mkdtemp()
        cls._img_shape = (10, 10)
        cls._n_per_file = 13
        cls._n_files = 11
        cls._fname_i0 = 2
        cls._n = cls._n_files * cls._n_per_file
        cls._hdf5key = "/entry/data/data"
        cls._data = np.repeat(
            np.arange(cls._n, dtype=np.uint16), np.prod(cls._img_shape)
        ).reshape((cls._n,) + cls._img_shape)

        cls._hdf5_fnames = []
        for i in range(cls._n_files):
            _fname = Path(os.path.join(cls._path, f"test_{i + cls._fname_i0:05d}.h5"))
            cls._hdf5_fnames.append(_fname)
            _slice = slice(i * cls._n_per_file, (i + 1) * cls._n_per_file, 1)
            with h5py.File(_fname, "w") as f:
                f[cls._hdf5key] = cls._data[_slice]

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls._path)

    def setUp(self):
        SCAN.restore_all_defaults(True)
        SCAN.set_param_value("scan_name_pattern", "test_#####.h5")
        SCAN.set_param_value("scan_base_directory", self._path)
        SCAN.set_param_value("scan_start_index", self._fname_i0)

    def tearDown(self):
        SCAN.restore_all_defaults(True)

    def create_plugin(self):
        plugin = PLUGIN_COLLECTION.get_plugin_by_name("Hdf5fileSeriesLoader")()
        plugin.set_param_value("images_per_file", self._n_per_file)
        plugin.set_param_value("hdf5_key", self._hdf5key)
        return plugin

    def get_index_in_file(self, index):
        return index % self._n_per_file

    def test_creation(self):
        plugin = PLUGIN_COLLECTION.get_plugin_by_name("Hdf5fileSeriesLoader")()
        self.assertIsInstance(plugin, BasePlugin)

    def test_pre_execute__no_input(self):
        plugin = PLUGIN_COLLECTION.get_plugin_by_name("Hdf5fileSeriesLoader")()
        plugin.pre_execute()
        self.assertEqual(plugin._image_metadata.final_shape, self._img_shape)

    def test_pre_execute__simple(self):
        plugin = self.create_plugin()
        plugin.pre_execute()
        self.assertEqual(plugin._image_metadata.final_shape, self._img_shape)

    def test_pre_execute__no_images_per_file_set(self):
        plugin = self.create_plugin()
        plugin.set_param_value("images_per_file", -1)
        plugin.pre_execute()
        self.assertEqual(plugin._image_metadata.final_shape, self._img_shape)
        self.assertEqual(
            plugin.get_param_value("_counted_images_per_file"), self._n_per_file
        )

    def test_execute__no_input(self):
        plugin = self.create_plugin()
        with self.assertRaises(UserConfigError):
            plugin.execute(0)

    def test_execute__simple(self):
        plugin = self.create_plugin()
        _index = 0
        plugin.pre_execute()
        _data, kwargs = plugin.execute(_index)
        self.assertTrue((_data == _index).all())
        self.assertEqual(kwargs["frame"], self.get_index_in_file(_index))
        self.assertEqual(_data.metadata["frame"], [self.get_index_in_file(_index)])

    def test_execute__with_roi(self):
        plugin = self.create_plugin()
        plugin.set_param_value("use_roi", True)
        plugin.set_param_value("roi_yhigh", 5)
        _index = 0
        plugin.pre_execute()
        _data, kwargs = plugin.execute(_index)
        self.assertTrue((_data == _index).all())
        self.assertEqual(kwargs["frame"], self.get_index_in_file(_index))
        self.assertEqual(_data.metadata["frame"], [self.get_index_in_file(_index)])
        self.assertEqual(
            _data.shape, (plugin.get_param_value("roi_yhigh"), self._img_shape[1])
        )

    def test_execute__get_all_frames(self):
        plugin = self.create_plugin()
        plugin.pre_execute()
        for _index in range(self._n):
            _data, kwargs = plugin.execute(_index)
            self.assertTrue((_data == _index).all())
            self.assertEqual(kwargs["frame"], self.get_index_in_file(_index))
            self.assertEqual(_data.metadata["frame"], [self.get_index_in_file(_index)])

    def test_pickle(self):
        plugin = self.create_plugin()
        _new_params = {get_random_string(6): get_random_string(12) for i in range(7)}
        for _key, _val in _new_params.items():
            plugin.add_param(Parameter(_key, str, _val))
        plugin2 = pickle.loads(pickle.dumps(plugin))
        for _key in plugin.params:
            self.assertEqual(
                plugin.get_param_value(_key), plugin2.get_param_value(_key)
            )


if __name__ == "__main__":
    unittest.main()
