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
__version__ = "0.1.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"


import unittest
import os

import pydidas
from pydidas.unittest_objects import create_plugin_class
from pydidas.plugins.plugin_collection_util_funcs import (
    get_generic_plugin_path, plugin_type_check)
from pydidas.core.constants import (BASE_PLUGIN, INPUT_PLUGIN, PROC_PLUGIN,
                                    OUTPUT_PLUGIN)

class TestPluginCollectionUtilFuncs(unittest.TestCase):

    def setUp(self):
        ...

    def tearDown(self):
        ...

    def test_get_generic_plugin_path(self):
        _target = os.path.join(os.path.dirname(pydidas.__path__[0]), 'plugins')
        self.assertEqual(get_generic_plugin_path()[0], _target)

    def test_plugin_type_check__w_base_plugin(self):
        _plugin = create_plugin_class(INPUT_PLUGIN)
        self.assertEqual(plugin_type_check(_plugin), INPUT_PLUGIN)

    def test_plugin_type_check__w_input_plugin(self):
        _plugin = create_plugin_class(BASE_PLUGIN)
        self.assertEqual(plugin_type_check(_plugin), -1)

    def test_plugin_type_check__w_proc_plugin(self):
        _plugin = create_plugin_class(PROC_PLUGIN)
        self.assertEqual(plugin_type_check(_plugin), PROC_PLUGIN)

    def test_plugin_type_check__w_output_plugin(self):
        _plugin = create_plugin_class(OUTPUT_PLUGIN)
        self.assertEqual(plugin_type_check(_plugin), OUTPUT_PLUGIN)


if __name__ == "__main__":
    unittest.main()
