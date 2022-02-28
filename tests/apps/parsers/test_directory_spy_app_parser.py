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


import copy
import unittest
import sys

from pydidas.apps.parsers import directory_spy_app_parser


class TestAppParsers(unittest.TestCase):

    def setUp(self):
        self._argv = copy.copy(sys.argv)

    def tearDown(self):
        sys.argv = self._argv

    def test_directory_spy_app_parser__case1(self):
        sys.argv = ['test', '-filename_pattern', 'something',
                    '--do_not_use_detmask']
        parsed = directory_spy_app_parser()
        self.assertEqual(parsed['filename_pattern'], 'something')
        self.assertEqual(parsed['use_global_det_mask'], False)
        self.assertIsNone(parsed['scan_for_all'])
        self.assertIsNone(parsed['use_bg_file'])

    def test_directory_spy_app_parser__case2(self):
        sys.argv = ['test', '--scan_for_all', '-directory_path',
                    'some/directory']
        parsed = directory_spy_app_parser()
        self.assertTrue(parsed['scan_for_all'])
        self.assertEqual(parsed['directory_path'], 'some/directory')
        self.assertIsNone(parsed['use_global_det_mask'])

    def test_directory_spy_app_parser__case3(self):
        sys.argv = ['test', '--use_bg_file', '-bg_file', 'a/file',
                    '-bg_hdf5_key', 'data/key']
        parsed = directory_spy_app_parser()
        self.assertTrue(parsed['use_bg_file'])
        self.assertEqual(parsed['bg_file'], 'a/file')
        self.assertEqual(parsed['bg_hdf5_key'], 'data/key')

    def test_directory_spy_app_parser__no_args(self):
        sys.argv = ['test']
        parsed = directory_spy_app_parser()
        self.assertIsNone(parsed['scan_for_all'])
        self.assertIsNone(parsed['use_global_det_mask'])
        self.assertIsNone(parsed['use_bg_file'])


if __name__ == "__main__":
    unittest.main()
