# This file is part of pydidas.
#
# Copyright 2023 - 2026, Helmholtz-Zentrum Hereon
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
__copyright__ = "Copyright 2023 - 2026, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["ProcessingResults"]


import re
from copy import deepcopy
from pathlib import Path
from typing import Any

import numpy as np

from pydidas.contexts import (
    DiffractionExperiment,
    DiffractionExperimentContext,
    Scan,
    ScanContext,
)
from pydidas.core import (
    Dataset,
    ObjectWithParameterCollection,
    UserConfigError,
)
from pydidas.plugins.plugin_result_info import PluginResultInfo
from pydidas.workflow.processing_result_saver import ProcessingResultSaver
from pydidas.workflow.processing_tree import ProcessingTree
from pydidas.workflow.result_io import ProcessingResultIoMeta as ResultIo
from pydidas.workflow.workflow_tree import WorkflowTree


_STANDARD_CONFIG = {
    "metadata_complete": False,
    "composites_created": False,
    "saver_metadata_set": False,
}


class ProcessingResults(ObjectWithParameterCollection):
    """
    A class for handling composite data from multiple plugins.

    This class handles Datasets from each plugin in the WorkflowTree. Results
    are referenced by the node ID of the data's producer.

    Warning: Users should generally only use the WorkflowResults singleton
    and never use the ProcessingResults directly unless explicitly required.

    Parameters
    ----------
    scan : Scan, optional
        The scan context. If None, the generic context will be used. Only specify this,
        if you explicitly require a different context. The default is None.
    diffraction_exp : DiffractionExperiment, optional
        The diffraction experiment context. If None, the generic context will be used.
        Only specify this if you explicitly require a different context. The default
        is None.
    processing_tree : ProcessingTree, optional
        The ProcessingTree. If None, the generic WorkflowTree will be used.
        Only specify this if you explicitly require a different context.
        The default is None.
    directory : str or Path, optional
        Directory to load ProcessingResults data from.
    """

    def __init__(
        self,
        scan: Scan | None = None,
        diffraction_exp: DiffractionExperiment | None = None,
        processing_tree: ProcessingTree | None = None,
        directory: str | Path | None = None,
    ):
        super().__init__(parent=None)
        self.set_default_params()
        self._scan = ScanContext() if scan is None else scan
        self._exp = (
            DiffractionExperimentContext()
            if diffraction_exp is None
            else diffraction_exp
        )
        self._tree = WorkflowTree() if processing_tree is None else processing_tree
        self._saver = ProcessingResultSaver()
        self._config: dict[str, Any] = {
            "frozen_scan": Scan(),
            "frozen_exp": DiffractionExperiment(),
            "frozen_tree": ProcessingTree(),
        } | _STANDARD_CONFIG
        self._composites: dict[int, Dataset] = {}
        self._plugin_result_infos: dict[int, PluginResultInfo] = {}
        self._source_hash: int = -1
        if directory is not None:
            self.import_data_from_directory(directory)

    # ------------------
    # Public properties:
    # ------------------

    @property
    def scan_instance(self) -> Scan:
        """Return the current scan instance."""
        return self._scan

    @property
    def diff_exp_instance(self) -> DiffractionExperiment:
        """Return the current diffraction experiment instance."""
        return self._exp

    @property
    def proc_tree_instance(self) -> ProcessingTree:
        """Return the current processing tree instance."""
        return self._tree

    @property
    def shapes(self) -> dict[int, tuple[int, ...]]:
        """
        Return the shapes of the results in the form of a dictionary.

        Returns
        -------
        dict[int, tuple[int, ...]]
            A dictionary with entries of the form <node_id: results_shape>
        """
        return {_key: _item.shape for _key, _item in self._plugin_result_infos.items()}

    @property
    def ndims(self) -> dict[int, int]:
        """
        Return a dictionary with the number of dimensions for each of the results.

        Returns
        -------
        dict[int, int]
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
        return self._config.get("frozen_tree", ProcessingTree())

    @property
    def frozen_exp(self) -> DiffractionExperiment:
        """
        Get the frozen instance of the DiffractionExperiment context.

        Returns
        -------
        DiffractionExperiment
            The DiffractionExperiment at the time of processing.
        """
        return self._config.get("frozen_exp", DiffractionExperiment())

    @property
    def frozen_scan(self) -> Scan:
        """
        Get the frozen instance of the Scan context.

        Returns
        -------
        Scan
            The Scan at the time of processing.
        """
        return self._config.get("frozen_scan", Scan())

    @property
    def source_hash(self) -> int:
        """
        Get the source hash from the input WorkflowTree ans ScanContext.

        Returns
        -------
        int
            The hash value of the combined input data.
        """
        self._source_hash = hash((hash(self._scan), hash(self._tree), hash(self._exp)))
        return self._source_hash

    @property
    def result_titles(self) -> dict[int, str]:
        """
        Return a dictionary with the result titles for all node IDs.

        Returns
        -------
        dict[int, str]
            The result titles in the form of a dictionary with <node_id: result_title>
            entries.
        """
        return {
            _key: _item.result_title
            for _key, _item in self._plugin_result_infos.items()
        }

    # ------------------
    # Public methods:
    # ------------------

    def clear_all_results(self) -> None:
        """Clear all internally stored results and reset the instance attributes."""
        self._composites = {}
        self._saver.set_active_savers(None)
        self._plugin_result_infos = {}
        self._source_hash = -1
        self._config.update(_STANDARD_CONFIG)

    def prepare_new_results(self) -> None:
        """Prepare the ProcessingResults for newly created results."""
        self.clear_all_results()
        for _node in self._tree.get_all_nodes_with_results():
            _node_id: int = _node.node_id  # type: ignore[type]
            self._plugin_result_infos[_node_id] = _node.plugin.plugin_result_info
        self._source_hash = hash((hash(self._scan), hash(self._tree), hash(self._exp)))
        self._config["frozen_scan"].update_from_scan(self._scan)
        self._config["frozen_exp"].update_from_diffraction_exp(self._exp)
        self._config["frozen_tree"].update_from_tree(self._tree)
        self._config["frozen_tree"].prepare_execution()

    def update_result_metadata(
        self, metadata: dict[int, Dataset] | dict[int, dict[str, Any]]
    ) -> None:
        """
        Update the stored metadata from plugin results.

        Parameters
        ----------
        metadata : dict[int, Dataset] or dict[int, dict[str, Any]]
            The metadata in form of a dictionary with nodeID keys and dict
            items containing the axis_units, -_labels, and -_ranges keys with
            the associated data. Alternatively, the Datasets can also be used
            directly as dict values.
        """
        _scan_shape = self._config["frozen_scan"].shape
        _scan_meta = {
            "axis_labels": self._config["frozen_scan"].axis_labels,
            "axis_units": self._config["frozen_scan"].axis_units,
            "axis_ranges": self._config["frozen_scan"].axis_ranges,
        }
        for _node_id, _meta in metadata.items():
            if isinstance(_meta, Dataset):
                _meta = _meta.property_dict
            _info = self._plugin_result_infos[_node_id]
            for _key in ["axis_labels", "axis_units", "axis_ranges"]:
                _val = dict(enumerate(_scan_meta[_key] + list(_meta[_key].values())))
                setattr(_info, _key, _val)
            _info.data_label = _meta.get("data_label", "")
            _info.data_unit = _meta.get("data_unit", "")
            _info.scan_ndim = self._config["frozen_scan"].ndim
        self._config["metadata_complete"] = True
        self._update_composite_metadata()

    def store_scan_point_results(
        self, index: int, results: dict[int, Dataset], autosave: bool = False
    ) -> None:
        """
        Store results from one scan point in the ProcessingResults.

        Parameters
        ----------
        index : int
            The index of the scan point.
        results: dict[int, Dataset]
            The results as dictionary with entries of the type
            <node_id: array>.
        autosave : bool
            Flag whether to export the new data directly to the savers.
            The default is False.
        """
        if not self._config["metadata_complete"]:
            self.update_result_metadata(results)
        if not self._config["saver_metadata_set"]:
            _info = {_id: _val.property_dict for _id, _val in self._composites.items()}
            self._saver.update_saver_metadata(_info)
            self._config["saver_metadata_set"] = True
        _scan_index = self._scan.get_indices_from_ordinal(index)
        for _key, _val in results.items():
            self._composites[_key][_scan_index] = _val
        if autosave:
            self._saver.export_frame_to_active_savers(index, results)

    def get_result_ranges(self, node_id: int) -> dict[int, np.ndarray]:
        """
        Get the data ranges for the requested node id.

        Parameters
        ----------
        node_id : int
            The node ID for which the result ranges should be returned.

        Returns
        -------
        dict[int, np.ndarray]
            The dictionary with the ranges with dimension keys and ranges
            values.
        """
        self._check_that_results_are_available(node_id)
        return self._plugin_result_infos[node_id].axis_ranges

    def get_results(
        self,
        node_id: int,
        squeeze: bool = False,
        flatten_scan_dims: bool = False,
        copy: bool = True,
    ) -> Dataset:
        """
        Get the combined results for the requested node_id.

        The squeeze and flatten_scan_dims flags can be used to modify
        the shape of the returned dataset. Please see the Parameter
        documentation below for more information.

        Parameters
        ----------
        node_id : int
            The node ID for which results should be returned.
        squeeze: bool
            Flag to squeeze the results of the requested node ID to
            remove dimensions of size 1.
        flatten_scan_dims: bool
            Flag to flatten all result dimensions of the Scan into
            a single timeline. All other dimensions are unchanged.
            This option can be combined with squeeze.
        copy : bool
            Flag to return a copy of the results. If False, the ndarray
            will be returned and the data can be changed in place.
            The default is True.

        Returns
        -------
        Dataset
            The combined results of all frames for a specific node.
        """
        self._check_that_results_are_available(node_id)
        _data = self._composites[node_id]
        if copy:
            _data = _data.copy()
        if flatten_scan_dims:
            _data.flatten_dims(
                *range(self._config["frozen_scan"].ndim),
                new_dim_label="Chronological scan points",
                new_dim_range=np.arange(self._config["frozen_scan"].n_points),
            )
        if squeeze:
            return _data.squeeze()
        return _data

    def get_result_subset(
        self,
        node_id: int,
        *slices: int | tuple[int] | slice,
        flatten_scan_dims: bool = False,
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
        *slices : int or tuple[int] or slice
            The integer, tuple or slice  used for indexing the np.ndarray.
        flatten_scan_dims : bool
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
        _slice_types = {type(_slice) for _slice in slices}
        _data = self.get_results(
            node_id, flatten_scan_dims=flatten_scan_dims, copy=False
        )
        if _slice_types.issubset({int, slice}):
            _data = _data[slices].copy()  # type: ignore[arg-type]
        else:
            for _index, _slice in enumerate(slices[::-1]):  # type: ignore[arg-type]
                _dim = len(slices) - _index - 1  # type: ignore[arg-type]
                _data = _data.take(_slice, axis=_dim)
        if squeeze:
            return _data.squeeze()
        return _data

    def prepare_result_export(
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
        save_dir : str or Path
            The basepath for all saved data.
        save_formats : str
            A string of all formats to be written. Individual formats can be
            separated by comma (","), ampersand ("&") or slash ("/")
            characters.
        overwrite : bool
            Flag to enable overwriting of existing files. The default is False.
        single_node: int or None
            Keyword to select a single node. If None, all nodes will be
            selected. The default is None.
        """
        _save_path = Path(save_dir)
        if not self._config["metadata_complete"]:
            raise UserConfigError(
                "The metadata has not been set from the results yet. Cannot "
                "save results."
            )
        _format_list = [s.strip() for s in re.split("[&/,]", save_formats)]
        self._saver.set_active_savers(_format_list)
        self._export_result_info = (
            {single_node: self._plugin_result_infos[single_node]}
            if single_node
            else self._plugin_result_infos.copy()
        )
        _names = self._saver.expected_export_filenames(self._export_result_info)
        if any((_save_path / _name).is_file() for _name in _names) and not overwrite:
            raise UserConfigError(
                f"The specified directory `{_save_path}` exists and is not empty. "
                "Please select a different directory."
            )
        self._saver.prepare_active_savers(
            _save_path,
            self._export_result_info,
            scan=self._config["frozen_scan"],
            diffraction_exp=self._config["frozen_exp"],
            processing_tree=self._config["frozen_tree"],
        )

    def save_results_to_disk(
        self,
        save_dir: str | Path,
        *save_formats: str,
        overwrite: bool = False,
        squeeze: bool = False,
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
        save_dir : str or Path
            The basepath for all saved data.
        save_formats : str
            Strings of all formats to be written. Individual formats can be
            also be given in a single string if they are separated by comma
            (","), ampersand ("&") or slash ("/") characters.
        overwrite : bool
            Flag to enable overwriting of existing files. The default is False.
        squeeze : bool
            Flag to enable squeezing of empty dimensions. The default is False.
        node_id : int or None, optional
            The node ID for which data shall be saved. If None, this defaults
            to all nodes. The default is None.
        """
        self.prepare_result_export(
            save_dir,
            ",".join(save_formats),
            overwrite,
            single_node=node_id,
        )
        if node_id is None:
            _res = self._composites
        else:
            _res = {node_id: self._composites[node_id]}
        self._saver.export_full_data_to_active_savers(
            _res,
            squeeze=squeeze,
        )

    # alias
    export_data_to_directory = save_results_to_disk

    def get_node_result_metadata_string(
        self,
        node_id: int,
        use_scan_timeline: bool = False,
        squeeze: bool = True,
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
        squeeze : bool, optional
            Flag whether to squeeze the results (i.e. remove all dimensions of length 1)
            from the data. The default is True.

        Returns
        -------
        str :
            The formatted string with a representation of all the metadata.
        """
        self._check_that_results_are_available(node_id)
        _result_info = self._plugin_result_infos[node_id]
        _metadata = _result_info.get_metadata(use_scan_timeline, squeeze)
        _node_info = (
            _result_info.plugin_name
            + ":\n\n"
            + f"Data: {self._composites[node_id].data_description}\n\n"
            + "".join(
                (
                    f"Axis #{_dim:02d} {_metadata['axis_types'][_dim]}:\n"
                    f"  Label: {_label}\n"
                    f"  N points: {_metadata['shape'][_dim]}\n"
                    f"  Range: {_metadata['axis_ranges'][_dim]} "
                    f"{_metadata['axis_units'][_dim]}\n"
                )
                for _dim, _label in enumerate(_metadata["axis_labels"])
            )
        )
        if self._composites[node_id].size == 1:
            _val = np.atleast_1d(self._composites[node_id].squeeze())[0]
            _node_info += f"Data zero-dimensional\n  Value: {_val:.6f}"
        return _node_info

    def import_data_from_directory(self, directory: Path | str):
        """
        Import data from a directory.

        Parameters
        ----------
        directory : Path or str
            The input directory with the exported pydidas results.
        """
        self.clear_all_results()
        _import = ResultIo.import_data_from_directory(directory)
        _data, _node_info, _scan, _exp, _tree = _import[:]
        for _id, _metadata in _node_info.items():
            _curr_data = _data[_id]
            _res_info = PluginResultInfo(
                label=_metadata["node_label"],
                node_id=_id,
                plugin_name=_metadata["plugin_name"],
                result_title=_metadata["result_title"],
            )
            _res_info.dataset_metadata = _data[_id].property_dict
            _res_info.scan_ndim = _scan.ndim
            self._plugin_result_infos[_id] = _res_info
        self._composites = _data
        if _data != {}:
            self._scan.update_from_scan(_scan)
            self._exp.update_from_diffraction_exp(_exp)
            self._tree.update_from_tree(_tree)
            self._config["frozen_scan"].update_from_scan(self._scan)
            self._config["frozen_exp"].update_from_diffraction_exp(self._exp)
            self._config["frozen_tree"].update_from_tree(self._tree)
            self._config["metadata_complete"] = True

    def update_from_processing_results(self, results: "ProcessingResults"):
        """
        Update the current ProcessingResults from another instance.

        Parameters
        ----------
        results : ProcessingResults
            The other ProcessingResults instance to update from.
        """
        if not isinstance(results, ProcessingResults):
            raise TypeError("The provided object is not a ProcessingResults instance.")
        self._scan.update_from_scan(results.scan_instance)
        self._exp.update_from_diffraction_exp(results.diff_exp_instance)
        self._tree.update_from_tree(results.proc_tree_instance)
        self._config["frozen_scan"].update_from_scan(self._scan)
        self._config["frozen_exp"].update_from_diffraction_exp(self._exp)
        self._config["frozen_tree"].update_from_tree(self._tree)
        self._composites = {
            _key: deepcopy(_val) for _key, _val in results._composites.items()
        }
        self._config = {_key: deepcopy(_val) for _key, _val in results._config.items()}
        self._plugin_result_infos = deepcopy(results._plugin_result_infos)

    # ------------------
    # Private methods:
    # ------------------

    def _create_composites(self) -> None:
        """Create the composite datasets for all node results."""
        if not self._config["metadata_complete"]:
            raise UserConfigError(
                "The shapes of the results have not been set. Please set the shapes "
                "before storing results."
            )
        self._composites = {
            _node_id: Dataset(
                np.full(_info.shape, np.nan, dtype=np.float32),
                **_info.dataset_metadata,
            )
            for _node_id, _info in self._plugin_result_infos.items()
        }
        self._config["composites_created"] = True

    def _update_composite_metadata(self) -> None:
        """Update the metadata of the composite datasets with the stored metadata."""
        if not self._config["composites_created"]:
            self._create_composites()
        for _node_id, _metadata in self._plugin_result_infos.items():
            _metadata = self._plugin_result_infos[_node_id].dataset_metadata
            self._composites[_node_id].axis_labels = _metadata["axis_labels"]
            self._composites[_node_id].axis_units = _metadata["axis_units"]
            self._composites[_node_id].axis_ranges = _metadata["axis_ranges"]
            self._composites[_node_id].data_label = _metadata["data_label"]
            self._composites[_node_id].data_unit = _metadata["data_unit"]

    def _check_that_results_are_available(self, node_id: int) -> None:
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
