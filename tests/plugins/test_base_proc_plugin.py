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


import shutil
import tempfile
import unittest

import numpy as np

from pydidas.core.constants import PROC_PLUGIN
from pydidas.plugins import ProcPlugin
from pydidas.unittest_objects import create_plugin_class


class TestBaseProcPlugin(unittest.TestCase):
    def setUp(self):
        self._temppath = tempfile.mkdtemp()
        self._shape = (20, 20)
        self._data = np.random.random(self._shape)

    def tearDown(self):
        shutil.rmtree(self._temppath)

    def test_class(self):
        plugin = create_plugin_class(PROC_PLUGIN)()
        self.assertIsInstance(plugin, ProcPlugin)

    def test_is_basic_plugin__baseclass(self):
        for _plugin in [ProcPlugin, ProcPlugin()]:
            with self.subTest(plugin=_plugin):
                self.assertTrue(_plugin.is_basic_plugin())

    def test_is_basic_plugin__subclass(self):
        _class = create_plugin_class(PROC_PLUGIN)
        for _plugin in [_class, _class()]:
            with self.subTest(plugin=_plugin):
                self.assertFalse(_plugin.is_basic_plugin())


if __name__ == "__main__":
    unittest.main()
