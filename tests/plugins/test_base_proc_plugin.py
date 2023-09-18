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
import shutil
import tempfile
import unittest

import h5py
import numpy as np

from pydidas.core.constants import PROC_PLUGIN
from pydidas.core.utils import get_random_string
from pydidas.plugins import ProcPlugin
from pydidas.unittest_objects import create_plugin_class


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


if __name__ == "__main__":
    unittest.main()
