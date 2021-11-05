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

import numpy as np

from pydidas import unittest_objects
from pydidas.workflow_tree.result_savers import (
    WorkflowResultSaverBase, WorkflowResultSaverMeta)
from pydidas.workflow_tree import WorkflowTree, WorkflowResults
from pydidas.core import ScanSettings, Dataset

TREE = WorkflowTree()
SCAN = ScanSettings()
RESULTS = WorkflowResults()
META = WorkflowResultSaverMeta
META.reset()

class SAVER(WorkflowResultSaverBase):
    extensions = ['TEST']
    format_name = 'Test'


class TestWorkflowResultSaverBase(unittest.TestCase):

    def setUp(self):
        ...

    def tearDown(self):
        ...

    def test__class_existance(self):
        self.assertIn(WorkflowResultSaverBase, SAVER.__bases__)

    def test_export_to_file(self):
        SAVER.export_to_file(0, {})
        # assert does not raise an Exception

    def test_export_full_data_to_file(self):
        SAVER.export_full_data_to_file({})
        # assert does not raise an Exception

    def test_prepare_files_and_directories(self):
        SAVER.prepare_files_and_directories('Dir', {}, {})
        # assert does not raise an Exception

    def test_get_directory_names_from_labels(self):
        _labels = {0: None, 1: 'some thing', 2: '\nanother name', 3: 'label'}
        _names = SAVER.get_directory_names_from_labels(_labels)
        for _node_id, _name in _names.items():
            self.assertTrue(_name.startswith(f'node_{_node_id:02d}_'))
            self.assertTrue(_name.endswith('_Test'))
            self.assertNotIn(' ', _name)
            self.assertNotIn('\n', _name)

if __name__ == '__main__':
    unittest.main()
