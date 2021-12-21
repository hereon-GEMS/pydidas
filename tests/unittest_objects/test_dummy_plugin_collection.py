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

from pydidas.plugins.plugin_collection import _PluginCollection
from pydidas.unittest_objects import DummyPluginCollection


class TestDummyPluginCollection(unittest.TestCase):

    def setUp(self):
        ...

    def tearDown(self):
        ...

    def test_dummy_plugin_collection(self):
        PC = DummyPluginCollection()
        self.assertIsInstance(PC, _PluginCollection)
        self.assertEqual(len(PC.get_all_plugins()), 21)

    def test_dummy_plugin_collection_w_n_plugins(self):
        _n = 13
        PC = DummyPluginCollection(n_plugins=_n)
        self.assertIsInstance(PC, _PluginCollection)
        self.assertEqual(len(PC.get_all_plugins()), _n)


if __name__ == "__main__":
    unittest.main()
