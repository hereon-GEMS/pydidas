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
__version__ = "0.0.1"
__maintainer__ = "Malte Storm"
__status__ = "Development"

import os
import unittest
import tempfile
import shutil
from pathlib import Path

import numpy as np
import h5py

from pydidas.plugins import PluginCollection, BasePlugin

PLUGIN_COLLECTION = PluginCollection()

class TestHdf5singleFileLoader(unittest.TestCase):

    def setUp(self):
        self._path = tempfile.mkdtemp()
        self._img_shape = (10, 10)
        self._n = 13
        self._hdf5key = '/entry/data/data'
        self._data = np.zeros(((self._n,) + self._img_shape), dtype=np.uint16)
        for index in range(self._n):
            self._data[index] = index

        self._hdf5_fname = Path(os.path.join(self._path, 'test_000.h5'))
        with h5py.File(self._hdf5_fname, 'w') as f:
            f[self._hdf5key] = self._data

    def tearDown(self):
        shutil.rmtree(self._path)

    def create_plugin_with_hdf5_filelist(self):
        plugin = PLUGIN_COLLECTION.get_plugin_by_name('Hdf5singleFileLoader')()
        plugin.set_param_value('filename', self._hdf5_fname)
        plugin.set_param_value('hdf5_key', self._hdf5key)
        return plugin

    def test_creation(self):
        plugin = PLUGIN_COLLECTION.get_plugin_by_name('Hdf5singleFileLoader')()
        self.assertIsInstance(plugin, BasePlugin)

    def test_execute__no_input(self):
        plugin = PLUGIN_COLLECTION.get_plugin_by_name('Hdf5singleFileLoader')()
        with self.assertRaises(KeyError):
            plugin.execute(0)

    def test_execute__simple(self):
        plugin = self.create_plugin_with_hdf5_filelist()
        _index = 0
        _data, kwargs = plugin.execute(_index)
        self.assertTrue((_data == _index).all())
        self.assertEqual(kwargs['frame'], _index)
        self.assertEqual(_data.metadata['frame'], _index)

    def test_execute__get_all_frames(self):
        plugin = self.create_plugin_with_hdf5_filelist()
        for _index in range(self._n):
            _data, kwargs = plugin.execute(_index)
            self.assertTrue((_data == _index).all())
            self.assertEqual(kwargs['frame'], _index)
            self.assertEqual(_data.metadata['frame'], _index)


if __name__ == "__main__":
    unittest.main()
