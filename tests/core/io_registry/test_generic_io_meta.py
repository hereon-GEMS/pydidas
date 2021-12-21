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
__version__ = "0.0.1"
__maintainer__ = "Malte Storm"
__status__ = "Development"


import unittest

from pydidas.core.io_registry import GenericIoMeta


class TestGenericIoMeta(unittest.TestCase):

    def setUp(self):
        GenericIoMeta.clear_registry()

    def tearDown(self):
        GenericIoMeta.clear_registry()

    def create_test_class(self):
        class TestClass(metaclass=GenericIoMeta):
            extensions = ['.dummy', '.test']
            format_name = 'TEST'
        self.test_class = TestClass()

    def create_test_class2(self):
        class TestClass2(metaclass=GenericIoMeta):
            extensions = ['.test2']
            format_name = 'Test2'
        self.test_class2 = TestClass2()

    def get_unregistered_test_class(self):
        class TestClass3():
            extensions = ['.test3', '.test4']
            format_name = 'Test3'
        return TestClass3

    def test_empty(self):
        self.assertEqual(GenericIoMeta.registry, dict())

    def test_get_registered_formats__empty(self):
        self.assertEqual(
            GenericIoMeta.get_registered_formats(), {})

    def test_get_registered_formats__with_entry(self):
        self.create_test_class()
        _formats = GenericIoMeta.get_registered_formats()
        _target = {self.test_class.format_name: self.test_class.extensions}
        self.assertEqual(_formats, _target)

    def test_get_string_of_formats(self):
        self.create_test_class()
        _str = GenericIoMeta.get_string_of_formats()
        _target = 'All supported files (*.dummy *.test);;TEST (*.dummy *.test)'
        self.assertEqual(_str, _target)

    def test_is_extension_registered__True(self):
        self.create_test_class()
        self.assertTrue(
            GenericIoMeta.is_extension_registered('.dummy'))

    def test_is_extension_registered__False(self):
        self.create_test_class()
        self.assertFalse(
            GenericIoMeta.is_extension_registered('none'))

    def test_verify_extension_is_registered__correct(self):
        self.create_test_class()
        GenericIoMeta.verify_extension_is_registered('.test')
        # assert does not raise an error

    def test_verify_extension_is_registered__incorrect(self):
        self.create_test_class()
        with self.assertRaises(KeyError):
            GenericIoMeta.verify_extension_is_registered(
                'none')

    def test_new__method(self):
        self.assertEqual(GenericIoMeta.registry, dict())
        self.create_test_class()
        for _key in self.test_class.extensions:
            self.assertTrue(_key in GenericIoMeta.registry)

    def test_new__method__multiple(self):
        self.assertEqual(GenericIoMeta.registry, dict())
        self.create_test_class()
        self.create_test_class2()
        for _key in self.test_class.extensions + self.test_class2.extensions:
            self.assertTrue(_key in GenericIoMeta.registry)

    def test_clear_registry(self):
        self.assertEqual(GenericIoMeta.registry, dict())
        self.create_test_class()
        GenericIoMeta.clear_registry()
        self.assertEqual(GenericIoMeta.registry, dict())

    def test_register_class__plain(self):
        self.assertEqual(GenericIoMeta.registry, dict())
        klass = self.get_unregistered_test_class()
        GenericIoMeta.register_class(klass)
        for _key in klass.extensions:
            self.assertTrue(_key in GenericIoMeta.registry)

    def test_register_class__same_ext_no_update(self):
        self.assertEqual(GenericIoMeta.registry, dict())
        klass = self.get_unregistered_test_class()
        GenericIoMeta.register_class(klass)
        with self.assertRaises(KeyError):
            GenericIoMeta.register_class(klass)

    def test_register_class__same_ext_and_update(self):
        self.assertEqual(GenericIoMeta.registry, dict())
        klass = self.get_unregistered_test_class()
        GenericIoMeta.register_class(klass)
        GenericIoMeta.register_class(klass, update_registry=True)
        for _key in klass.extensions:
            self.assertTrue(_key in GenericIoMeta.registry)


if __name__ == "__main__":
    unittest.main()
