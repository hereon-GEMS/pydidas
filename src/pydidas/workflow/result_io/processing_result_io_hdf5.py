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
Module with the ProcessingResultIoHdf5 class which exports and imports results in
Hdf5 file format.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2026, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["ProcessingResultIoHdf5"]


from pathlib import Path
from typing import Any, ClassVar

import h5py
import numpy as np

from pydidas.contexts.diff_exp import DiffractionExperiment
from pydidas.contexts.diff_exp.diff_exp_io_hdf5 import DiffractionExperimentIoHdf5
from pydidas.contexts.scan import Scan
from pydidas.contexts.scan.scan_io_hdf5 import ScanIoHdf5
from pydidas.core import Dataset
from pydidas.core.constants import HDF5_EXTENSIONS
from pydidas.core.exceptions import FileReadError
from pydidas.core.utils.hdf5 import (
    nxs_create_recursive_groups,
    nxs_write_dataset,
    read_and_decode_hdf5_dataset,
)
from pydidas.core.utils.iterable_utils import (
    insert_item_in_tuple,
)
from pydidas.data_io import import_data
from pydidas.plugins.plugin_result_info import PluginResultInfo
from pydidas.workflow.processing_tree import ProcessingTree
from pydidas.workflow.processing_tree_io.processing_tree_io_hdf5 import (
    ProcessingTreeIoHdf5,
)
from pydidas.workflow.result_io.processing_result_io_base import ProcessingResultIoBase


