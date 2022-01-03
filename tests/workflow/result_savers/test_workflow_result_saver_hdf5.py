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
import tempfile
import os
import shutil
import random

import h5py
import numpy as np

from pydidas.core import Dataset
from pydidas.experiment import ScanSetup
from pydidas.core.utils import get_random_string
from pydidas.workflow.result_savers import WorkflowResultSaverMeta
from pydidas.workflow import WorkflowTree, WorkflowResults
from pydidas.workflow.result_savers.workflow_result_saver_hdf5 import (
    WorkflowResultSaverHdf5)


TREE = WorkflowTree()
SCAN = ScanSetup()
RESULTS = WorkflowResults()
META = WorkflowResultSaverMeta
H5SAVER = WorkflowResultSaverHdf5


class TestWorkflowResultSaverHdf5(unittest.TestCase):

    def setUp(self):
        SCAN.set_param_value('scan_dim', 3)
        for d in range(1, 4):
            SCAN.set_param_value(f'n_points_{d}', random.choice([3, 5, 7, 8]))
            SCAN.set_param_value(f'delta_{d}',
                                 random.choice([0.1, 0.5, 1, 1.5]))
            SCAN.set_param_value(f'offset_{d}', random.choice([-0.1, 0.5, 1]))
            SCAN.set_param_value(f'scan_dir_{d}', get_random_string(12))
        self._dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self._dir)

    def prepare_with_defaults(self):
        _scan_shape = tuple(SCAN.get_param_value(f'n_points_{i}')
                            for i in [1, 2, 3])
        self._shapes = {1: _scan_shape + (12, 7), 2: _scan_shape + (23,),
                   3: _scan_shape + (1, 3, 7)}
        self._labels = {1: 'Test', 2: 'not again', 3: 'another'}
        self._filenames = {1: 'node_01_Test.h5', 2: 'node_02_not_again.h5',
                      3: 'node_03_another.h5'}
        self._resdir = os.path.join(self._dir, get_random_string(8))
        H5SAVER.prepare_files_and_directories(self._resdir, self._shapes,
                                              self._labels)

    def get_datasets(self, start_dim=3):
        return {_key: Dataset(np.random.random(_shape[start_dim:]))
                for _key, _shape in self._shapes.items()}

    def populate_metadata(self, dataset):
        _labels = {_key: get_random_string(8) for _key in dataset.axis_labels}
        _units = {_key: get_random_string(3) for _key in dataset.axis_units}
        _ranges = {_key: random.random() * np.arange(_len) + random.random()
                   for _key, _len in enumerate(dataset.shape)}
        for _axis in _labels:
            dataset.axis_labels[_axis] = _labels[_axis]
            dataset.axis_units[_axis] = _units[_axis]
            dataset.axis_ranges[_axis] = _ranges[_axis]
        return dataset, _labels, _units, _ranges

    def test_class(self):
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

    def test_update_node_metadata__with_None(self):
        self.prepare_with_defaults()
        _data = {_key: Dataset(np.random.random(_shape[3:]))
                  for _key, _shape in self._shapes.items()}
        _data1 = _data[1]
        H5SAVER.update_node_metadata(1, _data1)

    def test_update_node_metadata__with_entries(self):
        self.prepare_with_defaults()
        _data = {_key: Dataset(np.random.random(_shape[3:]))
                  for _key, _shape in self._shapes.items()}
        _data[1], _labels, _units, _ranges = self.populate_metadata(_data[1])
        H5SAVER.update_node_metadata(1, _data[1])
        _fname = os.path.join(self._resdir, self._filenames[1])
        with h5py.File(_fname, 'r') as _file:
            for _ax in [3, 4]:
                _axentry = _file[f'entry/data/axis_{_ax}']
                self.assertEqual(_axentry['label'][()].decode('UTF-8'),
                                  _labels[_ax - 3])
                self.assertEqual(_axentry['unit'][()].decode('UTF-8'),
                                  _units[_ax - 3])
                self.assertTrue(np.allclose(_axentry['range'][()],
                                            _ranges[_ax - 3]))

    def test_update_frame_metadata__standard(self):
        self.prepare_with_defaults()
        _data = {_key: Dataset(np.random.random(_shape[3:]))
                  for _key, _shape in self._shapes.items()}
        for _key in _data:
            _data[_key], _, _, _ = self.populate_metadata(_data[_key])
        _metadata = {_key: dict(axis_units=_item.axis_units,
                                axis_labels=_item.axis_labels,
                                axis_ranges=_item.axis_ranges)
                     for _key, _item in _data.items()}
        H5SAVER.update_frame_metadata(_metadata)
        for _node_id in self._shapes:
            _fname = os.path.join(self._resdir, self._filenames[_node_id])
            with h5py.File(_fname, 'r') as _file:
                for _ax in range(3, _data[_node_id].ndim):
                    _axentry = _file[f'entry/data/axis_{_ax}']
                    self.assertEqual(
                        _axentry['label'][()].decode('UTF-8'),
                        _metadata[_node_id]['axis_labels'][_ax - 3])
                    self.assertEqual(
                        _axentry['unit'][()].decode('UTF-8'),
                        _metadata[_node_id]['axis_units'][_ax - 3])
                    self.assertEqual(
                        _axentry['range'][()].decode('UTF-8'),
                        _metadata[_node_id]['axis_ranges'][_ax - 3])

    def test_write_metadata_to_files(self):
        self.prepare_with_defaults()
        _data = self.get_datasets()
        _metadata = {}
        for _node_id in self._shapes:
            _data[_node_id], _labels, _units, _ranges = (
                self.populate_metadata(_data[_node_id]))
            _metadata[_node_id] = dict(labels=_labels, units=_units,
                                        ranges=_ranges)
        H5SAVER.write_metadata_to_files(_data)
        for _node_id in self._shapes:
            _fname = os.path.join(self._resdir, self._filenames[_node_id])
            with h5py.File(_fname, 'r') as _file:
                for _ax in range(3, _data[_node_id].ndim):
                    _axentry = _file[f'entry/data/axis_{_ax}']
                    self.assertEqual(_axentry['label'][()].decode('UTF-8'),
                                      _metadata[_node_id]['labels'][_ax - 3])
                    self.assertEqual(_axentry['unit'][()].decode('UTF-8'),
                                      _metadata[_node_id]['units'][_ax - 3])
                    self.assertTrue(np.allclose(
                        _axentry['range'][()],
                        _metadata[_node_id]['ranges'][_ax - 3]))

    def test_export_full_data_to_file(self):
        self.prepare_with_defaults()
        _data = self.get_datasets(start_dim=0)
        H5SAVER.export_full_data_to_file(_data)
        for _node_id in self._shapes:
            _fname = os.path.join(self._resdir, self._filenames[_node_id])
            with h5py.File(_fname, 'r') as _file:
                _writtendata = _file['entry/data/data'][()]
            self.assertTrue(np.allclose(_data[_node_id], _writtendata))

    def test_export_frame_to_file(self):
        self.prepare_with_defaults()
        _data = self.get_datasets()
        _index = 23
        _scanindex = SCAN.get_frame_position_in_scan(_index)
        H5SAVER.export_frame_to_file(_index, _data)
        for _node_id in self._shapes:
            _fname = os.path.join(self._resdir, self._filenames[_node_id])
            with h5py.File(_fname, 'r') as _file:
                _written_data = _file['entry/data/data'][_scanindex]
            self.assertTrue(np.allclose(_written_data, _data[_node_id]))


if __name__ == '__main__':
    unittest.main()
