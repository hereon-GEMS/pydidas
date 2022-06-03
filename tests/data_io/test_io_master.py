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

import numpy as np

from pydidas.core import utils
from pydidas.data_io import IoMaster


class Tester:
    extensions_export = ["test", "export"]
    extensions_import = ["test", "import"]
    format_name = "Tester"

    @classmethod
    def export_to_file(cls, filename, data, **kwargs):
        cls._exported = [filename, data, kwargs]

    @classmethod
    def import_from_file(cls, filename, **kwargs):
        cls._imported = [filename, kwargs]


class TestIoMaster(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._stored_exts_import = IoMaster.registry_import.copy()
        cls._stored_exts_export = IoMaster.registry_export.copy()

    @classmethod
    def tearDownClass(cls):
        IoMaster.registry_import = cls._stored_exts_import
        IoMaster.registry_export = cls._stored_exts_export

    def setUp(self):
        IoMaster.clear_registry()

    def tearDown(self):
        ...

    def test_register_class__plain(self):
        IoMaster.register_class(Tester)
        for _ext in Tester.extensions_export:
            self.assertEqual(IoMaster.registry_export[_ext], Tester)
        for _ext in Tester.extensions_import:
            self.assertEqual(IoMaster.registry_import[_ext], Tester)

    def test_register_class__add_class_and_verify_entries_not_deleted(self):
        IoMaster.registry_import = {".no_ext": None}
        IoMaster.register_class(Tester)
        self.assertIsNone(IoMaster.registry_import[".no_ext"])

    def test_register_class__add_class_and_overwrite_old_entry_import(self):
        IoMaster.registry_import = {"test": None}
        IoMaster.register_class(Tester, update_registry=True)
        self.assertEqual(IoMaster.registry_import["test"], Tester)

    def test_register_class__add_class_and_overwrite_old_entry_export(self):
        IoMaster.registry_export = {"test": None}
        IoMaster.register_class(Tester, update_registry=True)
        self.assertEqual(IoMaster.registry_import["test"], Tester)

    def test_register_class__add_and_keep_old_entry_import(self):
        IoMaster.registry_import = {"test": None}
        with self.assertRaises(KeyError):
            IoMaster.register_class(Tester, update_registry=False)

    def test_register_class__add_and_keep_old_entry_export(self):
        IoMaster.registry_export = {"test": None}
        with self.assertRaises(KeyError):
            IoMaster.register_class(Tester, update_registry=False)

    def test_clear_registry(self):
        IoMaster.register_class(Tester)
        IoMaster.clear_registry()
        self.assertEqual(IoMaster.registry_import, {})
        self.assertEqual(IoMaster.registry_export, {})

    def test_is_extension_registered__True(self):
        IoMaster.register_class(Tester)
        for _mode in ["import", "export"]:
            with self.subTest():
                self.assertTrue(
                    IoMaster.is_extension_registered(f"{_mode}", mode=_mode)
                )

    def test_is_extension_registered__False(self):
        IoMaster.register_class(Tester)
        for _mode in ["import", "export"]:
            with self.subTest():
                self.assertFalse(IoMaster.is_extension_registered("false", mode=_mode))

    def test_get_registry__import(self):
        _reg = dict(a=1, b=12, c=None)
        IoMaster.registry_import = _reg
        self.assertEqual(_reg, IoMaster._get_registry("import"))

    def test_get_registry__export(self):
        _reg = dict(a=1, b=12, c=None)
        IoMaster.registry_export = _reg
        self.assertEqual(_reg, IoMaster._get_registry("export"))

    def test_get_registry__wrong_key(self):
        with self.assertRaises(ValueError):
            IoMaster._get_registry("other")

    def test_verify_extension_is_registered__okay(self):
        IoMaster.register_class(Tester)
        for _mode in ["import", "export"]:
            with self.subTest():
                IoMaster.verify_extension_is_registered(f"{_mode}", mode=_mode)
            # assert does not raise Exception

    def test_verify_extension_is_registered_import_error(self):
        for _mode in ["import", "export"]:
            with self.subTest():
                with self.assertRaises(KeyError):
                    IoMaster.verify_extension_is_registered("something", mode=_mode)

    def test_get_string_of_formats__empty(self):
        for _mode in ["import", "export"]:
            with self.subTest():
                _str = IoMaster.get_string_of_formats(mode=_mode)
                self.assertEqual("All supported files ()", _str)

    def test_get_string_of_formats__plain(self):
        IoMaster.register_class(Tester)
        for _mode in ["import", "export"]:
            with self.subTest():
                _str = IoMaster.get_string_of_formats(mode=_mode)
                for _ext in getattr(Tester, f"extensions_{_mode}"):
                    self.assertIn(f"*.{_ext}", _str)

    def test_export_to_file(self):
        _fname = utils.get_random_string(24) + ".test"
        _data = np.random.random((10, 10))
        _kws = dict(test_kw=True)
        IoMaster.register_class(Tester)
        IoMaster.export_to_file(_fname, _data, **_kws)
        self.assertEqual(Tester._exported[0], _fname)
        self.assertTrue(np.allclose(Tester._exported[1], _data))
        self.assertEqual(Tester._exported[2], _kws)

    def test_import_from_file(self):
        _fname = utils.get_random_string(24) + ".test"
        _kws = dict(test_kw=True)
        IoMaster.register_class(Tester)
        IoMaster.import_from_file(_fname, **_kws)
        self.assertEqual(Tester._imported[0], _fname)
        self.assertEqual(Tester._imported[1], _kws)


if __name__ == "__main__":
    unittest.main()
