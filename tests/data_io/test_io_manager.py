# This file is part of pydidas.
#
# Copyright 2023 - 2024, Helmholtz-Zentrum Hereon
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
__copyright__ = "Copyright 2023 - 2024, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"


import unittest

import numpy as np

from pydidas.core import UserConfigError, utils
from pydidas.data_io import IoManager


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
        return np.zeros((10, 10))


class TestIoManager(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._stored_exts_import = IoManager.registry_import.copy()
        cls._stored_exts_export = IoManager.registry_export.copy()

    @classmethod
    def tearDownClass(cls):
        IoManager.registry_import = cls._stored_exts_import
        IoManager.registry_export = cls._stored_exts_export

    def setUp(self):
        IoManager.clear_registry()

    def tearDown(self): ...

    def test_register_class__plain(self):
        IoManager.register_class(Tester)
        for _ext in Tester.extensions_export:
            self.assertEqual(IoManager.registry_export[_ext], Tester)
        for _ext in Tester.extensions_import:
            self.assertEqual(IoManager.registry_import[_ext], Tester)

    def test_register_class__add_class_and_verify_entries_not_deleted(self):
        IoManager.registry_import = {".no_ext": None}
        IoManager.register_class(Tester)
        self.assertIsNone(IoManager.registry_import[".no_ext"])

    def test_register_class__add_class_and_overwrite_old_entry_import(self):
        IoManager.registry_import = {"test": None}
        IoManager.register_class(Tester, update_registry=True)
        self.assertEqual(IoManager.registry_import["test"], Tester)

    def test_register_class__add_class_and_overwrite_old_entry_export(self):
        IoManager.registry_export = {"test": None}
        IoManager.register_class(Tester, update_registry=True)
        self.assertEqual(IoManager.registry_import["test"], Tester)

    def test_register_class__add_and_keep_old_entry_import(self):
        IoManager.registry_import = {"test": None}
        with self.assertRaises(KeyError):
            IoManager.register_class(Tester, update_registry=False)

    def test_register_class__add_and_keep_old_entry_export(self):
        IoManager.registry_export = {"test": None}
        with self.assertRaises(KeyError):
            IoManager.register_class(Tester, update_registry=False)

    def test_clear_registry(self):
        IoManager.register_class(Tester)
        IoManager.clear_registry()
        self.assertEqual(IoManager.registry_import, {})
        self.assertEqual(IoManager.registry_export, {})

    def test_is_extension_registered__True(self):
        IoManager.register_class(Tester)
        for _mode in ["import", "export"]:
            with self.subTest():
                self.assertTrue(
                    IoManager.is_extension_registered(f"{_mode}", mode=_mode)
                )

    def test_is_extension_registered__False(self):
        IoManager.register_class(Tester)
        for _mode in ["import", "export"]:
            with self.subTest():
                self.assertFalse(IoManager.is_extension_registered("false", mode=_mode))

    def test_get_registry__import(self):
        _reg = dict(a=1, b=12, c=None)
        IoManager.registry_import = _reg
        self.assertEqual(_reg, IoManager._get_registry("import"))

    def test_get_registry__export(self):
        _reg = dict(a=1, b=12, c=None)
        IoManager.registry_export = _reg
        self.assertEqual(_reg, IoManager._get_registry("export"))

    def test_get_registry__wrong_key(self):
        with self.assertRaises(ValueError):
            IoManager._get_registry("other")

    def test_verify_extension_is_registered__okay(self):
        IoManager.register_class(Tester)
        for _mode in ["import", "export"]:
            with self.subTest():
                IoManager.verify_extension_is_registered(f"{_mode}", mode=_mode)
            # assert does not raise Exception

    def test_verify_extension_is_registered_import_error(self):
        for _mode in ["import", "export"]:
            with self.subTest():
                with self.assertRaises(UserConfigError):
                    IoManager.verify_extension_is_registered("something", mode=_mode)

    def test_get_string_of_formats__empty(self):
        for _mode in ["import", "export"]:
            with self.subTest():
                _str = IoManager.get_string_of_formats(mode=_mode)
                self.assertEqual("All supported files ()", _str)

    def test_get_string_of_formats__plain(self):
        IoManager.register_class(Tester)
        for _mode in ["import", "export"]:
            with self.subTest():
                _str = IoManager.get_string_of_formats(mode=_mode)
                for _ext in getattr(Tester, f"extensions_{_mode}"):
                    self.assertIn(f"*.{_ext}", _str)

    def test_export_to_file(self):
        _fname = utils.get_random_string(24) + ".test"
        _data = np.random.random((10, 10))
        _kws = dict(test_kw=True)
        IoManager.register_class(Tester)
        IoManager.export_to_file(_fname, _data, **_kws)
        self.assertEqual(Tester._exported[0], _fname)
        self.assertTrue(np.allclose(Tester._exported[1], _data))
        self.assertEqual(Tester._exported[2], _kws)

    def test_import_from_file(self):
        _fname = utils.get_random_string(24) + ".test"
        _kws = dict(test_kw=True)
        IoManager.register_class(Tester)
        IoManager.import_from_file(_fname, **_kws)
        self.assertEqual(Tester._imported[0], _fname)
        self.assertEqual(Tester._imported[1], _kws)

    def test_import_from_file__w_forced_dim(self):
        _fname = utils.get_random_string(24) + ".test"
        IoManager.register_class(Tester)
        with self.assertRaises(UserConfigError):
            IoManager.import_from_file(_fname, forced_dimension=5)


if __name__ == "__main__":
    unittest.main()
