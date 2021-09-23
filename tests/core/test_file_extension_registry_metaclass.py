# This file is part of pydidas.

# pydidas is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# Pydidas is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with Pydidas. If not, see <http://www.gnu.org/licenses/>.

"""Unit tests for pydidas modules."""

__author__      = "Malte Storm"
__copyright__   = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.0.1"
__maintainer__ = "Malte Storm"
__status__ = "Development"

import unittest

from pydidas.core import FileExtensionRegistryMetaclass


class TestFileExtensionRegistryMetaclass(unittest.TestCase):

    def setUp(self):
        FileExtensionRegistryMetaclass.clear_registry()
        ...

    def tearDown(self):
        ...

    def create_test_class(self):
        class TestClass(metaclass=FileExtensionRegistryMetaclass):
            extensions = ['dummy', 'test']
        self.test_class = TestClass()

    def create_test_class2(self):
        class TestClass2(metaclass=FileExtensionRegistryMetaclass):
            extensions = ['test2']
        self.test_class2 = TestClass2()

    def get_unregistered_test_class(self):
        class TestClass3():
            extensions = ['test3', 'test4']
        return TestClass3

    def test_empty(self):
        self.assertEqual(FileExtensionRegistryMetaclass.registry, dict())

    def test_is_extension_registered__True(self):
        self.create_test_class()
        self.assertTrue(
            FileExtensionRegistryMetaclass.is_extension_registered('dummy'))

    def test_is_extension_registered__False(self):
        self.create_test_class()
        self.assertFalse(
            FileExtensionRegistryMetaclass.is_extension_registered('none'))

    def test_verify_extension_is_registered__correct(self):
        self.create_test_class()
        FileExtensionRegistryMetaclass.verify_extension_is_registered('test')
        # assert does not raise an error

    def test_verify_extension_is_registered__incorrect(self):
        self.create_test_class()
        with self.assertRaises(KeyError):
            FileExtensionRegistryMetaclass.verify_extension_is_registered(
                'none')

    def test__new__method(self):
        self.assertEqual(FileExtensionRegistryMetaclass.registry, dict())
        self.create_test_class()
        for _key in self.test_class.extensions:
            self.assertTrue(_key in FileExtensionRegistryMetaclass.registry)

    def test__new__method__multiple(self):
        self.assertEqual(FileExtensionRegistryMetaclass.registry, dict())
        self.create_test_class()
        self.create_test_class2()
        for _key in self.test_class.extensions + self.test_class2.extensions:
            self.assertTrue(_key in FileExtensionRegistryMetaclass.registry)


    def test_clear_registry(self):
        self.assertEqual(FileExtensionRegistryMetaclass.registry, dict())
        self.create_test_class()
        FileExtensionRegistryMetaclass.clear_registry()
        self.assertEqual(FileExtensionRegistryMetaclass.registry, dict())

    def test_register_class__plain(self):
        self.assertEqual(FileExtensionRegistryMetaclass.registry, dict())
        klass = self.get_unregistered_test_class()
        FileExtensionRegistryMetaclass.register_class(klass)
        for _key in klass.extensions:
            self.assertTrue(_key in FileExtensionRegistryMetaclass.registry)

    def test_register_class__same_ext_no_update(self):
        self.assertEqual(FileExtensionRegistryMetaclass.registry, dict())
        klass = self.get_unregistered_test_class()
        FileExtensionRegistryMetaclass.register_class(klass)
        with self.assertRaises(KeyError):
            FileExtensionRegistryMetaclass.register_class(klass)

    def test_register_class__same_ext_and_update(self):
        self.assertEqual(FileExtensionRegistryMetaclass.registry, dict())
        klass = self.get_unregistered_test_class()
        FileExtensionRegistryMetaclass.register_class(klass)
        FileExtensionRegistryMetaclass.register_class(klass,
                                                      update_registry=True)
        for _key in klass.extensions:
            self.assertTrue(_key in FileExtensionRegistryMetaclass.registry)


if __name__ == "__main__":
    unittest.main()
