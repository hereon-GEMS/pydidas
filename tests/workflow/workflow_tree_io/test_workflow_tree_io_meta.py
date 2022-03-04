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
__version__ = "0.1.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"


import unittest

from pydidas.workflow.workflow_tree_io import WorkflowTreeIoMeta
from pydidas.unittest_objects.mp_test_app import MpTestApp


class TestWorkflowTreeIoMeta(unittest.TestCase):

    def setUp(self):
        WorkflowTreeIoMeta.clear_registry()

    def tearDown(self):
        ...

    def create_test_class(self):
        class TestClass(metaclass=WorkflowTreeIoMeta):
            extensions = ['.test', '.another_test']
            format_name = 'Test'
            trees = {}

            @classmethod
            def export_to_file(cls, filename, tree):
                cls.trees[filename] = tree

            @classmethod
            def import_from_file(cls, filename):
                if filename in cls.trees:
                    return cls.trees[filename]
                raise KeyError('filename not registered')

        self.test_class = TestClass

    def test_empty(self):
        self.assertEqual(WorkflowTreeIoMeta.registry, dict())

    def test_new__method(self):
        self.assertEqual(WorkflowTreeIoMeta.registry, dict())
        self.create_test_class()
        for _key in self.test_class.extensions:
            self.assertTrue(_key in WorkflowTreeIoMeta.registry)

    def test_import_from_file(self):
        self.assertEqual(WorkflowTreeIoMeta.registry, dict())
        self.create_test_class()
        # just use any object for testing:
        _test_object = MpTestApp()
        self.test_class.trees['dummy.test'] = _test_object
        _new_obj = WorkflowTreeIoMeta.import_from_file('dummy.test')
        self.assertEqual(_test_object, _new_obj)

    def test_export_to_file(self):
        self.assertEqual(WorkflowTreeIoMeta.registry, dict())
        self.create_test_class()
        # just use any object for testing:
        _test_object = MpTestApp()
        WorkflowTreeIoMeta.export_to_file('dummy.test', _test_object)
        self.assertEqual(_test_object, self.test_class.trees['dummy.test'])

    def test_get_string_of_formats__empty(self):
        self.assertEqual(WorkflowTreeIoMeta.get_string_of_formats(),
                         'All supported files (*)')

    def test_get_string_of_formats__with_entry(self):
        self.create_test_class()
        _res = WorkflowTreeIoMeta.get_string_of_formats()
        _target = ('All supported files (*.test *.another_test);;'
                   'Test (*.test *.another_test)')
        self.assertEqual(_res, _target)

    def test_get_registered_formats_and_extensions__empty(self):
        self.assertEqual(WorkflowTreeIoMeta.get_registered_formats(), dict())

    def test_get_registered_formats_and_extensions__with_entry(self):
        self.create_test_class()
        _res = WorkflowTreeIoMeta.get_registered_formats()
        self.assertEqual(
            _res, {self.test_class.format_name: self.test_class.extensions})


if __name__ == "__main__":
    unittest.main()
