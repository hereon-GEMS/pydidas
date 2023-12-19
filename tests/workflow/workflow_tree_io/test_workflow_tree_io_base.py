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
import shutil
import tempfile
import unittest

from pydidas.workflow.processing_tree_io import ProcessingTreeIoBase


class TestProcessingTreeIoBase(unittest.TestCase):
    def setUp(self):
        self._path = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self._path)

    def test_init(self):
        obj = ProcessingTreeIoBase()
        self.assertIsInstance(obj, ProcessingTreeIoBase)

    def test_import_from_file(self):
        obj = ProcessingTreeIoBase
        with self.assertRaises(NotImplementedError):
            obj.export_to_file("something")

    def test_export_to_file(self):
        obj = ProcessingTreeIoBase
        with self.assertRaises(NotImplementedError):
            obj.import_from_file("something")

    def test_check_for_existing_file__file_does_not_exist(self):
        obj = ProcessingTreeIoBase
        obj.check_for_existing_file(os.path.join(self._path, "test.txt"))
        # assert does not raise an Error

    def test_check_for_existing_file__file_does_exist(self):
        obj = ProcessingTreeIoBase
        _fname = os.path.join(self._path, "test.txt")
        with open(_fname, "w") as f:
            f.write("test")
        with self.assertRaises(FileExistsError):
            obj.check_for_existing_file(_fname)

    def test_check_for_existing_file__file_does_exist_and_overwrite(self):
        obj = ProcessingTreeIoBase
        _fname = os.path.join(self._path, "test.txt")
        with open(_fname, "w") as f:
            f.write("test")
        obj.check_for_existing_file(_fname, overwrite=True)
        # assert does not raise an Error


if __name__ == "__main__":
    unittest.main()
