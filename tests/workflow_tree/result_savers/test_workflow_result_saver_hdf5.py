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
import tempfile
import os
import shutil
import random

import h5py
import numpy as np

from pydidas import unittest_objects
from pydidas.workflow_tree.result_savers import (
    WorkflowResultSaverBase, WorkflowResultSaverMeta)
from pydidas.workflow_tree import WorkflowTree, WorkflowResults
from pydidas.core import ScanSettings, Dataset
from pydidas.workflow_tree.result_savers.workflow_result_saver_hdf5 import (
    WorkflowResultSaverHdf5)
from pydidas.unittest_objects import get_random_string


TREE = WorkflowTree()
SCAN = ScanSettings()
SCAN.set_param_value('scan_dim', 3)
for d in range(1, 4):
    SCAN.set_param_value(f'n_points_{d}', random.choice([3, 5, 7, 8]))
    SCAN.set_param_value(f'delta_{d}', random.choice([0.1, 0.5, 1, 1.5]))
    SCAN.set_param_value(f'offset_{d}', random.choice([-0.1, 0.5, 1]))
    SCAN.set_param_value(f'scan_dir_{d}', get_random_string(12))
_scan_shape = tuple(SCAN.get_param_value(f'n_points_{i}') for i in [1, 2, 3])

RESULTS = WorkflowResults()
META = WorkflowResultSaverMeta
H5SAVER = WorkflowResultSaverHdf5

class TestWorkflowResultSaverHdf5(unittest.TestCase):

    def setUp(self):
        self._dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self._dir)

    def prepare_with_defaults(self):
        self._shapes = {1: _scan_shape + (12, 7), 2: _scan_shape + (23,),
                   3: _scan_shape + (1, 3, 7)}
        self._labels = {1: 'Test', 2: 'not again', 3: 'another'}
        self._filenames = {1: 'node_01_Test.h5', 2: 'node_02_not_again.h5',
                      3: 'node_03_another.h5'}
        self._resdir = os.path.join(self._dir, get_random_string(8))
        H5SAVER.prepare_files_and_directories(self._resdir, self._shapes,
                                              self._labels)


    def test__class(self):
        self.assertEqual(H5SAVER.__class__, META)

    def test_prepare_files_and_directories(self):
        self.prepare_with_defaults()
        self.assertTrue(os.path.exists(self._resdir))
        self.assertEqual(H5SAVER._shapes, self._shapes)
        self.assertEqual(H5SAVER._labels, self._labels)
        for _key in self._shapes:
            _fname = H5SAVER._filenames[_key]
            self.assertEqual(_fname, self._filenames[_key])
            self.assertTrue(os.path.exists(os.path.join(self._resdir, _fname)))

    def test_create_file_and_populate_metadata(self):
        _node_id = 1
        self.prepare_with_defaults()
        H5SAVER._create_file_and_populate_metadata(_node_id)
        with (h5py.File(os.path.join(self._resdir, self._filenames[1]), 'r')
                as _file):
            _data = _file['entry/data/data']
            self.assertEqual(_data.shape, self._shapes[1])
            self.assertIsInstance(_data, h5py.Dataset)

    # def test_update_node_metadata__with_None(self):
    #     self.prepare_with_defaults()
    #     _data = {_key: Dataset(np.random.random(_shape[3:]))
    #              for _key, _shape in self._shapes.items()}
    #     _data1 = _data[1]
    #     H5SAVER.update_node_metadata(1, _data1)

    # def test_update_node_metadata__with_entries(self):
    #     self.prepare_with_defaults()
    #     _data = {_key: Dataset(np.random.random(_shape[3:]))
    #              for _key, _shape in self._shapes.items()}
    #     _data1 = _data[1]
    #     _labels = {3: get_random_string(8), 4: get_random_string(8)}
    #     _units = {3: get_random_string(3), 4: get_random_string(3)}
    #     _range = {3: np.arange(self._shapes[1][3]),
    #               4: 3 - np.arange(self._shapes[1][4])}
    #     for _axis in [3, 4]:
    #         _data1.axis_labels[_axis] = _labels[_axis]
    #         _data1.axis_units[_axis] = _units[_axis]
    #         _data1.axis_range[_axis] = _range[_axis]
    #     H5SAVER.update_node_metadata(1, _data1)

    # def test_export_to_file(self):
    #     self.prepare_with_defaults()
    #     _data = {_key: Dataset(np.random.random(_shape[3:]))
    #              for _key, _shape in self._shapes.items()}
    #     _index = 23
    #     _scanindex = SCAN.get_frame_position_in_scan(_index)
    #     H5SAVER.export_to_file(_index, _data)
    #     for _node_id in self._shapes:
    #         _fname = os.path.join(self._resdir, self._filenames[_node_id])
    #         with h5py.File(_fname, 'r') as _file:
    #             _written_data = _file['entry/data/data'][_scanindex]
    #         self.assertTrue(np.allclose(_written_data, _data[_node_id]))

    # def test_export_full_data_to_file(self):
    #     SAVER.export_full_data_to_file({})
    #     # assert does not raise an Exception

    # def test_prepare_files_and_directories(self):
    #     SAVER.prepare_files_and_directories('Dir', {}, {})
    #     # assert does not raise an Exception

    # def test_get_directory_names_from_labels(self):
    #     _labels = {0: None, 1: 'some thing', 2: '\nanother name', 3: 'label'}
    #     _names = SAVER.get_directory_names_from_labels(_labels)
    #     for _node_id, _name in _names.items():
    #         self.assertTrue(_name.startswith(f'node_{_node_id:02d}_'))
    #         self.assertTrue(_name.endswith('_Test'))
    #         self.assertNotIn(' ', _name)
    #         self.assertNotIn('\n', _name)

if __name__ == '__main__':
    unittest.main()
