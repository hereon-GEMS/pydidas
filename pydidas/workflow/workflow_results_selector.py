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
Module with the WorkflowResultsSelector which allows to select a subset of the
results stored in the WorkflowResults.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.1.1"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['WorkflowResultsSelector']

import re

import numpy as np
from qtpy import QtCore

from ..core import (Parameter, ObjectWithParameterCollection,
                     get_generic_param_collection, AppConfigError)
from ..experiment import ScanSetup
from .workflow_results import WorkflowResults


RESULTS = WorkflowResults()
SCAN = ScanSetup()


class WorkflowResultsSelector(ObjectWithParameterCollection):
    """
    The WorkflowResultsSelector class allows to select a subset of results
    from a full WorkflowResults node.

    Parameters
    ----------
    parent : QtWidgets.QWidget
        The parent widget.
    select_results_param : pydidas.core.Parameter
        The select_results Parameter instance. This instance should be
        shared between the ResultSelectorForOutput and the parent.
    """
    new_selection = QtCore.Signal(bool, int, int, object)

    default_params = get_generic_param_collection(
        'use_scan_timeline', 'result_n_dim')

    def __init__(self, **kwargs):
        ObjectWithParameterCollection.__init__(self)
        self.set_default_params()
        self._selection = None
        self._active_node = -1
        self._npoints = []
        self._re_pattern = re.compile('^(-?\\d*,?:?){0,30}$')

    def reset(self):
        """
        Reset the instance to its default selection, for example when a new
        processing has been started and the old information is no longer valid.
        """
        self._active_node = -1
        self._selection = None

    def select_active_node(self, index):
        """
        Select the active node.

        Parameters
        ----------
        index : int
            The new node index.
        """
        self._active_node = index
        self._calc_and_store_ndim_of_results()
        self._check_and_create_params_for_slice_selection()

    def _calc_and_store_ndim_of_results(self):
        """
        Update the number of dimensions the results will have and store the
        new number.
        """
        _ndim = RESULTS.ndims[self._active_node]
        if self.get_param_value('use_scan_timeline'):
            _ndim -= SCAN.ndim - 1
        self._config['result_ndim'] = _ndim

    def _check_and_create_params_for_slice_selection(self):
        """
        Check whether the required Parameters for the slice selection exist
        for all current data dimensions and create and add them if they do not.
        """
        for _dim in range(RESULTS.ndims[self._active_node]):
            _refkey = f'data_slice_{_dim}'
            _param = Parameter(
                _refkey, str, ':', name=f'Slice of data dim #{_dim}',
                tooltip=('The slice description for the selected data '
                         'dimension. Use a colon to select the full range.'))
            if _refkey not in self.params:
                self.add_param(_param)

    @property
    def selection(self):
        """
        Get the current selection object.

        Returns
        -------
        tuple
            The selection for slicing the WorkflowResults array.
        """
        self._update_selection()
        return self._selection

    def _update_selection(self):
        """
        Update the selection based on the entries for the "data_slice_##"
        Parameters.
        """
        _use_timeline = self.get_param_value('use_scan_timeline')
        self._npoints = list(RESULTS.shapes[self._active_node])
        if _use_timeline:
            del self._npoints[:SCAN.ndim]
            self._npoints.insert(0, SCAN.n_total)
        _selection = tuple(self._get_single_slice_object(_dim)
                           for _dim in range(self._config['result_ndim']))
        self._check_for_selection_dim(_selection)
        self._selection = _selection

    def _get_single_slice_object(self, index):
        """
        Get the array which slices the selected dimension

        Parameters
        ----------
        index : int
            The dimension index.

        Raises
        ------
        AppConfigError
            If the string pattern cannot be parsed.

        Returns
        -------
        np.ndarray
            The array with the selected slice indices for the given dimension.
        """
        # Get the selection string without any blank chars to match the
        # regular expression.
        _str = ''.join(self.get_param_value(f'data_slice_{index}').split())
        if _str in ['', ':']:
            return np.r_[slice(0, self._npoints[index], 1)]
        if not bool(self._re_pattern.fullmatch(_str)):
            raise AppConfigError('Cannot interprete the selection pattern for '
                                 f'the dimension "{index}".')
        _defaults = [0, self._npoints[index], 1]
        _substrings = _str.split(',')
        _slices = []
        for _substr in _substrings:
            _entries = _substr.split(':')
            for _pos, _key in enumerate(_entries):
                _entries[_pos] = int(_defaults[_pos] if _key == '' else _key)
                if _entries[_pos] < 0:
                    _entries[_pos] = np.mod(_entries[_pos],
                                            self._npoints[index])
            if len(_entries) == 1:
                _slices.append(_entries[0])
            elif len(_entries) == 2:
                _slices.append(slice(_entries[0], _entries[1]))
            elif len(_entries) == 3:
                _slices.append(slice(_entries[0], _entries[1], _entries[2]))
        return np.unique(np.r_[tuple(_slices)])

    def _check_for_selection_dim(self, selection):
        """
        Check that the selection has the same dimensionality as the requested
        dimensionality and raise an Exception if not.

        Parameters
        ----------
        selection : tuple
            The slice objects for all dimensions.

        Raises
        ------
        AppConfigError
            If the number of dimensions in the selection does not match the
            demanded result dimensionality.
        """
        _dims_larger_one = 0
        for _value in selection:
            if _value.size > 1:
                _dims_larger_one += 1
        _target_dims = self.get_param_value('result_n_dim')
        if _target_dims == -1:
            return
        if _target_dims != _dims_larger_one:
            raise AppConfigError('The dimensionality of the selected data '
                                 'subset does not match ')
