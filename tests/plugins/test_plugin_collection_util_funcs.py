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

import unittest
from pathlib import Path

import pydidas
from pydidas.core.constants import BASE_PLUGIN, INPUT_PLUGIN, OUTPUT_PLUGIN, PROC_PLUGIN
from pydidas.plugins.plugin_collection_util_funcs import (
    get_generic_plugin_path,
    plugin_type_check,
)
from pydidas.unittest_objects import create_plugin_class


class TestPluginCollectionUtilFuncs(unittest.TestCase):
    def setUp(self):
        ...

    def tearDown(self):
        ...

    def test_get_generic_plugin_path(self):
        _target = (
            Path(pydidas.__path__[0]).absolute().parent.joinpath("pydidas_plugins")
        )
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
