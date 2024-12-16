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
import random
import shutil
import tempfile
import unittest

import numpy as np
from qtpy import QtCore

from pydidas.core import UserConfigError
from pydidas.core.utils import rebin2d
from pydidas.plugins import BasePlugin
from pydidas.unittest_objects import LocalPluginCollection


PLUGIN_COLLECTION = LocalPluginCollection()


class TestMaskImage(unittest.TestCase):
    @classmethod
    def tearDownClass(cls):
        qs = QtCore.QSettings("Hereon", "pydidas")
        qs.remove("unittesting")

    def setUp(self):
        self._temppath = tempfile.mkdtemp()
        self._shape = (20, 20)
        _n = self._shape[0] * self._shape[1]
        self._mask = np.asarray([random.choice([0, 1]) for _ in range(_n)]).reshape(
            self._shape
        )
        self._data = np.ones(self._shape)

    def tearDown(self):
        shutil.rmtree(self._temppath)

    def create_mask(self):
        _maskfilename = os.path.join(self._temppath, "mask.npy")
        np.save(_maskfilename, self._mask)
        return _maskfilename

    def test_creation(self):
        plugin = PLUGIN_COLLECTION.get_plugin_by_name("MaskImage")()
        self.assertIsInstance(plugin, BasePlugin)

    def test_pre_execute__local_mask(self):
        _maskfilename = self.create_mask()
        plugin = PLUGIN_COLLECTION.get_plugin_by_name("MaskImage")()
        plugin.set_param_value("detector_mask_file", _maskfilename)
        plugin.pre_execute()
        self.assertTrue((plugin._mask == self._mask).all())

    def test_execute__simple(self):
        _maskval = 0.42
        _maskfilename = self.create_mask()
        plugin = PLUGIN_COLLECTION.get_plugin_by_name("MaskImage")()
        plugin.set_param_value("detector_mask_file", _maskfilename)
        plugin.set_param_value("detector_mask_val", _maskval)
        plugin.pre_execute()
        kwargs = {"key": 1, "another_key": "another_val"}
        _masked, _kwargs = plugin.execute(self._data, **kwargs)
        self.assertEqual(kwargs, _kwargs)
        self.assertTrue(np.all(_masked[self._mask == 1] == _maskval))

    def test_execute__with_cropped_data(self):
        _maskval = 0.42
        _maskfilename = self.create_mask()
        plugin = PLUGIN_COLLECTION.get_plugin_by_name("MaskImage")()
        plugin.set_param_value("detector_mask_file", _maskfilename)
        plugin.set_param_value("detector_mask_val", _maskval)
        _data = rebin2d(self._data[1:, 3:], 2)
        plugin.pre_execute()
        with self.assertRaises(UserConfigError):
            plugin.execute(_data)


if __name__ == "__main__":
    unittest.main()
