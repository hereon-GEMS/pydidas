# This file is part of pydidas.

# pydidas is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# Pydidas is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with Pydidas. If not, see <http://www.gnu.org/licenses/>.

"""Unit tests for pydidas modules."""

__author__      = "Malte Storm"
__copyright__   = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.0.1"
__maintainer__ = "Malte Storm"
__status__ = "Development"

import copy
import unittest
from pathlib import Path
import sys

from pydidas.apps.app_parsers import (
    parse_composite_creator_cmdline_arguments)


class TestAppParsers(unittest.TestCase):

    def setUp(self):
        ...

    def tearDown(self):
        ...

    def test_creation_with_cmdline_args(self):
        _argv = copy.copy(sys.argv)
        sys.argv = ['test', '-file_stepping', '5', '-binning', '2',
                    '-first_file', 'testname']
        parsed = parse_composite_creator_cmdline_arguments()
        sys.argv = _argv
        self.assertEqual(parsed['file_stepping'], 5)
        self.assertEqual(parsed['binning'], 2)
        self.assertEqual(parsed['first_file'], 'testname')


if __name__ == "__main__":
    unittest.main()
