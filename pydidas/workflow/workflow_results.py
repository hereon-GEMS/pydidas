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
The workflow_results module includes the WorkflowResults singleton class for
storing and accessing the composite results of the processing.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.0.1"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['WorkflowResults']

import os
import re

import numpy as np
from PyQt5 import QtCore

from ..core import Dataset, SingletonFactory
from ..experiment import ScanSetup
from .workflow_tree import WorkflowTree
from .result_savers import WorkflowResultSaverMeta


RESULT_SAVER = WorkflowResultSaverMeta
SCAN = ScanSetup()
TREE = WorkflowTree()


class _WorkflowResults(QtCore.QObject):
    """
    WorkflowResults is a class for handling composite data which spans
    multiple datasets with multiple dimensions each. Results are referenced
    by the node ID of the data's producer.
    """
    new_results = QtCore.pyqtSignal()

    def __init__(self):
        super().__init__()
        self.clear_all_results()

    def update_shapes_from_scan_and_workflow(self):
        """
        Update the shape of the results by querying ScanSetup and
        WorkflowTree for their current dimensions and shapes.
        """
        self.clear_all_results()
        _dim = SCAN.get_param_value('scan_dim')
        _points = tuple(SCAN.get_param_value(f'n_points_{_n}')
                        for _n in range(1, _dim + 1))
        _results = TREE.get_all_result_shapes()
        _shapes = {_key: _points + _shape for _key, _shape in _results.items()}
        for _node_id, _shape in _shapes.items():
            _dset = Dataset(np.zeros(_shape, dtype=np.float32))
            for index in range(_dim):
                _label, _unit, _range = SCAN.get_metadata_for_dim(index + 1)
                _dset.axis_labels[index] = _label
                _dset.axis_units[index] = _unit
                _dset.axis_ranges[index] = _range
            self.__composites[_node_id] = _dset
            self._config['shapes'] = _shapes
            self._config['labels'][_node_id] = (
                TREE.nodes[_node_id].plugin.get_param_value('label'))
        self.__source_hash = hash((hash(SCAN), hash(TREE)))

    def clear_all_results(self):
        """
        Clear all interally stored results and reset the instance attributes.
        """
        self.__composites = {}
        self.__source_hash = hash((hash(SCAN), hash(TREE)))
        self._config = {'shapes': {},
                        'labels': {},
                        'metadata_complete': False}

    def update_frame_metadata(self, metadata):
        """
        Manually supply metadata for the non-scan dimensions of the results
        and update the stored metadata.

        Parameters
        ----------
        metadata : dict
            The metadata in form of a dictionary with nodeID keys and dict
            items containing the axis_units, -_labels, and -_scales keys with
            the associated data.
        """
        for node_id, _meta in metadata.items():
            _dim_offset = SCAN.get_param_value('scan_dim')
            for _key, _items in _meta.items():
                _obj = getattr(self.__composites[node_id], _key)
                for _dim, _val in _items.items():
                    _obj[_dim + _dim_offset] = _val
        self._config['metadata_complete'] = True

    def store_results(self, index, results):
        """
        Store results from one frame in the WorkflowResults.

        Note: If write_to_disk is enabled, please be advised that this may
        slow down the WorkflowResults

        Parameters
        ----------
        index : int
            The frame index
        results: dict
            The results as dictionary with entries of the type
            <node_id: array>.
        """
        if not self._config['metadata_complete']:
            self.__update_composite_metadata(results)
        _scan_index = SCAN.get_frame_position_in_scan(index)
        for _key, _val in results.items():
            self.__composites[_key][_scan_index] = _val
        self.new_results.emit()

    def __update_composite_metadata(self, results):
        """
        Update the metadata of the composites with the

        Parameters
        ----------
        results : dict
            The results for a single processing step.
        """
        for node_id, result in results.items():
            if not isinstance(result, Dataset):
                continue
            _dim_offset = SCAN.get_param_value('scan_dim')
            for _dim in range(result.ndim):
                self.__composites[node_id].axis_labels[_dim + _dim_offset] = (
                    result.axis_labels[_dim])
                self.__composites[node_id].axis_units[_dim + _dim_offset] = (
                    result.axis_units[_dim])
                self.__composites[node_id].axis_ranges[_dim + _dim_offset] = (
                    result.axis_ranges[_dim])
        self._config['metadata_complete'] = True

    @property
    def shapes(self):
        """
        Return the shapes of the results in form of a dictionary.

        Returns
        -------
        dict
            A dictionary with entries of the form <node_id: results_shape>
        """
        return self._config['shapes'].copy()

    @property
    def labels(self):
        """
        Return the labels of the results in form of a dictionary.

        Returns
        -------
        dict
            A dictionary with entries of the form <node_id: label>
        """
        return self._config['labels'].copy()

    @property
    def ndims(self):
        """
        Return the number of dimensions of the results in form of a dictionary.

        Returns
        -------
        dict
            A dictionary with entries of the form <node_id: n_dim>
        """
        return {_key: self.__composites[_key].ndim
                for _key in self.__composites}

    @property
    def source_hash(self):
        """
        Get the source hash from the input WorkflowTree ans ScanSetup.

        Returns
        -------
        int
            The hash value of the combined input data.
        """
        self.__source_hash = hash((hash(SCAN), hash(TREE)))
        return self.__source_hash

    def get_results(self, node_id):
        """
        Get the combined results for the requested node_id.

        Parameters
        ----------
        node_id : int
            The node ID for which results should be retured.

        Returns
        -------
        pydidas.core.Dataset
            The combined results of all frames for a specific node.
        """
        return self.__composites[node_id]

    def get_results_for_flattened_scan(self, node_id):
        """
        Get the combined results for the requested node_id with all scan
        dimensions flatted into a timeline

        Parameters
        ----------
        node_id : int
            The node ID for which results should be retured.

        Returns
        -------
        pydidas.core.Dataset
            The combined results of all frames for a specific node.
        """
        _data = self.__composites[node_id].copy()
        _data.flatten_dims(*range(SCAN.ndim), new_dim_label='Scan timeline',
                           new_dim_range=np.arange(SCAN.n_total))
        return _data

    def get_result_subset(self, node_id, slices, flattened_scan_dim=False):
        """
        Get a slices subset of a node_id result.

        Parameters
        ----------
        node_id : int
            The node ID for which results should be retured.
        slices : tuple
            The tuple used for slicing/indexing the np.ndaray.
        flattened_scan_dim : bool, optional
            Keyword to process flattened Scan dimensions. If True, the Scan
            is assumed to be 1-d only and the first slice item will be used
            for the Scan whereas the remaining slice items will be used for
            the resulting data. The default is False.

        Returns
        -------
        pydidas.core.Dataset
            The subset of the results.
        """
        if flattened_scan_dim:
            _tmpslices = (
                tuple(slice(0, SCAN.shape[_i], 1) for _i in range(SCAN.ndim))
                + slices[1:])
            _data = self.__composites[node_id][_tmpslices].copy()
            _data.flatten_dims(*range(SCAN.ndim),
                               new_dim_label='Scan timeline',
                               new_dim_range=np.arange(SCAN.n_total))
            return _data[slices[0]]
        _data = self.__composites[node_id].copy()
        return _data[slices]

    def get_result_metadata(self, node_id):
        """
        Get the stored metadata for the results of the specified node.

        Parameters
        ----------
        node_id : int
            The node ID identifier.

        Returns
        -------
        dict
            A dictionary with the metadata stored using the "axis_labels",
            "axis_ranges", "axis_units" and "metadata" keys.
        """
        return  {'axis_labels': self.__composites[node_id].axis_labels,
                 'axis_units': self.__composites[node_id].axis_units,
                 'axis_ranges': self.__composites[node_id].axis_ranges,
                 'metadata': self.__composites[node_id].metadata}

    def save_results_to_disk(self, save_dir, *save_formats, overwrite=False,
                             node_id=None):
        """
        Save results to disk.

        By default, this method saves all results to disk using the specified
        formats and directory.
        Note that the directory needs to be empty (or non-existing) if
        the overwrite keyword is not set.

        Results from a single node can be saved by passing a value for the
        node_id keyword.

        Parameters
        ----------
        save_dir : Union[str, pathlib.Path]
            The basepath for all saved data.
        save_formats : str
            Strings of all formats to be written. Individual formats can be
            also be given in a single string if they are separated by comma
            (","), ampersand ("&") or slash ("/") characters.
        overwrite : bool, optional
            Flag to enable overwriting of existing files. The default is False.
        node_id : Union[None, int], optional
            The node ID for which data shall be saved. If None, this defaults
            to all nodes. The default is None.
        """
        self.prepare_files_for_saving(save_dir, ','.join(save_formats),
                                      overwrite, single_node=node_id)
        if node_id is None:
            _res = self.__composites
        else:
            _res = {node_id: self.__composites[node_id]}
        RESULT_SAVER.export_full_data_to_active_savers(_res)

    def prepare_files_for_saving(self, save_dir, save_formats,
                                 overwrite=False, single_node=None):
        """
        Prepare the required files and directories for saving.

        Note that the directory needs to be empty (or non-existing) if
        the overwrite keyword is not set.

        Parameters
        ----------
        save_dir : Union[str, pathlib.Path]
            The basepath for all saved data.
        save_formats : str
            A string of all formats to be written. Individual formats can be
            separated by comma (","), ampersand ("&") or slash ("/")
            characters.
        overwrite : bool, optional
            Flag to enable overwriting of existing files. The default is False.
        single_node: Union[None, int]
            Keyword to select a single node. If None, all nodes will be
            selected. The default is None.

        Raises
        ------
        FileExistsError
            If the directory exists and is not empty and overwrite is not
            enabled.
        """
        if (os.path.exists(save_dir) and len(os.listdir(save_dir)) > 0
                and not overwrite):
            raise FileExistsError(f'The specified directory "{save_dir}" '
                                  'exists and is not empty. Please select'
                                  ' a different directory.')
        if single_node is None:
            _shapes = self.shapes
            _labels = self.labels
        else:
            _shapes = {single_node: self.shapes[single_node]}
            _labels = {single_node: self.labels[single_node]}
        # TODO  : check if the commented line can be deleted
        # self._config['save_dir'] = save_dir
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
        save_formats = [s.strip() for s in re.split('&|/|,', save_formats)]
        _name = SCAN.get_param_value('scan_name')
        RESULT_SAVER.set_active_savers_and_title(save_formats, _name)
        RESULT_SAVER.prepare_active_savers(save_dir, _shapes, _labels)

    def update_param_choices_from_labels(self, param,
                                         add_no_selection_entry=True):
        """
        Store the current WorkflowResults node labels in the specified
        Parameter's choices.

        A neutral entry of "No selection" can be added with the optional flag.

        Parameters
        ----------
        param : pydidas.core.Parameter
            The Parameter to be updated.
        add_no_selection_entry : bool, optional
            Flag to add an entry of no selection in addition to the entries
            from the nodes. The default is True.
        """
        _curr_choice = param.value
        _new_choices = ['No selection'] if add_no_selection_entry else []
        _new_choices.extend(
            [(f'{_val} (node #{_key:03d})' if len(_val) > 0
              else f'(node #{_key:03d})')
             for _key, _val in self._config['labels'].items()])
        if _curr_choice in _new_choices:
            param.choices = _new_choices
        else:
            _new_choices.append(_curr_choice)
            param.choices = _new_choices
            param.value = _new_choices[0]
            param.choices = _new_choices[:-1]


WorkflowResults = SingletonFactory(_WorkflowResults)
