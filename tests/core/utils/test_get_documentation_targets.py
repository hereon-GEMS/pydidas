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
import os


from qtpy import QtCore

from pydidas.core.utils import (
    get_doc_make_directory, get_doc_home_filename, get_doc_home_address,
    get_doc_home_qurl)


class TestGetDocQUrl(unittest.TestCase):

    def setUp(self):
        ...

    def tearDown(self):
        ...

    def test_get_doc_make_directory(self):
        _dir = get_doc_make_directory()
        self.assertIn('Makefile', os.listdir(_dir))

    def test_get_doc_home_filename(self):
        _fname = get_doc_home_filename()
        self.assertTrue(os.path.exists(_fname))

    def test_get_doc_home_address(self):
        _address = get_doc_home_address()
        self.assertTrue(_address.startswith( 'file:///' ))

    def test_get_doc_qurl(self):
        _url = get_doc_home_qurl()
        self.assertIsInstance(_url, QtCore.QUrl)


if __name__ == "__main__":
    unittest.main()