class ProcessingResultIoHdf5(ProcessingResultIoBase):
    """
    Implementation of the ProcessingResultIoBase for HDF5 files.
    """

    extensions: ClassVar[list[str]] = HDF5_EXTENSIONS
    format_name = "NeXus (HDF5)"
    default_suffix = ".nxs"

    def __init__(self):
        super().__init__()
        self._config["metadata_written"] = False

    def prepare_files_and_directories(
        self,
        save_dir: Path | str,
        node_information: dict[int, PluginResultInfo],
        **kwargs: Any,
    ) -> None:
        """
        Prepare the hdf5 files with the metadata.

        Parameters
        ----------
        save_dir : Path or str
            The full path for the data to be saved.
        node_information : dict[int, PluginResultInfo]
            A dictionary with nodeID keys and PluginResultInfo values.
        **kwargs : Any
            Supported kwargs are:

            scan : Scan or None, optional
                The scan context. If None, the generic context will be
                used. Only specify this if you explicitly require a
                different context. The default is None.
            diffraction_exp : DiffractionExperiment or None, optional
                The diffraction experiment context. If None, the generic
                context will be used. Only specify this if you explicitly
                require a different context. The default is None.
            processing_tree : ProcessingTree or None, optional
                The ProcessingTree. If None, the generic ProcessingTree will
                be used. Only specify this if you explicitly require a
                different context. The default is None.
            squeeze : bool
                Flag whether to squeeze dimensions of size 1. The default
                is False.
        """
        super().prepare_files_and_directories(save_dir, node_information, **kwargs)
        for _index, _info in node_information.items():
            self._create_file_and_populate_metadata(_index, _info)

    def export_frame_to_file(
        self,
        index: int,
        frame_result_dict: dict[int, Dataset],
        **kwargs: Any,
    ) -> None:
        """
        Export the results of one frame and store them on disk.

        Parameters
        ----------
        index : int
            The frame index.
        frame_result_dict : dict[int, Dataset]
            The result dictionary with nodeID keys and result values.
        **kwargs : Any
            Not used in the HDF5 implementation.
        """
        _scan = self._config["scan"]
        _indices = _scan.get_indices_from_ordinal(index)
        if not self._config.get("metadata_written", False):
            _metadata = self._combine_scan_and_frame_metadata(frame_result_dict, _scan)
            self.create_result_nxdata_entry(_metadata)
        for _node_id, _data in frame_result_dict.items():
            _file_path = self._config["filenames"][_node_id]
            with h5py.File(_file_path, "r+") as _file:  # type: ignore[operator]
                _file["entry/data/data"][_indices] = _data

    def export_full_data_to_file(
        self,
        full_data: dict[int, Dataset],
        squeeze: bool = False,
    ) -> None:
        """
        Export the full dataset to disk.

        Parameters
        ----------
        full_data : dict[int, Dataset]
            The result dictionary with nodeID keys and result values.
        squeeze : bool, optional
            Flag to toggle squeezing of empty dimensions. If True, the data
            will be squeezed to remove empty dimensions. The default is False.
        """
        if not self._config.get("metadata_written", False):
            self.create_result_nxdata_entry(full_data, squeeze=squeeze)
        for _node_id, _data in full_data.items():
            if squeeze:
                _data = _data.squeeze()
            _file_path = self._config["filenames"][_node_id]
            with h5py.File(_file_path, "r+") as _file:  # type: ignore[operator]
                _file["entry/data/data"][()] = _data.array

    def create_result_nxdata_entry(
        self,
        result_metadata: dict[int, dict[str, Any]] | dict[int, Dataset],
        squeeze: bool = False,
    ) -> None:
        """
        Create the NXdata entry for the results.

        This method prepares the entry/data/data group in the NeXus file
        and writes all the necessary metadata to the file.
        Only the signal data itself needs to be written separately.

        Parameters
        ----------
        result_metadata : dict[int, dict[str, Any]] or dict[int, Dataset]
            The metadata in dictionary form with entries of the form
            node_id: node_metadata or node_id: Dataset.
        squeeze : bool, optional
            Flag to toggle squeezing of empty dimensions. If True, the data
            will be squeezed to remove empty dimensions. The default is False.
        """
        _scan_shape = self._config["scan"].shape
        _squeezed_scan_dims = (
            ";".join([str(i) for i, n in enumerate(_scan_shape) if n == 1])
            if squeeze
            else ""
        )
        for _id, _metadata in result_metadata.items():
            if isinstance(_metadata, Dataset):
                # convert the metadata to a dictionary if given as Dataset:
                if squeeze:
                    _metadata = _metadata.squeeze()
                _metadata = _metadata.property_dict
            _ndim = len(_metadata["axis_labels"])
            _shape = tuple(_ax.size for _ax in _metadata["axis_ranges"].values())
            _file_path = self._config["filenames"][_id]
            with h5py.File(_file_path, "r+") as _h5file:
                _nxdata_group = _h5file["entry/data"]
                _dset = _nxdata_group.create_dataset(
                    "data", shape=_shape, dtype=np.float32
                )
                _dset.attrs["units"] = _metadata.get("data_unit", "")
                _nxdata_group.attrs["title"] = _metadata.get("data_label", "")
                _nxdata_group.attrs["signal"] = "data"
                _nxdata_group.attrs["axes"] = [f"axis_{_i}" for _i in range(_ndim)]
                for _dim in range(_ndim):
                    _nxdata_group.attrs[f"axis_{_dim}_indices"] = [_dim]
                    nxs_write_dataset(
                        _nxdata_group,
                        f"axis_{_dim}",
                        _metadata["axis_ranges"][_dim],
                        units=_metadata["axis_units"][_dim],
                        long_name=_metadata["axis_labels"][_dim],
                        axis=_dim,
                    )
                nxs_write_dataset(
                    _h5file["entry/node_info"],
                    "squeezed_scan_dims",
                    _squeezed_scan_dims,
                )
        self._config["metadata_written"] = True

    update_result_metadata = create_result_nxdata_entry

    @staticmethod
    def import_results_from_file(
        filename: Path | str,
    ) -> tuple[Dataset, dict[str, Any], Scan, DiffractionExperiment, ProcessingTree]:
        """
        Import results from a file and store them as a Dataset.

        Parameters
        ----------
        filename : Path or str
            The full filename of the file to be imported.

        Returns
        -------
        data : Dataset
            The dataset with the imported data.
        node_info : dict[str, Any]
            A dictionary with node_label, data_label, plugin_name keys and
            the respective values.
        scan : Scan
            The imported scan configuration.
        diffraction_exp : DiffractionExperiment
            The imported diffraction experiment configuration.
        tree : ProcessingTree
            The imported workflow tree.
        """
        _tree = ProcessingTree()
        _scan = Scan()
        _exp = DiffractionExperiment()
        _data = import_data(filename, auto_squeeze=False)
        _scan.import_from_file(filename)
        _exp.import_from_file(filename)
        try:
            _tree = ProcessingTreeIoHdf5.import_from_file(filename)
        except (
            OSError,
            FileReadError,
            FileNotFoundError,
            PermissionError,
            TypeError,
            AttributeError,
            ValueError,
        ):
            raise FileReadError(
                "The given file does not conform to the pydidas results data "
                "standard and cannot be imported. Please check the input file."
            )
        with h5py.File(filename, "r") as _file:
            if "entry/node_info" in _file:
                _node_group = _file["entry/node_info"]
            else:
                _node_group = _file["entry/"]
            _info = {
                "node_label": read_and_decode_hdf5_dataset(_node_group["node_label"]),
                "plugin_name": read_and_decode_hdf5_dataset(_node_group["plugin_name"]),
                "node_id": read_and_decode_hdf5_dataset(_node_group["node_id"]),
            }
            _info["result_title"] = (
                f"{_info['node_label']} (node #{_info['node_id']:03d})"
                if len(_info["node_label"]) > 0
                else f"[{_info['plugin_name']}] (node #{_info['node_id']:03d})"
            )
            try:
                _squeeze_str = read_and_decode_hdf5_dataset(
                    _node_group["squeezed_scan_dims"]
                )
                if _squeeze_str:
                    _squeezed_scan_dims = [int(_s) for _s in _squeeze_str.split(";")]
                else:
                    _squeezed_scan_dims = []
            except (KeyError, ValueError, AttributeError):
                try:
                    _squeeze_str = read_and_decode_hdf5_dataset(
                        _file["entry/node_info/squeezed_scan_dims"]
                    )
                    if _squeeze_str:
                        _squeezed_scan_dims = [
                            int(_s) for _s in _squeeze_str.split(";")
                        ]
                    else:
                        _squeezed_scan_dims = []
                except (KeyError, ValueError, AttributeError):
                    _squeezed_scan_dims = None

        if _squeezed_scan_dims is None:
            # Check in files written before the squeezed_scan_dims flag
            # was introduced: if the scan has size-1 dims and the non-size-1
            # scan shape prefix matches the start of the data shape, those
            # size-1 dims were squeezed away during export.
            _size_1_scan_dims = [i for i, n in enumerate(_scan.shape) if n == 1]
            if _size_1_scan_dims:
                _scan_shape_no_ones = tuple(n for n in _scan.shape if n > 1)
                if _data.shape[: len(_scan_shape_no_ones)] == _scan_shape_no_ones:
                    _squeezed_scan_dims = _size_1_scan_dims
        if _squeezed_scan_dims is not None and len(_squeezed_scan_dims) > 0:
            _data = ProcessingResultIoHdf5._insert_squeezed_scan_dims(
                _data, _scan, _squeezed_scan_dims
            )
        _info["shape"] = _data.shape
        return _data, _info, _scan, _exp, _tree

    def _create_file_and_populate_metadata(
        self,
        node_id: int,
        result_info: PluginResultInfo,
    ) -> None:
        """
        Create a hdf5 file and populate it with the Scan metadata.

        Parameters
        ----------
        node_id : int
            The nodeID.
        result_info : PluginResultInfo
            The PluginResultInfo object for the node.
        """
        _file_path = self._config["filenames"][node_id]
        if _file_path.is_file():
            _file_path.unlink()
        ScanIoHdf5.export_to_file(_file_path, replace=True, scan=self._config["scan"])
        DiffractionExperimentIoHdf5.export_to_file(
            _file_path, replace=True, diffraction_exp=self._config["diffraction_exp"]
        )
        ProcessingTreeIoHdf5.export_to_file(
            _file_path, self._config["processing_tree"], replace=True
        )
        with h5py.File(_file_path, "a") as h5file:
            _node_info_group = nxs_create_recursive_groups(
                h5file, "entry/node_info", group_type="NXcollection"
            )
            nxs_write_dataset(_node_info_group, "node_id", node_id)
            nxs_write_dataset(_node_info_group, "node_label", result_info.label)
            nxs_write_dataset(_node_info_group, "plugin_name", result_info.plugin_name)
            nxs_create_recursive_groups(h5file, "entry/data", group_type="NXdata")

    @staticmethod
    def _combine_scan_and_frame_metadata(
        metadata: dict[int, Dataset] | dict[int, dict[str, Any]], scan: Scan
    ) -> dict[int, dict[str, Any]]:
        """
        Combine the scan metadata with the frame metadata.

        This method updates the metadata of the frame with the scan
        metadata.

        Parameters
        ----------
        metadata : dict[int, Dataset] or dict[int, dict[str, Any]]
            The result metadata in dictionary form with entries of the form
            node_id: node_metadata or node_id: Dataset.
            If the Dataset is given, the metadata will be read from the
            Dataset.
        scan : Scan
            The scan context to be used for metadata information.

        Returns
        -------
        dict[int, dict[str, Any]]
            The updated metadata in a dictionary.
        """
        _scan_meta = {
            "axis_labels": scan.axis_labels,
            "axis_units": scan.axis_units,
            "axis_ranges": scan.axis_ranges,
        }
        _new_metadata = {}
        for _id, _entry in metadata.items():
            _metadata: dict[str, Any] = (  # type: ignore[type]
                _entry.property_dict if isinstance(_entry, Dataset) else _entry
            )
            for _key in ["axis_labels", "axis_units", "axis_ranges"]:
                _result_metadata = list(_metadata[_key].values())
                _scan_metadata = _scan_meta[_key]
                _metadata[_key] = dict(enumerate(_scan_metadata + _result_metadata))
            _new_metadata[_id] = _metadata
        return _new_metadata

    @staticmethod
    def _insert_squeezed_scan_dims(
        data: Dataset,
        scan: Scan,
        dims: list[int],
    ) -> Dataset:
        """
        Re-insert scan dimensions of size 1 that were squeezed during export.

        Parameters
        ----------
        data : Dataset
            The squeezed Dataset to reconstruct.
        scan : Scan
            The scan context containing the full scan definition.
        dims : list[int]
            The scan dimension indices that were squeezed (any order).

        Returns
        -------
        Dataset
            The Dataset with the squeezed scan dims re-inserted.
        """
        _shape = data.shape
        for _dim in sorted(dims):
            _shape = insert_item_in_tuple(_shape, _dim, 1)
        data = data.reshape(_shape)  # type: ignore[type]
        for _dim in sorted(dims):
            _label, _unit, _range = scan.get_metadata_for_dim(_dim)
            data.update_axis_label(_dim, _label)
            data.update_axis_unit(_dim, _unit)
            data.update_axis_range(_dim, _range)
        return data
