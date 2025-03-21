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
The workflow_results module includes the ProcessingResults and WorkflowResults
singleton class for storing and accessing the composite results of the processing.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["ProcessingResults"]


import os
import re
from pathlib import Path

import numpy as np
from qtpy import QtCore

from pydidas.contexts import (
    DiffractionExperiment,
    DiffractionExperimentContext,
    Scan,
    ScanContext,
)
from pydidas.core import Dataset, Parameter, UserConfigError, utils
from pydidas.workflow.processing_tree import ProcessingTree
from pydidas.workflow.result_io import ProcessingResultIoMeta as ResultSaver
from pydidas.workflow.workflow_tree import WorkflowTree


class ProcessingResults(QtCore.QObject):
    """
    A class for handling composite data from multiple plugins.

    This class handles Datasets from each plugin in the WorkflowTree. Results
    are referenced by the node ID of the data's producer.

    Warning: Users should generally only use the WorkflowResults singleton,
    and never use the ProcessingResults directly unless explicitly required.

    Parameters
    ----------
    scan_context : Optional[pydidas.contexts.Scan]
        The scan context. If None, the generic context will be used. Only specify this,
        if you explicitly require a different context. The default is None.
    diffraction_exp_context : Union[DiffractionExp, None], optional
        The diffraction experiment context. If None, the generic context will be used.
        Only specify this, if you explicitly require a different context. The default
        is None.
    workflow_tree : Union[WorkflowTree, None], optional
        The WorkflowTree. If None, the generic WorkflowTree will be used. Only specify
        this, if you explicitly require a different context. The default is None.
    """

    new_results = QtCore.Signal()

    def __init__(
        self,
        diffraction_exp_context: DiffractionExperiment | None = None,
        scan_context: Scan | None = None,
        workflow_tree: ProcessingTree | None = None,
    ):
        super().__init__(parent=None)
        self._SCAN = ScanContext() if scan_context is None else scan_context
        self._EXP = (
            DiffractionExperimentContext()
            if diffraction_exp_context is None
            else diffraction_exp_context
        )
        self._TREE = WorkflowTree() if workflow_tree is None else workflow_tree
        self._config = {
            "frozen_SCAN": self._SCAN.copy(),
            "frozen_EXP": self._EXP.copy(),
            "frozen_TREE": self._TREE.copy(),
        }
        self._composites = {}
        self.__source_hash = -1
        self.clear_all_results()

    def clear_all_results(self):
        """
        Clear all internally stored results and reset the instance attributes.
        """
        self._composites = {}
        self.__source_hash = -1
        for _key in (
            "shapes",
            "plugin_names",
            "result_titles",
            "node_labels",
            "plugin_res_metadata",
        ):
            self._config[_key] = {}
        for _key in ("metadata_complete", "composites_created", "shapes_set"):
            self._config[_key] = False

    def prepare_new_results(self):
        """
        Prepare the ProcessingResults for new results.
        """
        self.clear_all_results()
        for _node in self._TREE.get_all_nodes_with_results():
            _node_id = _node.node_id
            _plugin = self._TREE.nodes[_node_id].plugin
            self._config["node_labels"][_node_id] = _plugin.get_param_value("label")
            self._config["plugin_names"][_node_id] = _plugin.plugin_name
            self._config["result_titles"][_node_id] = _plugin.result_title
            self._config["plugin_res_metadata"][_node_id] = {}
        self.__source_hash = hash((hash(self._SCAN), hash(self._TREE), hash(self._EXP)))
        self._config["frozen_SCAN"].update_from_scan(self._SCAN)
        self._config["frozen_EXP"].update_from_diffraction_exp(self._EXP)
        self._config["frozen_TREE"].update_from_tree(self._TREE)
        self._config["frozen_TREE"].prepare_execution()

    def store_frame_shapes(self, shapes: dict):
        """
        Store the shapes of the results in the ProcessingResults.

        Parameters
        ----------
        shapes : dict
            The shapes in form of a dictionary with nodeID keys and shape
            values.
        """
        if shapes.keys() != self._config["plugin_res_metadata"].keys():
            raise UserConfigError(
                "The provided node IDs of the shapes do not match the node IDs "
                "given during the preparation of the ProcessingResults."
            )
        _shapes = {
            _key: self._config["frozen_SCAN"].shape + tuple(_shape)
            for _key, _shape in shapes.items()
        }
        self._config["shapes"] = _shapes
        self._config["shapes_set"] = True

    def store_frame_metadata(self, metadata: dict[int, dict]):
        """
        Store the metadata for plugin results.

        Parameters
        ----------
        metadata : dict[int, dict]
            The metadata in form of a dictionary with nodeID keys and dict
            items containing the axis_units, -_labels, and -_ranges keys with
            the associated data.
        """
        _scan_metadata = [
            self._config["frozen_SCAN"].get_metadata_for_dim(i)
            for i in range(self._config["frozen_SCAN"].ndim)
        ]
        _scan_ax_labels = [_item[0] for _item in _scan_metadata]
        _scan_ax_units = [_item[1] for _item in _scan_metadata]
        _scan_ax_ranges = [_item[2] for _item in _scan_metadata]
        _meta = {}
        for node_id, _meta in metadata.items():
            _curr_metadata = self._config["plugin_res_metadata"].get(node_id, {})
            _curr_metadata["axis_labels"] = dict(
                enumerate(_scan_ax_labels + list(_meta["axis_labels"].values()))
            )
            _curr_metadata["axis_units"] = dict(
                enumerate(_scan_ax_units + list(_meta["axis_units"].values()))
            )
            _curr_metadata["axis_ranges"] = dict(
                enumerate(_scan_ax_ranges + list(_meta["axis_ranges"].values()))
            )
            _curr_metadata["data_label"] = _meta.get("data_label", "")
            _curr_metadata["data_unit"] = _meta.get("data_unit", "")
            self._config["plugin_res_metadata"][node_id] = _curr_metadata
            if node_id not in self._config["shapes"]:
                self._config["shapes"][node_id] = self._config[
                    "frozen_SCAN"
                ].shape + tuple(
                    [_range.size for _range in _meta["axis_ranges"].values()]
                )
            if node_id in self._composites:
                self._composites[node_id].axis_labels = _curr_metadata["axis_labels"]
                self._composites[node_id].axis_units = _curr_metadata["axis_units"]
                self._composites[node_id].axis_ranges = _curr_metadata["axis_ranges"]
                self._composites[node_id].data_label = _curr_metadata["data_label"]
                self._composites[node_id].data_unit = _curr_metadata["data_unit"]
        self._config["shapes_set"] = True
        self._config["metadata_complete"] = True
        ResultSaver.push_metadata_to_active_savers(_meta, self._config["frozen_SCAN"])

    def store_results(self, index: int, results: dict[int, Dataset]):
        """
        Store results from one scan point in the ProcessingResults.

        Parameters
        ----------
        index : int
            The index of the scan point.
        results: dict
            The results as dictionary with entries of the type
            <node_id: array>.
        """
        if not self._config["metadata_complete"]:
            self.store_frame_metadata(
                {_node_id: _data.property_dict for _node_id, _data in results.items()}
            )
        if not self._config["composites_created"]:
            self._create_composites()
        _scan_index = self._SCAN.get_index_position_in_scan(index)
        for _key, _val in results.items():
            self._composites[_key][_scan_index] = _val
        self.new_results.emit()

    def _create_composites(self):
        """
        Create the composite datasets for all node results.
        """
        if not self._config["shapes_set"]:
            raise UserConfigError(
                "The shapes of the results have not been set. Please set the shapes "
                "before storing results."
            )
        self._composites = {
            _key: Dataset(
                np.full(_shape, np.nan, dtype=np.float32),
                **self._config["plugin_res_metadata"].get(_key, {}),
            )
            for _key, _shape in self._config["shapes"].items()
        }
        self._config["composites_created"] = True

    @property
    def shapes(self) -> dict:
        """
        Return the shapes of the results in form of a dictionary.

        Returns
        -------
        dict
            A dictionary with entries of the form <node_id: results_shape>
        """
        return self._config["shapes"].copy()

    @property
    def node_labels(self) -> dict:
        """
        Return the labels of the results in form of a dictionary.

        Returns
        -------
        dict
            A dictionary with entries of the form <node_id: label>
        """
        return self._config["node_labels"].copy()

    @property
    def data_labels(self) -> dict:
        """
        Return the data labels of the different Plugins to in form of a
        dictionary.

        Returns
        -------
        dict
            A dictionary with entries of the form <node_id: label>
        """
        return {_key: _item.data_label for _key, _item in self._composites.items()}

    @property
    def data_units(self) -> dict:
        """
        Return the data units of the different Plugins to in form of a
        dictionary.

        Returns
        -------
        dict
            A dictionary with entries of the form <node_id: label>
        """
        return {_key: _item.data_unit for _key, _item in self._composites.items()}

    @property
    def ndims(self) -> dict:
        """
        Return the number of dimensions of the results in form of a dictionary.

        Returns
        -------
        dict
            A dictionary with entries of the form <node_id: ndim>
        """
        return {_key: _item.ndim for _key, _item in self._composites.items()}

    @property
    def frozen_tree(self) -> WorkflowTree:
        """
        Get the frozen instance of the WorkflowTree context.

        Returns
        -------
        WorkflowTree
            The WorkflowTree at the time of processing.
        """
        return self._config["frozen_TREE"]

    @property
    def frozen_exp(self) -> DiffractionExperiment:
        """
        Get the frozen instance of the DiffractionExperiment context.

        Returns
        -------
        DiffractionExperiment
            The DiffractionExperiment at the time of processing.
        """
        return self._config["frozen_EXP"]

    @property
    def frozen_scan(self) -> Scan:
        """
        Get the frozen instance of the Scan context.

        Returns
        -------
        Scan
            The Scan at the time of processing.
        """
        return self._config["frozen_SCAN"]

    @property
    def source_hash(self) -> int:
        """
        Get the source hash from the input WorkflowTree ans ScanContext.

        Returns
        -------
        int
            The hash value of the combined input data.
        """
        self.__source_hash = hash((hash(self._SCAN), hash(self._TREE), hash(self._EXP)))
        return self.__source_hash

    @property
    def result_titles(self) -> dict:
        """
        Return the result titles for all node IDs in form of a dictionary.

        Returns
        -------
        dict
            The result titles in the form of a dictionary with <node_id: result_title>
            entries.
        """
        return self._config["result_titles"].copy()

    def _check_that_results_are_available(self, node_id: int):
        """
        Check if results are available for the specified node ID.

        Parameters
        ----------
        node_id : int
            The node ID for which results should be checked.
        """
        if node_id not in self._composites:
            raise UserConfigError(
                f"The selected node ID `{node_id}` does not have any results "
                "associated with it. Please verify that that selected node is "
                "either a leaf node (i.e. it does not have any children) or that "
                "the `keep_results` flag is set to True in the plugin."
            )

    def get_result_ranges(self, node_id: int) -> dict:
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
        self._check_that_results_are_available(node_id)
        return self._config["plugin_res_metadata"].get(node_id).get("axis_ranges")

    def get_results(self, node_id: int) -> Dataset:
        """
        Get the combined results for the requested node_id.

        Parameters
        ----------
        node_id : int
            The node ID for which results should be returned.

        Returns
        -------
        Dataset
            The combined results of all frames for a specific node.
        """
        self._check_that_results_are_available(node_id)
        return self._composites[node_id]

    def get_results_for_flattened_scan(
        self, node_id: int, squeeze: bool = False
    ) -> Dataset:
        """
        Get the results for the requested node_id with all scan dimensions flatted.

        This method will essentially flatten all scan dimensions into a timeline for
        convenience. The squeeze Parameter can be used to remove all dimensions of
        length 1 from the data.

        Parameters
        ----------
        node_id : int
            The node ID for which results should be returned.
        squeeze : bool, optional
            Keyword to toggle squeezing of data dimensions of the final dataset. If
            True, all dimensions with a length of 1 will be removed. The default is
            False.

        Returns
        -------
        Dataset
            The combined results of all frames for a specific node.
        """
        self._check_that_results_are_available(node_id)
        _data = self._composites[node_id].copy()
        _data.flatten_dims(
            *range(self._config["frozen_SCAN"].ndim),
            new_dim_label="Chronological scan points",
            new_dim_range=np.arange(self._config["frozen_SCAN"].n_points),
        )
        if squeeze:
            return _data.squeeze()
        return _data

    def get_result_subset(
        self,
        node_id: int,
        *slices: tuple[int | slice],
        flattened_scan_dim: bool = False,
        squeeze: bool = False,
    ) -> Dataset:
        """
        Get a sliced subset of a node_id result.

        Note that numpy's slicing always squeezes dimensions with a length of 1 if
        they are given as integers, or slices. Iterable objects keep a
        dimension of length 1.

        Parameters
        ----------
        node_id : int
            The node ID for which results should be returned.
        *slices : tuple[int | slice]
            The tuple used for slicing/indexing the np.ndarray.
        flattened_scan_dim : bool, optional
            Keyword to process flattened Scan dimensions. If True, the Scan
            is assumed to be 1-d only and the first slice item will be used
            for the Scan whereas the remaining slice items will be used for
            the resulting data. The default is False.
        squeeze : bool, optional
            Keyword to toggle squeezing of data dimensions of the final dataset.

        Returns
        -------
        Dataset
            The subset of the results.
        """
        if flattened_scan_dim:
            _data = self.get_results_for_flattened_scan(node_id)
        else:
            self._check_that_results_are_available(node_id)
            _data = self._composites[node_id].copy()
        if set(type(_slice) for _slice in slices).issubset({int, slice}):
            _data = _data[slices]
        else:
            for _index, _slice in enumerate(slices[::-1]):
                _dim = len(slices) - _index - 1
                _data = _data.take(_slice, axis=_dim)
        if squeeze:
            return _data.squeeze()
        return _data

    def get_result_metadata(
        self, node_id: int, use_scan_timeline: bool = False
    ) -> dict:
        """
        Get the stored metadata for the results of the specified node.

        Parameters
        ----------
        node_id : int
            The node ID identifier.
        use_scan_timeline : bool, optional
            Flag to collapse all scan dimensions into a single timeline.

        Returns
        -------
        dict[str, object]
            A dictionary with the metadata retrieved from the Dataset plus the shape
            and `node_label`.
        """
        self._check_that_results_are_available(node_id)
        _metadata = self._composites[node_id].property_dict
        _metadata["node_label"] = self._config["node_labels"].get(node_id, "")
        if not use_scan_timeline:
            _metadata["shape"] = self._composites[node_id].shape
            return _metadata
        _scan_ndim = self._config["frozen_SCAN"].ndim
        _metadata["shape"] = (self._config["frozen_SCAN"].n_points,) + self._composites[
            node_id
        ].shape[_scan_ndim:]
        for _key, _entry in [
            ["axis_labels", "Chronological scan points"],
            ["axis_units", ""],
            ["axis_ranges", np.arange(self._config["frozen_SCAN"].n_points)],
        ]:
            _entries = [_entry] + list(_metadata[_key].values())[_scan_ndim:]
            _metadata[_key] = dict(enumerate(_entries))
        return _metadata

    def save_results_to_disk(
        self,
        save_dir: str | Path,
        *save_formats: tuple[str],
        overwrite: bool = False,
        node_id: int | None = None,
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
        save_formats : tuple[str]
            Strings of all formats to be written. Individual formats can be
            also be given in a single string if they are separated by comma
            (","), ampersand ("&") or slash ("/") characters.
        overwrite : bool, optional
            Flag to enable overwriting of existing files. The default is False.
        node_id : int | None, optional
            The node ID for which data shall be saved. If None, this defaults
            to all nodes. The default is None.
        """
        self.prepare_files_for_saving(
            save_dir, ",".join(save_formats), overwrite, single_node=node_id
        )
        if node_id is None:
            _res = self._composites
        else:
            _res = {node_id: self._composites[node_id]}
        ResultSaver.export_full_data_to_active_savers(
            _res, scan_context=self._config["frozen_SCAN"]
        )

    def prepare_files_for_saving(
        self,
        save_dir: str | Path,
        save_formats: str,
        overwrite: bool = False,
        single_node: int | None = None,
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
        single_node: int | None, optional
            Keyword to select a single node. If None, all nodes will be
            selected. The default is None.

        Raises
        ------
        FileExistsError
            If the directory exists and is not empty and overwrite is not
            enabled.
        """
        if not self._config["shapes_set"] or not self._config["metadata_complete"]:
            raise UserConfigError(
                "The shapes and metadata have not been set. Cannot save results yet."
            )
        save_dir = Path(save_dir) if isinstance(save_dir, str) else save_dir
        save_formats = [s.strip() for s in re.split("[&/,]", save_formats)]
        _name = self._config["frozen_SCAN"].get_param_value("scan_title")
        ResultSaver.set_active_savers_and_title(save_formats, _name)
        if single_node is None:
            _keys = list(self._composites.keys())
        else:
            _keys = [single_node]
        _node_info = {
            _id: {
                "shape": self._config["shapes"][_id],
                "node_label": self._config["node_labels"][_id],
                "plugin_name": self._config["plugin_names"][_id],
            }
            for _id in _keys
        }
        _names = ResultSaver.get_filenames_from_active_savers(self.node_labels)
        _exist_check = [save_dir.joinpath(_name).is_file() for _name in _names]
        if True in _exist_check and not overwrite:
            raise UserConfigError(
                f'The specified directory "{save_dir}" exists and is not empty. Please '
                "select a different directory."
            )
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
        ResultSaver.prepare_active_savers(
            save_dir,
            _node_info,
            scan_context=self._config["frozen_SCAN"],
            diffraction_exp=self._config["frozen_EXP"],
            workflow_tree=self._config["frozen_TREE"],
        )

    def update_param_choices_from_labels(
        self, param: Parameter, add_no_selection_entry: bool = True
    ):
        """
        Store the current ProcessingResults node labels in the specified
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
        _new_choices = ["No selection"] if add_no_selection_entry else []
        _new_choices.extend(list(self.result_titles.values()))
        param.update_value_and_choices(_new_choices[0], _new_choices)

    def get_node_result_metadata_string(
        self,
        node_id: int,
        use_scan_timeline: bool = False,
        squeeze_results: bool = True,
    ) -> str:
        """
        Get the edited metadata from ProcessingResults as a formatted string.

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
        _metadata = self.get_result_metadata(node_id, use_scan_timeline)
        _nscan = 1 if use_scan_timeline else self._config["frozen_SCAN"].ndim
        _print_info = {
            "axis_labels": list(_metadata["axis_labels"].values()),
            "axis_units": list(_metadata["axis_units"].values()),
            "axis_ranges": list(
                utils.get_range_as_formatted_string(_range)
                for _range in _metadata["axis_ranges"].values()
            ),
            "axis_types": (
                ["(scan)"] * _nscan + ["(data)"] * (self.ndims[node_id] - _nscan)
            ),
            "axis_points": list(_metadata["shape"]),
        }
        if squeeze_results:
            _squeezed_dims = np.where(np.asarray(_print_info["axis_points"]) == 1)[0]
            _print_info = {
                _key: [
                    _item
                    for _index, _item in enumerate(_print_info[_key])
                    if _index not in _squeezed_dims
                ]
                for _key in _print_info
            }
        _node_info = (
            self._config["plugin_names"][node_id]
            + ":\n\n"
            + f"Data: {self._composites[node_id].data_description}\n\n"
            + "".join(
                (
                    f"Axis #{_dim:02d} {_print_info['axis_types'][_dim]}:\n"
                    f"  Label: {_print_info['axis_labels'][_dim]}\n"
                    f"  N points: {_print_info['axis_points'][_dim]}\n"
                    f"  Range: {_print_info['axis_ranges'][_dim]} "
                    f"{_print_info['axis_units'][_dim]}\n"
                )
                for _dim, _ in enumerate(_print_info["axis_labels"])
            )
        )
        if self._composites[node_id].size == 1:
            _val = np.atleast_1d(self._composites[node_id].squeeze())[0]
            _node_info += f"Data zero-dimensional\n  Value: {_val:.6f}"
        return _node_info

    def import_data_from_directory(self, directory: str | Path):
        """
        Import data from a directory.

        Parameters
        ----------
        directory : Union[pathlib.Path, str]
            The input directory with the exported pydidas results.
        """
        self.clear_all_results()
        _import = ResultSaver.import_data_from_directory(directory)
        _data, _node_info, _scan, _exp, _tree = _import[:]
        for _key in ["shape", "node_label", "plugin_name", "result_title"]:
            self._config[f"{_key}s"] = {
                _id: _item[_key] for _id, _item in _node_info.items()
            }
        self._composites = _data
        if _data != {}:
            self._SCAN.update_from_scan(_scan)
            self._EXP.update_from_diffraction_exp(_exp)
            self._TREE.update_from_tree(_tree)
            self._config["frozen_SCAN"].update_from_scan(self._SCAN)
            self._config["frozen_EXP"].update_from_diffraction_exp(self._EXP)
            self._config["frozen_TREE"].update_from_tree(self._TREE)
            self._config["shapes_set"] = True
            self._config["metadata_complete"] = True
            for _id, _array in _data.items():
                self._config["plugin_res_metadata"][_id] = _array.property_dict
                self._config["plugin_res_metadata"][_id].pop("metadata")
