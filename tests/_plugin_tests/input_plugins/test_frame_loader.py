# This file is part of pydidas.
#
# Copyright 2023, Helmholtz-Zentrum Hereon
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
__copyright__ = "Copyright 2023, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"

import os
import pickle
import shutil
import tempfile
import unittest
import warnings
from pathlib import Path

import numpy as np
import skimage

from pydidas.contexts import ScanContext
from pydidas.core import Parameter, UserConfigError
from pydidas.core.utils import get_random_string
from pydidas.plugins import BasePlugin, PluginCollection


PLUGIN_COLLECTION = PluginCollection()
SCAN = ScanContext()


class TestFrameLoader(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._path = tempfile.mkdtemp()
        cls._img_shape = (10, 10)
        cls._n = 113
        cls._fname_i0 = 2
        cls._data = np.repeat(
            np.arange(cls._n, dtype=np.uint16), np.prod(cls._img_shape)
        ).reshape((cls._n,) + cls._img_shape)
        cls._fnames = lambda i: os.path.join(cls._path, f"test_{i:05d}.tiff")

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            for i in range(cls._n):
                _fname = Path(
                    os.path.join(cls._path, f"test_{i + cls._fname_i0:05d}.tiff")
                )
                skimage.io.imsave(_fname, cls._data[i])

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls._path)

    def setUp(self):
        SCAN.restore_all_defaults(True)
        SCAN.set_param_value("scan_name_pattern", "test_#####.tiff")
        SCAN.set_param_value("scan_base_directory", self._path)
        SCAN.set_param_value("scan_start_index", self._fname_i0)

    def tearDown(self):
        SCAN.restore_all_defaults(True)

    def test_creation(self):
        plugin = PLUGIN_COLLECTION.get_plugin_by_name("FrameLoader")()
        self.assertIsInstance(plugin, BasePlugin)

    def test_pre_execute__simple(self):
        plugin = PLUGIN_COLLECTION.get_plugin_by_name("FrameLoader")()
        plugin.pre_execute()
        self.assertEqual(plugin._image_metadata.final_shape, self._img_shape)

    def test_execute__no_input(self):
        plugin = PLUGIN_COLLECTION.get_plugin_by_name("FrameLoader")()
        with self.assertRaises(UserConfigError):
            plugin.execute(0)

    def test_execute__simple(self):
        plugin = PLUGIN_COLLECTION.get_plugin_by_name("FrameLoader")()
        _index = 0
        plugin.pre_execute()
        _data, kwargs = plugin.execute(_index)
        self.assertTrue((_data == _index).all())

    def test_execute__with_roi(self):
        plugin = PLUGIN_COLLECTION.get_plugin_by_name("FrameLoader")()
        plugin.set_param_value("use_roi", True)
        plugin.set_param_value("roi_yhigh", 5)
        _index = 0
        plugin.pre_execute()
        _data, kwargs = plugin.execute(_index)
        self.assertTrue((_data == _index).all())
        self.assertEqual(
            _data.shape, (plugin.get_param_value("roi_yhigh"), self._img_shape[1])
        )

    def test_execute__get_all_frames(self):
        plugin = PLUGIN_COLLECTION.get_plugin_by_name("FrameLoader")()
        plugin.pre_execute()
        for _index in range(self._n):
            _data, kwargs = plugin.execute(_index)
            self.assertTrue((_data == _index).all())

    def test_pickle(self):
        plugin = PLUGIN_COLLECTION.get_plugin_by_name("FrameLoader")()
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
