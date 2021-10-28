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

"""The composites module includes the Composite class for handling composite image data."""

__author__      = "Malte Storm"
__copyright__   = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.0.1"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['WorkflowResults']

import numpy as np
from PyQt5 import QtCore

from ..core.singleton_factory import SingletonFactory
from ..core.scan_settings import ScanSettings
from ..core import Dataset
from .workflow_tree import WorkflowTree

SCAN = ScanSettings()

TREE = WorkflowTree()


class _WorkflowResults(QtCore.QObject):
    """
    WorkflowResults is a class for handling composite data which spans
    individual images.
    """
    new_results = QtCore.pyqtSignal()

    def __init__(self):
        super().__init__()
        self.__composites = {}
        self._config = {'shapes': None,
                        'metadata_complete': False}

    def update_shapes_from_scan(self):
        """
        Update the shape of the results from the ScanSettings.
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
                _label, _unit, _range = self.get_scan_data_for_dim(index)
                _dset.axis_labels[index] = _label
                _dset.axis_units[index] = _unit
                _dset.axis_scales[index] = _range
            self.__composites[_node_id] = _dset
            self._config['shapes'] = _shapes

    def clear_all_results(self):
        """
        Clear all interally stored results and reset the instance attributes.
        """
        self.__composites = {}
        self._config = {'shapes': None,
                        'metadata_complete': False}

    @staticmethod
    def get_scan_data_for_dim(index):
        """
        Get the label, unit and range of the specified scan dimension.

        Parameters
        ----------
        index : int
            The index of the scan dimension.

        Returns
        -------
        label : str
            The label / motor name for this scan dimension.
        unit : str
            The unit for the range.
        range : np.ndarray
            The numerical positions of the scan.
        """
        _f0 = SCAN.get_param_value(f'offset_{index + 1}')
        _df = SCAN.get_param_value(f'delta_{index + 1}')
        _n = SCAN.get_param_value(f'n_points_{index + 1}')
        _range = np.linspace(_f0, _f0 + _df * _n, _n, endpoint=False)
        _label = SCAN.get_param_value(f'scan_dir_{index + 1}')
        _unit = SCAN.get_param_value(f'unit_{index + 1}')
        return _label, _unit, _range


    def store_results(self, index, results):
        """
        Store results from one frame in the WorkflowResults.

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
            _dim_offset = self.__composites[node_id].ndim - result.ndim
            for _dim in range(result.ndim):
                self.__composites[node_id].axis_labels[_dim + _dim_offset] = (
                    result.axis_labels[_dim])
                self.__composites[node_id].axis_units[_dim + _dim_offset] = (
                    result.axis_units[_dim])
                self.__composites[node_id].axis_scales[_dim + _dim_offset] = (
                    result.axis_scales[_dim])
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
        return self._config['shapes']

    def get_results(self, node_id):
        """
        Get the combined results for the requested node_id.

        Parameters
        ----------
        node_id : int
            The node ID for which results should be retured.

        Returns
        -------
        np.ndarray
            The combined results of all frames for a specific node.
        """
        return self.__composites[node_id]


WorkflowResults = SingletonFactory(_WorkflowResults)
