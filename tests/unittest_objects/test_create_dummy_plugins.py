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

from pydidas.core.constants import BASE_PLUGIN, INPUT_PLUGIN, OUTPUT_PLUGIN, PROC_PLUGIN
from pydidas.plugins import BasePlugin, InputPlugin, OutputPlugin, ProcPlugin
from pydidas.unittest_objects.create_dummy_plugins import (
    create_base_class,
    create_plugin_class,
)


class TestDummyPluginCollection(unittest.TestCase):
    def setUp(self):
        ...

    def tearDown(self):
        ...

    def test_create_base_class_w_base(self):
        _cls = create_base_class(BasePlugin)
        _cls.default_params = "some defaults"
        self.assertTrue(issubclass(_cls, BasePlugin))
        self.assertNotEqual(_cls.default_params, BasePlugin.default_params)

    def test_create_plugin_class__base(self):
        _cls = create_plugin_class(BASE_PLUGIN)
        _instance = _cls()
        self.assertIsInstance(_instance, BasePlugin)

    def test_create_plugin_class__input(self):
        _cls = create_plugin_class(INPUT_PLUGIN)
        _instance = _cls()
        self.assertIsInstance(_instance, InputPlugin)

    def test_create_plugin_class__proc(self):
        _cls = create_plugin_class(PROC_PLUGIN)
        _instance = _cls()
        self.assertIsInstance(_instance, ProcPlugin)

    def test_create_plugin_class__output(self):
        _cls = create_plugin_class(OUTPUT_PLUGIN)
        _instance = _cls()
        self.assertIsInstance(_instance, OutputPlugin)

    def test_create_plugin_class__w_number(self):
        _num = 42
        _cls = create_plugin_class(OUTPUT_PLUGIN, number=_num)
        _instance = _cls()
        self.assertIsInstance(_instance, OutputPlugin)
        self.assertEqual(_instance.number, _num)


if __name__ == "__main__":
    unittest.main()
