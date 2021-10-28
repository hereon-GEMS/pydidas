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

import os
import unittest
import tempfile
import shutil
import time
import random
from pathlib import Path

import numpy as np
import h5py
from PyQt5 import QtCore, QtTest

from pydidas.apps import ExecuteWorkflowApp
from pydidas.core import (ParameterCollection, Dataset,
                          get_generic_parameter, CompositeImage, ScanSettings)
from pydidas._exceptions import AppConfigError
from pydidas.workflow_tree import WorkflowTree, WorkflowResults
from pydidas.unittest_objects import DummyLoader, DummyProc

TREE = WorkflowTree()
SCAN = ScanSettings()
RESULTS = WorkflowResults()


class TestExecuteWorkflowApp(unittest.TestCase):

    def setUp(self):
        self._path = tempfile.mkdtemp()
        self.generate_tree()
        self.generate_scan()

    def tearDown(self):
        shutil.rmtree(self._path)

    def generate_tree(self):
        TREE.clear()
        TREE.create_and_add_node(DummyLoader())
        TREE.create_and_add_node(DummyProc())
        TREE.create_and_add_node(DummyProc(), parent=TREE.root)

    def generate_scan(self):
        SCAN.restore_all_defaults(True)
        SCAN.set_param_value('scan_dim', 3)
        self._nscan = (random.choice([5,7,9,11]), random.choice([2, 4, 5]),
                       random.choice([5,6,7,8]))
        self._scandelta = (0.1, -0.2, 1.1)
        self._scanoffset = (-5, 0, 1.2)
        for i in range(1, 4):
            SCAN.set_param_value('scan_dim', 3)
            SCAN.set_param_value(f'n_points_{i}', self._nscan[i-1])
            SCAN.set_param_value(f'delta_{i}', self._scandelta[i-1])
            SCAN.set_param_value(f'offset_{i}', self._scanoffset[i-1])

    def test_creation(self):
        app = ExecuteWorkflowApp()
        self.assertIsInstance(app, ExecuteWorkflowApp)

    def test_creation_with_args(self):
        _autosave = get_generic_parameter('autosave_results')
        _autosave.value = True
        app = ExecuteWorkflowApp(_autosave)
        self.assertTrue(app.get_param_value('autosave_results'))

    def test_creation_with_cmdargs(self):
        ExecuteWorkflowApp.parse_func = lambda x: {'autosave_results': True}
        app = ExecuteWorkflowApp()
        self.assertTrue(app.get_param_value('autosave_results'))



if __name__ == "__main__":
    unittest.main()
