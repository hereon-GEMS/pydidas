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
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ["WorkflowResults"]

import os
import re

import numpy as np
from qtpy import QtCore

from ..core import utils, Dataset, SingletonFactory
from ..experiment import SetupScan
from .workflow_tree import WorkflowTree
from .result_io import WorkflowResultIoMeta


RESULT_SAVER = WorkflowResultIoMeta
SCAN = SetupScan()
TREE = WorkflowTree()


class _WorkflowResults(QtCore.QObject):
    """
    WorkflowResults is a class for handling composite data which spans
    multiple datasets with multiple dimensions each. Results are referenced
    by the node ID of the data's producer.
    """

    new_results = QtCore.Signal()

    def __init__(self):
        super().__init__()
        self.clear_all_results()

    def update_shapes_from_scan_and_workflow(self):
        """
        Update the shape of the results by querying SetupScan and
        WorkflowTree for their current dimensions and shapes.
        """
        self.clear_all_results()
        _dim = SCAN.get_param_value("scan_dim")
        _results = TREE.get_all_result_shapes()
        _shapes = {_key: SCAN.shape + _shape for _key, _shape in _results.items()}
        for _node_id, _shape in _shapes.items():
            _dset = Dataset(np.zeros(_shape, dtype=np.float32))
            for index in range(_dim):
                _label, _unit, _range = SCAN.get_metadata_for_dim(index)
                _dset.update_axis_labels(index, _label)
                _dset.update_axis_units(index, _unit)
                _dset.update_axis_ranges(index, _range)
            self.__composites[_node_id] = _dset
            self._config["shapes"] = _shapes
            _plugin = TREE.nodes[_node_id].plugin
            self._config["node_labels"][_node_id] = _plugin.get_param_value("label")
            self._config["data_labels"][_node_id] = _plugin.output_data_label
            self._config["data_units"][_node_id] = _plugin.output_data_unit
            self._config["plugin_names"][_node_id] = _plugin.plugin_name
            self._config["result_titles"][_node_id] = _plugin.result_title
        self.__source_hash = hash((hash(SCAN), hash(TREE)))

    def clear_all_results(self):
        """
        Clear all interally stored results and reset the instance attributes.
        """
        self.__composites = {}
        self.__source_hash = hash((hash(SCAN), hash(TREE)))
        self._config = {
            "shapes": {},
            "node_labels": {},
            "data_labels": {},
            "data_units": {},
            "metadata_complete": False,
            "plugin_names": {},
            "result_titles": {},
        }

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
            _dim_offset = SCAN.get_param_value("scan_dim")
            for _key, _items in _meta.items():
                _update_method = getattr(self.__composites[node_id], f"update_{_key}")
                for _dim, _val in _items.items():
                    _update_method(_dim + _dim_offset, _val)
        self._config["metadata_complete"] = True

    def store_results(self, index, results):
        """
        Store results from one scan point in the WorkflowResults.

        Note: If write_to_disk is enabled, please be advised that this may
        slow down the WorkflowResults

        Parameters
        ----------
        index : int
            The index of the scan point.
        results: dict
            The results as dictionary with entries of the type
            <node_id: array>.
        """
        if not self._config["metadata_complete"]:
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
            _dim_offset = SCAN.get_param_value("scan_dim")
            for _dim in range(result.ndim):
                self.__composites[node_id].update_axis_labels(
                    _dim + _dim_offset, result.axis_labels[_dim]
                )
                self.__composites[node_id].update_axis_units(
                    _dim + _dim_offset, result.axis_units[_dim]
                )
                self.__composites[node_id].update_axis_ranges(
                    _dim + _dim_offset, result.axis_ranges[_dim]
                )
        self._config["metadata_complete"] = True

    @property
    def shapes(self):
        """
        Return the shapes of the results in form of a dictionary.

        Returns
        -------
        dict
            A dictionary with entries of the form <node_id: results_shape>
        """
        return self._config["shapes"].copy()

    @property
    def labels(self):
        """
        Return the labels of the results in form of a dictionary.

        Returns
        -------
        dict
            A dictionary with entries of the form <node_id: label>
        """
        return self._config["node_labels"].copy()

    @property
    def data_labels(self):
        """
        Return the data labels of the different Plugins to in form of a
        dictionary.

        Returns
        -------
        dict
            A dictionary with entries of the form <node_id: label>
        """
        return self._config["data_labels"].copy()

    @property
    def data_units(self):
        """
        Return the data units of the different Plugins to in form of a
        dictionary.

        Returns
        -------
        dict
            A dictionary with entries of the form <node_id: label>
        """
        return self._config["data_units"].copy()

    @property
    def ndims(self):
        """
        Return the number of dimensions of the results in form of a dictionary.

        Returns
        -------
        dict
            A dictionary with entries of the form <node_id: n_dim>
        """
        return {_key: _item.ndim for _key, _item in self.__composites.items()}

    @property
    def source_hash(self):
        """
        Get the source hash from the input WorkflowTree ans SetupScan.

        Returns
        -------
        int
            The hash value of the combined input data.
        """
        self.__source_hash = hash((hash(SCAN), hash(TREE)))
        return self.__source_hash

    @property
    def result_titles(self):
        """
        Return the result titles for all node IDs in form of a dictionary.

        Returns
        -------
        dict
            The result titles in the form of a dictionary with <node_id: result_title>
            entries.
        """
        return self._config["result_titles"].copy()

    def get_result_ranges(self, node_id):
        """
        Get the data ranges for the requested node id.

        Parameters
        ----------
        node_id : int
            The node ID for which the result ranges should be returned.

        Returns
        -------
        dict
            The dictionary with the ranges with dimension keys and ranges
            values.
        """
        return self.__composites[node_id].axis_ranges.copy()

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

    def get_results_for_flattened_scan(self, node_id, squeeze=False):
        """
        Get the combined results for the requested node_id with all scan
        dimensions flatted into a timeline

        Parameters
        ----------
        node_id : int
            The node ID for which results should be retured.
        squeeze : bool, optional
            Keyword to toggle squeezing of data dimensions of the final dataset. If
            True, all dimensions with a length of 1 will be removed. The default is
            False.

        Returns
        -------
        pydidas.core.Dataset
            The combined results of all frames for a specific node.
        """
        _data = self.__composites[node_id].copy()
        _data.flatten_dims(
            *range(SCAN.ndim),
            new_dim_label="Chronological scan points",
            new_dim_range=np.arange(SCAN.n_points),
        )
        if squeeze:
            return _data.squeeze()
        return _data

    def get_result_subset(
        self,
        node_id,
        slices,
        flattened_scan_dim=False,
        squeeze=False,
    ):
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
        _data = self.__composites[node_id].copy()

        def __dim_index(i):
            return len(slices) - (i + 1) + flattened_scan_dim * (SCAN.ndim - 1)

        for _dim, _slice in enumerate(slices[flattened_scan_dim:][::-1]):
            if isinstance(_slice, slice):
                _slice = np.r_[_slice]
            _data = np.take(_data, _slice, __dim_index(_dim))

        if flattened_scan_dim:
            _data.flatten_dims(
                *range(SCAN.ndim),
                new_dim_label="Chronological scan points",
                new_dim_range=np.arange(SCAN.n_points),
            )
            _data = _data[slices[0]]

        if squeeze:
            return _data.squeeze()
        return _data

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
        return {
            "axis_labels": self.__composites[node_id].axis_labels,
            "axis_units": self.__composites[node_id].axis_units,
            "axis_ranges": self.__composites[node_id].axis_ranges,
            "metadata": self.__composites[node_id].metadata,
        }

    def save_results_to_disk(
        self, save_dir, *save_formats, overwrite=False, node_id=None
    ):
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
        self.prepare_files_for_saving(
            save_dir, ",".join(save_formats), overwrite, single_node=node_id
        )
        if node_id is None:
            _res = self.__composites
        else:
            _res = {node_id: self.__composites[node_id]}
        RESULT_SAVER.export_full_data_to_active_savers(_res)

    def prepare_files_for_saving(
        self, save_dir, save_formats, overwrite=False, single_node=None
    ):
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
        save_formats = [s.strip() for s in re.split("&|/|,", save_formats)]
        _name = SCAN.get_param_value("scan_title")
        RESULT_SAVER.set_active_savers_and_title(save_formats, _name)
        if single_node is None:
            _keys = list(self.shapes.keys())
        else:
            _keys = [single_node]
        _node_info = {
            _id: {
                "shape": self._config["shapes"][_id],
                "node_label": self._config["node_labels"][_id],
                "data_label": self._config["data_labels"][_id],
                "data_unit": self._config["data_units"][_id],
                "plugin_name": self._config["plugin_names"][_id],
            }
            for _id in _keys
        }
        _labels = {_id: _node_info[_id]["node_label"] for _id in _node_info}
        _names = RESULT_SAVER.get_filenames_from_active_savers(_labels)
        _existcheck = [
            os.path.exists(os.path.join(save_dir, _name)) for _name in _names
        ]
        if True in _existcheck and not overwrite:
            raise FileExistsError(
                f"The specified directory '{save_dir}' exists and is not empty. Please "
                "select a different directory."
            )
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
        RESULT_SAVER.prepare_active_savers(save_dir, _node_info)

    def update_param_choices_from_labels(self, param, add_no_selection_entry=True):
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
        _new_choices = ["No selection"] if add_no_selection_entry else []
        _new_choices.extend(self._config["result_titles"].values())
        if _curr_choice in _new_choices:
            param.choices = _new_choices
        else:
            _new_choices.append(_curr_choice)
            param.choices = _new_choices
            param.value = _new_choices[0]
            param.choices = _new_choices[:-1]

    def get_node_result_metadata_string(
        self, node_id, use_scan_timeline=False, squeeze_results=True
    ):
        """
        Get the edited metadata from WorkflowResults as a formatted string.

        Parameters
        ----------
        node_id : int
            The node ID of the active node.
        use_scan_timeline : bool, optional
            The flag whether to reduce the scan dimensions to a single
            timeline. The default is False.
        squeeze_results : bool, optional
            Flag whether to squeeze the results (i.e. remove all dimensions of length 1)
            from the data. The default is True.

        Returns
        -------
        str :
            The formatted string with a representation of all the metadata.
        """
        _meta = self.get_result_metadata(node_id)
        _scandim = SCAN.get_param_value("scan_dim")
        _start_index = use_scan_timeline * _scandim
        _print_info = {
            "ax_labels": list(_meta["axis_labels"].values())[_start_index:],
            "ax_units": list(_meta["axis_units"].values())[_start_index:],
            "ax_ranges": list(
                utils.get_range_as_formatted_string(_range)
                for _range in _meta["axis_ranges"].values()
            )[_start_index:],
            "ax_types": list(
                ("(scan)" if _key < _scandim else "(data)")
                for _key in _meta["axis_labels"].keys()
            )[_start_index:],
            "ax_points": list(self.shapes[node_id])[_start_index:],
        }
        if use_scan_timeline:
            _print_info["ax_labels"].insert(0, "Chronological scan points")
            _print_info["ax_units"].insert(0, "")
            _print_info["ax_ranges"].insert(0, f"0 ... {SCAN.n_points - 1}")
            _print_info["ax_points"].insert(0, SCAN.n_points)
            _print_info["ax_types"].insert(0, "(scan)")
        if squeeze_results:
            _squeezed_dims = np.where(np.asarray(_print_info["ax_points"]) == 1)[0]
            for _key in _print_info.keys():
                _print_info[_key] = list(np.delete(_print_info[_key], _squeezed_dims))
        _data_label = self._config["data_labels"][node_id] + (
            f" / {self._config['data_units'][node_id]}"
            if len(self._config["data_units"][node_id]) > 0
            else ""
        )
        _node_info = (
            self._config["plugin_names"][node_id]
            + ":\n\n"
            + f"Data: {_data_label}\n\n"
            + "".join(
                (
                    f"Axis #{_dim:02d} {_print_info['ax_types'][_dim]}:\n"
                    f"  Label: {_print_info['ax_labels'][_dim]}\n"
                    f"  N points: {_print_info['ax_points'][_dim]}\n"
                    f"  Range: {_print_info['ax_ranges'][_dim]} "
                    f"{_print_info['ax_units'][_dim]}\n"
                )
                for _dim, _ in enumerate(_print_info["ax_labels"])
            )
        )
        return _node_info

    def import_data_from_directory(self, directory):
        """
        Import data from a directory.

        Parameters
        ----------
        directory : Union[pathlib.Path, str]
            The input directory with the exported pydidas results.
        """
        self.clear_all_results()
        _data, _node_info, _scan = RESULT_SAVER.import_data_from_directory(directory)
        self._config = {
            "shapes": {_key: _item.shape for _key, _item in _data.items()},
            "node_labels": {
                _id: _item["node_label"] for _id, _item in _node_info.items()
            },
            "data_labels": {
                _id: _item["data_label"] for _id, _item in _node_info.items()
            },
            "data_units": {
                _id: _item["data_unit"] for _id, _item in _node_info.items()
            },
            "plugin_names": {
                _id: _item["plugin_name"] for _id, _item in _node_info.items()
            },
            "result_titles": {
                _id: _item["result_title"] for _id, _item in _node_info.items()
            },
            "metadata_complete": True,
        }
        self.__composites = _data
        SCAN.update_from_dictionary(_scan)


WorkflowResults = SingletonFactory(_WorkflowResults)
