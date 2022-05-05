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


import unittest
import shutil
import tempfile
import os

import h5py
import numpy as np

from pydidas.core.constants import PROC_PLUGIN
from pydidas.core.utils import get_random_string
from pydidas.unittest_objects import create_plugin_class
from pydidas.plugins import ProcPlugin


class TestBaseProcPlugin(unittest.TestCase):
    def setUp(self):
        self._temppath = tempfile.mkdtemp()
        self._shape = (20, 20)
        self._data = np.random.random(self._shape)

    def tearDown(self):
        shutil.rmtree(self._temppath)

    def create_image(self):
        _fname = os.path.join(self._temppath, "image.npy")
        np.save(_fname, self._data)
        return _fname

    def create_hdf5_image(self):
        _fname = os.path.join(self._temppath, "image.h5")
        _dset = get_random_string(4) + "/" + get_random_string(4) + "data"
        with h5py.File(_fname, "w") as _f:
            _f[_dset] = self._data[None]
        return _fname, _dset

    def test_class(self):
        plugin = create_plugin_class(PROC_PLUGIN)()
        self.assertIsInstance(plugin, ProcPlugin)

    def test_load_image_from_file__simple(self):
        _fname = self.create_image()
        plugin = create_plugin_class(PROC_PLUGIN)()
        _image = plugin.load_image_from_file(_fname)
        self.assertTrue(np.allclose(_image, self._data))

    def test_load_image_from_file__hdf5(self):
        _fname, _dset = self.create_hdf5_image()
        plugin = create_plugin_class(PROC_PLUGIN)()
        _image = plugin.load_image_from_file(_fname, hdf5_dset=_dset)
        self.assertTrue(np.allclose(_image, self._data))


if __name__ == "__main__":
    unittest.main()
