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
import warnings
from pathlib import Path

import skimage
import numpy as np

from pydidas.core import AppConfigError, Parameter
from pydidas.core.utils import get_random_string
from pydidas.plugins import PluginCollection, BasePlugin


PLUGIN_COLLECTION = PluginCollection()


class TestFrameLoader(unittest.TestCase):

    def setUp(self):
        self._path = tempfile.mkdtemp()
        self._img_shape = (10, 10)
        self._n = 113
        self._data = np.zeros(((self._n,) + self._img_shape), dtype=np.uint16)
        self._fnames = lambda i: os.path.join(self._path, f'test_{i:03d}.tiff')
        for index in range(self._n):
            self._data[index] = index

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            for i in range(self._n):
                _fname = Path(os.path.join(self._path, f'test_{i:03d}.tiff'))
                skimage.io.imsave(_fname, self._data[i])

    def tearDown(self):
        shutil.rmtree(self._path)

    def create_plugin_with_filelist(self):
        plugin = PLUGIN_COLLECTION.get_plugin_by_name('FrameLoader')()
        plugin.set_param_value('first_file', self._fnames(0))
        plugin.set_param_value('last_file', self._fnames(self._n - 1))
        return plugin

    def test_creation(self):
        plugin = PLUGIN_COLLECTION.get_plugin_by_name('FrameLoader')()
        self.assertIsInstance(plugin, BasePlugin)

    def test_pre_execute__no_input(self):
        plugin = PLUGIN_COLLECTION.get_plugin_by_name('FrameLoader')()
        with self.assertRaises(AppConfigError):
            plugin.pre_execute()

    def test_pre_execute__simple(self):
        plugin = self.create_plugin_with_filelist()
        plugin.pre_execute()
        self.assertEqual(plugin._file_manager.n_files, self._n)
        self.assertEqual(plugin._image_metadata.final_shape, self._img_shape)

    def test_execute__no_input(self):
        plugin = PLUGIN_COLLECTION.get_plugin_by_name('FrameLoader')(
            images_per_file=1)
        with self.assertRaises(AppConfigError):
            plugin.execute(0)

    def test_execute__simple(self):
        plugin = self.create_plugin_with_filelist()
        _index = 0
        plugin.pre_execute()
        _data, kwargs = plugin.execute(_index)
        self.assertTrue((_data == _index).all())

    def test_execute__with_roi(self):
        plugin = self.create_plugin_with_filelist()
        plugin.set_param_value('use_roi', True)
        plugin.set_param_value('roi_yhigh', 5)
        _index = 0
        plugin.pre_execute()
        _data, kwargs = plugin.execute(_index)
        self.assertTrue((_data == _index).all())
        self.assertEqual(
            _data.shape,
            (plugin.get_param_value('roi_yhigh'), self._img_shape[1]))

    def test_execute__get_all_frames(self):
        plugin = self.create_plugin_with_filelist()
        plugin.pre_execute()
        for _index in range(self._n):
            _data, kwargs = plugin.execute(_index)
            self.assertTrue((_data == _index).all())

    def test_pickle(self):
        plugin = self.create_plugin_with_filelist()
        _new_params = {get_random_string(6): get_random_string(12)
                       for i in range(7)}
        for _key, _val in _new_params.items():
            plugin.add_param(Parameter(_key, str, _val))
        plugin2 = pickle.loads(pickle.dumps(plugin))
        for _key in plugin.params:
            self.assertEqual(plugin.get_param_value(_key),
                             plugin2.get_param_value(_key))


if __name__ == "__main__":
    unittest.main()
