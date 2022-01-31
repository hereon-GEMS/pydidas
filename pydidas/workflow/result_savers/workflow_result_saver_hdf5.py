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
"""
Module with the WorkflowTreeExporterBase class which exporters should inherit
from.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.0.1"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['WorkflowResultSaverHdf5']

import os

import h5py

from ...experiment import ExperimentalSetup, ScanSetup
from ...core.utils import create_hdf5_dataset
from .workflow_result_saver_base import WorkflowResultSaverBase


EXP = ExperimentalSetup()
SCAN = ScanSetup()


class WorkflowResultSaverHdf5(WorkflowResultSaverBase):
    """
    Base class for WorkflowTree exporters.
    """
    extensions = ['HDF5']
    format_name = 'HDF5'
    _shapes = []
    _filenames = []
    _save_dir = None
    _metadata_written = False

    @classmethod
    def prepare_files_and_directories(cls, save_dir, shapes, labels):
        """
        Prepare the hdf5 files with the metadata.

        Parameters
        ----------
        title : str
            The scan name or title.
        save_dir : Union[pathlib.Path, str]
            The full path for the data to be saved.
        shapes : dict
            The shapes of the results in form of a dictionary with nodeID
            keys and result values.
        labels : dict
            The labels of the results in form of a dictionary with nodeID
            keys and label values.
        """
        cls._save_dir = save_dir
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
        cls._filenames = {_i: _s.removesuffix('_HDF5') + '.h5' for _i, _s in
                          cls.get_directory_names_from_labels(labels).items()}
        cls._shapes = shapes
        cls._labels = labels
        cls._metadata_written = False
        for _index in cls._shapes:
            cls._create_file_and_populate_metadata(_index)

    @classmethod
    def _create_file_and_populate_metadata(cls, node_id):
        """
        Create a hdf5 file and populate it with the Scan metadata.

        Parameters
        ----------
        node_id : int
            The nodeID.
        """
        _ndim = SCAN.get_param_value('scan_dim')
        _dsets = [
            ['entry', 'title', {'data': cls.scan_title}],
            ['entry', 'label', {'data': cls._labels[node_id]}],
            ['entry', 'definition', {'data': 'custom (NXxbase-aligned)'}],
            ['entry/instrument/source', 'probe', {'data': 'x-ray'}],
            ['entry/instrument/source', 'type', {'data': 'synchrotron'}],
            ['entry/instrument/detector', 'frame_start_number', {'data': (0)}],
            ['entry/instrument/detector', 'x_pixel_size',
             {'data': EXP.get_param_value('detector_pxsizex')}],
            ['entry/instrument/detector', 'y_pixel_size',
             {'data': EXP.get_param_value('detector_pxsizey')}],
            ['entry/instrument/detector', 'distance',
             {'data': EXP.get_param_value('detector_dist')}],
            ['entry/data', 'data', {'shape': cls._shapes[node_id]}],
            ['entry/scan', 'scan_dimension', {'data': _ndim}]]
        scanval = SCAN.get_param_value
        for _dim in range(_ndim):
            _dsets.append([f'entry/scan/dim_{_dim}', 'name',
                           {'data': scanval(f'scan_dir_{_dim + 1}')}])
            _dsets.append([f'entry/scan/dim_{_dim}', 'unit',
                           {'data': scanval(f'unit_{_dim + 1}')}])
            _dsets.append([f'entry/scan/dim_{_dim}', 'range',
                           {'data': SCAN.get_range_for_dim(_dim + 1)}])

        with h5py.File(os.path.join(cls._save_dir, cls._filenames[node_id]),
                       'w') as _file:
            for _group, _name, kws in _dsets:
                create_hdf5_dataset(_file, _group, _name, **kws)
            for _dim in range(_ndim):
                _file[f'entry/data/axis_{_dim}'] = h5py.SoftLink(
                    f'/entry/scan/dim_{_dim}')

    @classmethod
    def export_frame_to_file(cls, index, frame_result_dict, **kwargs):
        """
        Export the results of one frame and store them on disk.

        Parameters
        ----------
        index : int
            The frame index.
        frame_result_dict : dict
            The result dictionary with nodeID keys and result values.
        kwargs : dict
            Any kwargs which should be passed to the udnerlying exporter.
        """
        _indices = SCAN.get_frame_position_in_scan(index)
        if not cls._metadata_written:
            cls.write_metadata_to_files(frame_result_dict)
        for _node_id, _data in frame_result_dict.items():
            with h5py.File(os.path.join(cls._save_dir,
                                        cls._filenames[_node_id]),
                           'r+') as _file:
                _file['entry/data/data'][_indices] = _data

    @classmethod
    def export_full_data_to_file(cls, full_data):
        """
        Export the full dataset to disk,

        Parameters
        ----------
        full_data : dict
            The result dictionary with nodeID keys and result values.
        """
        if not cls._metadata_written:
            _indices = SCAN.get_frame_position_in_scan(0)
            cls.write_metadata_to_files({_id: _data[_indices] for _id, _data
                                         in full_data.items()})
        for _node_id, _data in full_data.items():
            with h5py.File(os.path.join(cls._save_dir,
                                        cls._filenames[_node_id]),
                           'r+') as _file:
                _file['entry/data/data'][()] = _data.array

    @classmethod
    def write_metadata_to_files(cls, frame_result_dict):
        """
        Write the metadata from the WorkflowTree to the individual files
        for each node.

        Parameters
        ----------
        frame_result_dict : dict
            The result dictionary with nodeID keys and result values.
        """
        for _node_id, _data in frame_result_dict.items():
            cls.update_node_metadata(_node_id, _data)
        cls._metadata_written = True

    @classmethod
    def update_node_metadata(cls, index, data):
        """
        Update the metadata for a single node.

        Parameters
        ----------
        index : int
            The nodeID.
        data : pydidas.core.Dataset
            The processed Dataset.
        """
        _ndim = SCAN.get_param_value('scan_dim')
        with h5py.File(os.path.join(cls._save_dir, cls._filenames[index]),
                       'r+') as _file:
            for _dim in range(data.ndim):
                _group = _file['entry/data']
                _axisgroup = _group.create_group(f'axis_{_dim + _ndim}')
                for _key in ['label', 'unit', 'range']:
                    _dict = getattr(data, f'axis_{_key}s')
                    _data = 'None' if _dict[_dim] is None else _dict[_dim]
                    _axisgroup.create_dataset(_key, data=_data)

    @classmethod
    def update_frame_metadata(cls, metadata):
        """
        Update the frame metadata with a separately supplied metadata
        dictionary.

        Parameters
        ----------
        metadata : dict
            The metadata in dictionary form with entries of the form
            node_id: node_metadata.
        """
        _ndim = SCAN.get_param_value('scan_dim')
        for _id, _metadata in metadata.items():
            with h5py.File(os.path.join(cls._save_dir, cls._filenames[_id]),
                           'r+') as _file:
                _ndim_frame = len(_metadata['axis_labels'])
                for _dim in range(_ndim_frame):
                    _group = _file['entry/data']
                    _axisgroup = _group.create_group(f'axis_{_dim + _ndim}')
                    for _key in ['label', 'unit', 'range']:
                        _val = _metadata[f'axis_{_key}s'][_dim]
                        _val = 'None' if _val is None else _val
                        _axisgroup.create_dataset(_key, data=_val)
        cls._metadata_written = True
