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

from pydidas.apps.parsers import execute_workflow_app_parser
from pydidas.core.utils import get_random_string


class TestAppParsers(unittest.TestCase):
    def setUp(self):
        self._argv = copy.copy(sys.argv)

    def tearDown(self):
        sys.argv = self._argv

    def test_parse_execute_workflow_cmdline_arguments_no_args(self):
        sys.argv = ["test"]
        parsed = execute_workflow_app_parser()
        self.assertFalse(parsed["autosave_results"])
        self.assertIsNone(parsed["autosave_directory"])
        self.assertIsNone(parsed["autosave_format"])

    def test_parse_execute_workflow_cmdline_arguments(self):
        _dir = get_random_string(12)
        _format = ":.3f"
        sys.argv = ["test", "--autosave", "-d", _dir, "-f", _format]
        parsed = execute_workflow_app_parser()
        self.assertTrue(parsed["autosave_results"])
        self.assertEqual(parsed["autosave_directory"], _dir)
        self.assertEqual(parsed["autosave_format"], _format)


if __name__ == "__main__":
    unittest.main()
