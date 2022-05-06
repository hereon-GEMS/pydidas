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

from pydidas.core.constants import OUTPUT_PLUGIN

from pydidas.unittest_objects import create_plugin_class
from pydidas.plugins import OutputPlugin


class TestBaseOutputPlugin(unittest.TestCase):
    def setUp(self):
        ...

    def tearDown(self):
        ...

    def test_class(self):
        plugin = create_plugin_class(OUTPUT_PLUGIN)
        self.assertIsInstance(plugin(), OutputPlugin)


if __name__ == "__main__":
    unittest.main()
