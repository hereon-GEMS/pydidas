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


import os
import unittest

from qtpy import QtCore

from pydidas.core.utils import (
    DOC_HOME_ADDRESS,
    DOC_HOME_FILENAME,
    DOC_HOME_QURL,
    DOC_MAKE_DIRECTORY,
)


class TestGetDocQUrl(unittest.TestCase):
    def setUp(self):
        ...

    def tearDown(self):
        ...

    def test_DOC_MAKE_DIRECTORY(self):
        _dir = DOC_MAKE_DIRECTORY
        self.assertIn("Makefile", os.listdir(_dir))

    def test_DOC_HOME_FILENAME(self):
        _fname = DOC_HOME_FILENAME
        self.assertTrue(os.path.exists(_fname))

    def test_DOC_HOME_ADDRESS(self):
        _address = DOC_HOME_ADDRESS
        self.assertTrue(_address.startswith(r"file:///"))

    def test_get_doc_qurl(self):
        _url = DOC_HOME_QURL
        self.assertIsInstance(_url, QtCore.QUrl)


if __name__ == "__main__":
    unittest.main()
