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
import random

import numpy as np
from qtpy import QtCore

from pydidas.plugins import PluginCollection, BasePlugin
from pydidas.image_io import rebin2d


PLUGIN_COLLECTION = PluginCollection()


class TestMaskImage(unittest.TestCase):

    def setUp(self):
        self._temppath = tempfile.mkdtemp()
        self._qsettings = QtCore.QSettings('Hereon', 'pydidas')
        self._qsettings_det_mask = self._qsettings.value('global/det_mask')
        self._qsettings.setValue('global/det_mask', '')
        self._shape = (20, 20)
        _n = self._shape[0] * self._shape[1]
        self._mask = np.asarray([random.choice([0, 1])
                                 for _ in range(_n)]).reshape(self._shape)
        self._data = np.ones(self._shape)

    def tearDown(self):
        shutil.rmtree(self._temppath)
        self._qsettings.setValue('global/det_mask', self._qsettings_det_mask)

    def create_mask(self):
        _maskfilename = os.path.join(self._temppath, 'mask.npy')
        np.save(_maskfilename, self._mask)
        return _maskfilename

    def test_creation(self):
        plugin = PLUGIN_COLLECTION.get_plugin_by_name('MaskImage')()
        self.assertIsInstance(plugin, BasePlugin)

    def test_pre_execute__local_mask(self):
        _maskfilename = self.create_mask()
        plugin = PLUGIN_COLLECTION.get_plugin_by_name('MaskImage')()
        plugin.set_param_value('use_global_mask', False)
        plugin.set_param_value('det_mask', _maskfilename)
        plugin.pre_execute()
        self.assertTrue((plugin._mask == self._mask).all())

    def test_pre_execute__q_settings_mask(self):
        _maskfilename = self.create_mask()
        self._qsettings.setValue('global/det_mask', _maskfilename)
        plugin = PLUGIN_COLLECTION.get_plugin_by_name('MaskImage')()
        plugin.set_param_value('use_global_mask', True)
        plugin.pre_execute()
        self.assertTrue(np.equal(plugin._mask, self._mask).all())

    def test_execute__simple(self):
        _maskval = 0.42
        _maskfilename = self.create_mask()
        plugin = PLUGIN_COLLECTION.get_plugin_by_name('MaskImage')()
        plugin.set_param_value('use_global_mask', False)
        plugin.set_param_value('det_mask', _maskfilename)
        plugin.set_param_value('det_mask_val', _maskval)
        plugin.pre_execute()
        kwargs = {'key': 1, 'another_key': 'another_val'}
        _masked, _kwargs = plugin.execute(self._data, **kwargs)
        self.assertEqual(kwargs, _kwargs)
        self.assertTrue(np.alltrue(_masked[self._mask == 1] == _maskval))

    def test_execute__with_legacy_ops(self):
        _maskval = 0.42
        _maskfilename = self.create_mask()
        plugin = PLUGIN_COLLECTION.get_plugin_by_name('MaskImage')()
        plugin.set_param_value('use_global_mask', False)
        plugin.set_param_value('det_mask', _maskfilename)
        plugin.set_param_value('det_mask_val', _maskval)
        plugin._legacy_image_ops = [
            ['roi', (1, self._shape[0], 3, self._shape[1])], ['binning', 2]]
        plugin._original_input_shape = self._shape
        _data = rebin2d(self._data[1:, 3:], 2)
        _mask = np.where(rebin2d(self._mask[1:, 3:], 2) > 0, 1, 0)
        plugin.pre_execute()
        kwargs = {'key': 1, 'another_key': 'another_val'}
        _masked, _kwargs = plugin.execute(_data, **kwargs)
        self.assertEqual(kwargs, _kwargs)
        self.assertEqual(
            _masked.shape,
            ((self._shape[0] - 1) // 2, (self._shape[1] - 3) // 2))
        self.assertTrue(np.alltrue(_masked[_mask == 1] == _maskval))


if __name__ == "__main__":
    unittest.main()
