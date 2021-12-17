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
__copyright__ = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.0.1"
__maintainer__ = "Malte Storm"
__status__ = "Development"

import unittest
import time
import string
import random

from pydidas.plugins import (BasePlugin, InputPlugin,
                             ProcPlugin, OutputPlugin)
from pydidas.unittest_objects.dummy_plugin_collection import (
    create_plugin_class, DummyPluginCollection)
from pydidas.core.constants import (BASE_PLUGIN, INPUT_PLUGIN, PROC_PLUGIN,
                               OUTPUT_PLUGIN)


class TestDummyPluginCollection(unittest.TestCase):

    def setUp(self):
        ...

    def tearDown(self):
        ...

    def test_init__no_path(self):
        ...

    def test_create_plugin_class__input(self):
        _cls = create_plugin_class(0, INPUT_PLUGIN)
        _instance = _cls()
        self.assertIsInstance(_instance, InputPlugin)

    def test_create_plugin_class__proc(self):
        _cls = create_plugin_class(0, PROC_PLUGIN)
        _instance = _cls()
        self.assertIsInstance(_instance, ProcPlugin)

    def test_create_plugin_class__output(self):
        _cls = create_plugin_class(0, OUTPUT_PLUGIN)
        _instance = _cls()
        self.assertIsInstance(_instance, OutputPlugin)


if __name__ == "__main__":
    unittest.main()
