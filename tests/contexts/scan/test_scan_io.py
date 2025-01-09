# This file is part of pydidas.
#
# Copyright 2023 - 2025, Helmholtz-Zentrum Hereon
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
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"


import os
import shutil
import tempfile
import unittest
from pathlib import Path

from pydidas.contexts.scan import Scan, ScanContext, ScanIo, ScanIoBase
from pydidas.core import UserConfigError


SCAN = ScanContext()


class TestIo(ScanIoBase):
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
    def import_from_file(cls, filename, scan):
        cls.imported = True
        cls.scan = SCAN if scan is None else scan
        cls.import_filename = filename


class TestIoBeamlineFormat(TestIo):
    extensions = ["bl_test"]
    format_name = "Beamline Test"
    beamline_format = True
    import_only = True


class TestScanIo(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._original_registry = ScanIo.registry.copy()
        ScanIo.clear_registry()
        ScanIo.register_class(TestIo)
        ScanIo.register_class(TestIoBeamlineFormat)

    @classmethod
    def tearDownClass(cls):
        ScanIo.registry = cls._original_registry

    def setUp(self):
        self._tmppath = Path(tempfile.mkdtemp())
        TestIo.reset()
        TestIoBeamlineFormat.reset()
        TestIoBeamlineFormat.import_only = True

    def tearDown(self):
        shutil.rmtree(self._tmppath)
        SCAN.restore_all_defaults(True)

    def test_register_class(self):
        # this is done implicitly in the metaclass
        self.assertIn("test", ScanIo.registry)
        self.assertIn("bl_test", ScanIo.beamline_format_registry)

    def test_clear_registry(self):
        ScanIo.clear_registry()
        self.assertEqual(ScanIo.registry, {})
        self.assertEqual(ScanIo.beamline_format_registry, {})

    def test_is_extension_registered(self):
        for _ext in ["test", "bl_test"]:
            with self.subTest(ext=_ext):
                self.assertTrue(ScanIo.is_extension_registered(_ext))

    def test_export_to_file(self):
        _fname = self._tmppath.joinpath("test.test")
        ScanIo.export_to_file(_fname)
        self.assertTrue(TestIo.exported)
        self.assertEqual(TestIo.export_filename, _fname)

    def test_export_to_file__bl_format(self):
        _fname = self._tmppath.joinpath("test.bl_test")
        ScanIo.beamline_format_registry["bl_test"].import_only = False
        ScanIo.export_to_file(_fname)
        self.assertTrue(TestIoBeamlineFormat.exported)
        self.assertEqual(TestIoBeamlineFormat.export_filename, _fname)

    def test_export_to_file__import_only(self):
        _fname = self._tmppath.joinpath("test.bl_test")
        with self.assertRaises(UserConfigError):
            ScanIo.export_to_file(_fname)

    def test_import_from_file__generic_ScanContext(self):
        _fname = os.path.join(self._tmppath, "test.test")
        ScanIo.import_from_file(_fname)
        self.assertTrue(TestIo.imported)
        self.assertEqual(TestIo.import_filename, _fname)
        self.assertEqual(TestIo.scan, SCAN)

    def test_import_from_file__given_Scan(self):
        _fname = os.path.join(self._tmppath, "test.test")
        _scan = Scan()
        ScanIo.import_from_file(_fname, scan=_scan)
        self.assertTrue(TestIo.imported)
        self.assertEqual(TestIo.import_filename, _fname)
        self.assertEqual(TestIo.scan, _scan)

    def test_get_string_of_beamline_formats(self):
        _str = ScanIo.get_string_of_beamline_formats()
        self.assertIn("*.bl_test", _str)
        self.assertNotIn("*.test", _str)


if __name__ == "__main__":
    unittest.main()
    ScanIo.clear_registry()
