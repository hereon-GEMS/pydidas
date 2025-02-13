# This file is part of pydidas.
#
# Copyright 2023 - 2025, Helmholtz-Zentrum Hereon
# SPDX-License-Identifier: GPL-3.0-only
#
# pydidas is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 3 as
# published by the Free Software Foundation.
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
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["WorkflowResultsSelector"]


import re

import numpy as np
from qtpy import QtCore

from pydidas.core import (
    ObjectWithParameterCollection,
    Parameter,
    UserConfigError,
    get_generic_param_collection,
)
from pydidas.workflow.workflow_results import WorkflowResults


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
        shared between the WorkflowResultsSelector and the parent.
    **kwargs : dict
        Optional keyword arguments. Supported kwargs are:

        workflow_results : ProcessingResults, optional
            The ProcessingResults instance to use. If not specied, this will default
            to the WorkflowResults.
    """

    new_selection = QtCore.Signal(bool, int, int, object)

    default_params = get_generic_param_collection(
        "use_scan_timeline", "result_n_dim", "use_data_range"
    )

    def __init__(self, *args: tuple, **kwargs: dict):
        ObjectWithParameterCollection.__init__(self)
        self.add_params(*args)
        self.set_default_params()
        _results = kwargs.get("workflow_results", None)
        self._RESULTS = WorkflowResults() if _results is None else _results
        self._SCAN = self._RESULTS.frozen_scan
        self._selection = None
        self._npoints = []
        self._config["active_node"] = -1
        self._config["active_ranges"] = {}
        self._config["param_hash"] = -1
        self._re_pattern = re.compile(r"^(\s*(-?\d*\.?\d*:?){1,3},?)*?$")

    def reset(self):
        """
        Reset the instance to its default selection, for example when a new
        processing has been started and the old information is no longer valid.
        """
        self._config["active_node"] = -1
        self._selection = None

    def select_active_node(self, index: int):
        """
        Select the active node.

        Parameters
        ----------
        index : int
            The new node index.
        """
        self._config["active_node"] = index
        self._calc_and_store_ndim_of_results()
        self._check_and_create_params_for_slice_selection()
        self._config["active_ranges"] = self._RESULTS.get_result_ranges(index)

    def _calc_and_store_ndim_of_results(self):
        """
        Update the number of dimensions the results will have and store the
        new number.
        """
        _ndim = self._RESULTS.ndims[self._config["active_node"]]
        if self.get_param_value("use_scan_timeline"):
            _ndim -= self._SCAN.ndim - 1
        self._config["result_ndim"] = _ndim

    def _check_and_create_params_for_slice_selection(self):
        """
        Check whether the required Parameters for the slice selection exist
        for all current data dimensions and create and add them if they do not.
        """
        for _dim in range(self._RESULTS.ndims[self._config["active_node"]]):
            _refkey = f"data_slice_{_dim}"
            _param = Parameter(
                _refkey,
                str,
                ":",
                name=f"Slice of data dim #{_dim}",
                tooltip=(
                    "The slice description for the selected data "
                    "dimension. Use a colon to select the full range."
                ),
            )
            if _refkey not in self.params:
                self.add_param(_param)

    @property
    def selection(self) -> tuple[slice, ...]:
        """
        Get the current selection object.

        Returns
        -------
        tuple
            The selection for slicing the WorkflowResults array.
        """
        if self._get_param_hash() != self._config["param_hash"]:
            self._update_selection()
        return self._selection

    @property
    def active_dims(self) -> list[int, ...]:
        """
        Get the active dimensions (i.e. dimensions with more than one entry)

        Returns
        -------
        list
            The active dimensions.
        """
        if self._get_param_hash() != self._config["param_hash"]:
            self._update_selection()
        return [
            _index for _index, _items in enumerate(self._selection) if _items.size > 1
        ]

    def _get_param_hash(self) -> int:
        """
        Get the hash value for all Parameter values.

        Returns
        -------
        int
            The hash value.
        """
        _hash_tuple = tuple(
            [
                self.get_param_value(f"data_slice_{_dim}")
                for _dim in range(self._config["result_ndim"])
            ]
            + [self.get_param_value("use_scan_timeline")]
            + [self.get_param_value("use_data_range")]
            + [self._config["result_ndim"]]
            + [self._config["active_node"]]
            + [hash(self._SCAN)]
        )
        return hash(tuple(_hash_tuple))

    def _update_selection(self):
        """
        Update the selection based on the entries for the "data_slice_##"
        Parameters.
        """
        _use_timeline = self.get_param_value("use_scan_timeline")
        self._npoints = list(self._RESULTS.shapes[self._config["active_node"]])
        if _use_timeline:
            del self._npoints[: self._SCAN.ndim]
            self._npoints.insert(0, self._SCAN.n_points)
        _selection = tuple(
            self._get_single_slice_object(_dim)
            for _dim in range(self._config["result_ndim"])
        )
        self._check_for_selection_dim(_selection)
        self._selection = _selection
        self._config["param_hash"] = self._get_param_hash()

    def _get_single_slice_object(self, index: int) -> np.ndarray:
        """
        Get the array which slices the selected dimension

        Parameters
        ----------
        index : int
            The dimension index.

        Raises
        ------
        UserConfigError
            If the string pattern cannot be parsed.

        Returns
        -------
        np.ndarray
            The array with the selected slice indices for the given dimension.
        """
        self._config["active_index"] = index
        self._config["index_defaults"] = [0, self._npoints[index], 1]
        _str = self.get_param_value(f"data_slice_{index}")
        if _str in ["", ":"]:
            return np.r_[slice(0, self._npoints[index], 1)]
        if not bool(self._re_pattern.fullmatch(_str)):
            raise UserConfigError(
                "Cannot interprete the selection pattern "
                f'"{_str}" for the dimension "{index}".'
            )
        _substrings = [_s.strip() for _s in _str.split(",")]
        _slices = []
        if (
            self.get_param_value("use_scan_timeline") and index == 0
        ) or not self.get_param_value("use_data_range"):
            _entries = self._parse_string_indices(_substrings)
        else:
            _entries = self._convert_values_to_indices(_substrings)
        for _entry in _entries:
            if len(_entry) == 1:
                _slices.append(_entry[0])
            elif len(_entry) in (2, 3):
                if self.get_param_value("use_data_range"):
                    _entry[1] = _entry[1] + (_entry[2] if len(_entry) == 3 else 1)
                _slices.append(slice(*_entry))
            else:
                raise UserConfigError(
                    f"Cannot interpret slice objects with 4 items: '{_str}'"
                )
        return np.unique(np.r_[tuple(_slices)])

    def _parse_string_indices(self, substrings: list[str]) -> list[int]:
        """
        Parse the string with indices to integer values.

        Parameters
        ----------
        substrings : list[str]
            The list with individual entries (which were separated by "," in
            the original string).

        Returns
        -------
        list[int]
            The list with index values for the various selections.
        """
        _new_items = []
        _index = self._config["active_index"]
        _defaults = self._config["index_defaults"]
        for _substr in substrings:
            _entries = _substr.split(":")
            for _pos, _key in enumerate(_entries):
                _entries[_pos] = int(_defaults[_pos] if _key == "" else _key)
                if _entries[_pos] < 0:
                    _entries[_pos] = np.mod(_entries[_pos], self._npoints[_index])
            _new_items.append(_entries)
        return _new_items

    def _convert_values_to_indices(self, substrings: list[str]) -> list[int]:
        """
        Convert data value strings to indexes for selecting the required
        datapoints.

        Parameters
        ----------
        substrings : list[str]
            The list with individual entries (which were separated by "," in
            the original string).

        Returns
        -------
        list[int]
            The list with index values for the various selections.
        """
        _new_items = []
        _range = self._config["active_ranges"][self._config["active_index"]]
        _defaults = self._config["index_defaults"]
        for _item in substrings:
            _keys = [
                float(_defaults[_pos] if _val == "" else _val)
                for _pos, _val in enumerate(_item.split(":"))
            ]
            if len(_keys) == 1:
                _index = self.get_best_index_for_value(_keys[0], _range)
                _new_items.append([_index])
            elif len(_keys) == 2:
                _startindex = self.get_best_index_for_value(_keys[0], _range)
                _stopindex = self.get_best_index_for_value(_keys[1], _range)
                _new_items.append([_startindex, _stopindex])
            elif len(_keys) == 3:
                _targets = np.arange(_keys[0], _keys[1], _keys[2])
                for _val in _targets:
                    _index = self.get_best_index_for_value(_val, _range)
                    _new_items.append([_index])
        return _new_items

    def get_best_index_for_value(self, value: float, valrange: np.ndarray) -> int:
        """
        Get the index which is the closest match to the selected value from a range.

        Parameters
        ----------
        value : float
            The target value
        valrange : np.ndarray
            The array with all values.

        Returns
        -------
        index : int
            The index with the best match.
        """
        if not isinstance(valrange, np.ndarray):
            return int(value)
        _delta = abs(valrange - value)
        _index = _delta.argmin()
        return _index

    def _check_for_selection_dim(self, selection: tuple[slice]):
        """
        Check that the selection has the same dimensionality as the requested
        dimensionality and raise an Exception if not.

        Parameters
        ----------
        selection : tuple[slice]
            The slice objects for all dimensions.

        Raises
        ------
        UserConfigError
            If the number of dimensions in the selection does not match the
            demanded result dimensionality.
        """
        _dims_larger_one = 0
        for _value in selection:
            if _value.size > 1:
                _dims_larger_one += 1
        _target_dims = self.get_param_value("result_n_dim")
        if _target_dims == -1:
            return
        if _target_dims != _dims_larger_one:
            raise UserConfigError(
                "The dimensionality of the selected data subset does not match "
                f"the specified dimension. Specified dimensionality: {_dims_larger_one}"
                f"; Target dimensionality: {_target_dims}."
            )
