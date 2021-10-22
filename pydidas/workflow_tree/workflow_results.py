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
        self._config = {}

    def update_shapes_from_scan(self):
        """
        Update the shape of the results from the ScanSettings.
        """
        _dim = SCAN.get_param_value('scan_dim')
        _points = tuple([SCAN.get_param_value(f'n_points_{_n}')
                         for _n in range(1, _dim + 1)])
        _results = TREE.get_all_result_shapes()
        _shapes = {_key: _points + _shape for _key, _shape in _results.items()}
        for _node_id, _shape in _shapes.items():
            self.__composites[_node_id] = Dataset(
                np.zeros(_shape, dtype=np.float32))
            self._config['shapes'] = _shapes

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
        _scan_index = SCAN.get_frame_position_in_scan(index)
        for _key, _val in results.items():
            self.__composites[_key][_scan_index] = _val
        self.new_results.emit()

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
        Get the combined results for the requested node_id

        Parameters
        ----------
        node_id : int
            The node ID for which results should be retured.

        Returns
        -------
        np.ndarray
            DESCRIPTION.

        """
        return self.__composites[node_id]


WorkflowResults = SingletonFactory(_WorkflowResults)
