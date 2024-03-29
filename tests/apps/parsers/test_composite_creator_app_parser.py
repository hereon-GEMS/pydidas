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


import copy
import sys
import unittest

from pydidas.apps.parsers import composite_creator_app_parser


class TestAppParsers(unittest.TestCase):
    def setUp(self):
        self._argv = copy.copy(sys.argv)

    def tearDown(self):
        sys.argv = self._argv

    def test_composite_creator_app_parser(self):
        sys.argv = [
            "test",
            "-file_stepping",
            "5",
            "-binning",
            "2",
            "-first_file",
            "testname",
        ]
        parsed = composite_creator_app_parser()
        self.assertEqual(parsed["file_stepping"], 5)
        self.assertEqual(parsed["binning"], 2)
        self.assertEqual(parsed["first_file"], "testname")


if __name__ == "__main__":
    unittest.main()
