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


import unittest

from pydidas.core.constants import OUTPUT_PLUGIN
from pydidas.plugins import OutputPlugin
from pydidas.unittest_objects import create_plugin_class


class TestBaseOutputPlugin(unittest.TestCase):
    def setUp(self): ...

    def tearDown(self): ...

    def test_class(self):
        plugin = create_plugin_class(OUTPUT_PLUGIN)
        self.assertIsInstance(plugin(), OutputPlugin)

    def test_is_basic_plugin__this_class(self):
        for _plugin in [OutputPlugin, OutputPlugin()]:
            with self.subTest(plugin=_plugin):
                self.assertTrue(_plugin.is_basic_plugin())

    def test_is_basic_plugin__sub_class(self):
        _class = create_plugin_class(OUTPUT_PLUGIN)
        for _plugin in [_class, _class()]:
            with self.subTest(plugin=_plugin):
                self.assertFalse(_plugin.is_basic_plugin())


if __name__ == "__main__":
    unittest.main()
