# This file is part of pydidas.
#
# Copyright 2023, Helmholtz-Zentrum Hereon
# SPDX-License-Identifier: GPL-3.0-only
#
# pydidas is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 3 as published by
# the Free Software Foundation.
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


import unittest

from pydidas.contexts import ScanContext
from pydidas.workflow import WorkflowResults, WorkflowTree
from pydidas.workflow.result_io import WorkflowResultIoBase, WorkflowResultIoMeta


TREE = WorkflowTree()
SCAN = ScanContext()
RESULTS = WorkflowResults()
META = WorkflowResultIoMeta


class TestWorkflowResultIoBase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._meta_registry = META.registry.copy()
        cls._node_information = {
            5: {"test": 42, "42": "test", "node_label": "__\n _ \t pretty@!%ugly_name"},
            7: {"test": 12, "42": "spam", "node_label": "a_beautiful_name"},
        }
        META.reset()

        class SAVER(WorkflowResultIoBase):
            extensions = ["TEST"]
            default_extension = "Test"
            format_name = "Test"
            _node_information = cls._node_information

        cls.SAVER = SAVER

    @classmethod
    def tearDownClass(cls):
        META.reset()
        META.registry = cls._meta_registry.copy()

    def test_class_existance(self):
        self.assertIn(WorkflowResultIoBase, self.SAVER.__bases__)

    def test_get_attribute_dict(self):
        _name = "test"
        _dict = self.SAVER.get_attribute_dict(_name)
        self.assertEqual(
            _dict, {_id: self._node_information[_id][_name] for _id in _dict}
        )

    def test_get_attribute_value(self):
        _name = "test"
        _id = 5
        _val = self.SAVER.get_node_attribute(_id, _name)
        self.assertEqual(_val, self._node_information[_id][_name])

    def test_export_frame_to_file(self):
        with self.assertRaises(NotImplementedError):
            self.SAVER.export_frame_to_file(0, {})

    def test_export_full_data_to_file(self):
        with self.assertRaises(NotImplementedError):
            self.SAVER.export_full_data_to_file({})

    def test_prepare_files_and_directories(self):
        with self.assertRaises(NotImplementedError):
            self.SAVER.prepare_files_and_directories("Dir", {})
        # assert does not raise an Exception

    def test_get_filenames_from_labels(self):
        _names = self.SAVER.get_filenames_from_labels()
        self.assertEqual(
            _names,
            {5: "node_05_pretty_ugly_name.Test", 7: "node_07_a_beautiful_name.Test"},
        )

    def test_get_filenames_from_labels__with_labels(self):
        _labels = {_id: self._node_information[_id]["node_label"] for _id in [5, 7]}
        _names = self.SAVER.get_filenames_from_labels(_labels)
        self.assertEqual(
            _names,
            {5: "node_05_pretty_ugly_name.Test", 7: "node_07_a_beautiful_name.Test"},
        )

    def test_import_results_from_file(self):
        with self.assertRaises(NotImplementedError):
            self.SAVER.import_results_from_file("dummy")


if __name__ == "__main__":
    unittest.main()
