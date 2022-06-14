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


import os
import unittest
import shutil
import tempfile

from pydidas.experiment.setup_scan import SetupScan, SetupScanIoBase, SetupScanIoMeta


SCAN_SETTINGS = SetupScan()
SCAN_IO_META = SetupScanIoMeta
SCAN_IO_META.clear_registry()


class TestIo(SetupScanIoBase):
    extensions = ["test"]
    format_name = "Test"

    @classmethod
    def reset(cls):
        cls.imported = False
        cls.exported = False
        cls.export_filename = None
        cls.import_filename = None

    @classmethod
    def export_to_file(cls, filename, **kwargs):
        cls.exported = True
        cls.export_filename = filename

    @classmethod
    def import_from_file(cls, filename):
        cls.imported = True
        cls.import_filename = filename


class TestSetupScanIoMeta(unittest.TestCase):
    def setUp(self):
        self._tmppath = tempfile.mkdtemp()
        TestIo.reset()

    def tearDown(self):
        shutil.rmtree(self._tmppath)
        SCAN_SETTINGS.restore_all_defaults(True)

    def test_export_to_file(self):
        _fname = os.path.join(self._tmppath, "test.test")
        SCAN_IO_META.export_to_file(_fname)
        self.assertTrue(TestIo.exported)
        self.assertEqual(TestIo.export_filename, _fname)

    def test_import_from_file(self):
        _fname = os.path.join(self._tmppath, "test.test")
        SCAN_IO_META.import_from_file(_fname)
        self.assertTrue(TestIo.imported)
        self.assertEqual(TestIo.import_filename, _fname)


if __name__ == "__main__":
    unittest.main()
    SCAN_IO_META.clear_registry()
