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
Functions to create HDF5 files compatible with the pydidas HDF5 result
importer/exporter.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2026, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["create_hdf5_io_file", "create_hdf5_results_file"]


from pathlib import Path
from typing import Any, Iterable

import h5py  # type: ignore[import-untyped]

from pydidas.contexts import DiffractionExperiment, Scan
from pydidas.core import Dataset, UserConfigError
from pydidas.core.utils import iso_timestring
from pydidas.core.utils.hdf5.nxs_export import (
    nxs_create_nxentry,
    nxs_create_recursive_groups,
    nxs_param_config_for_dset,
    nxs_write_dataset,
    nxs_write_nxdata,
    nxs_write_root_metadata,
)
from pydidas.version import VERSION
from pydidas.workflow import ProcessingTree


def _get_keys(dset_key: str) -> tuple[str, str, str]:
    """
    Get the keys for the entry group, data group and dataset key from the input.

    Parameters
    ----------
    dset_key : str
        The key of the dataset to be returned.

    Returns
    -------
    str
        The key for the NXentry group.
    str
        The key for the NXdata group.
    str
        The key for the dataset.
    """
    _keys = dset_key.strip("/").split("/")
    if len(_keys) != 3:
        raise ValueError(
            "The dataset key must include exactly 3 elements in the form of "
            "root/dataset_group/dataset."
        )
    _root_group_name = _keys[0]
    _data_group_name = "/".join(_keys[0:2])
    _data_key = _keys[2]
    return _root_group_name, _data_group_name, _data_key


def create_hdf5_io_file(
    filename: Path | str,
    data: Dataset,
    **kwargs: Any,
) -> None:
    """
    Create a Hdf5 file from a dataset which can be read by the Hdf5 importer.

    Parameters
    ----------
    filename : str or Path
        The output filename.
    data : Dataset
        The data to be written.
    **kwargs : Any
        Any optional kwargs passed to the function. Supported arguments are

        dataset : str, optional
            The name of the hdf5 dataset where the data is stored. The default
            is entry/data/data
        write_mode : str, optional
            The mode to write the hdf5 file (`w`) or to append to the file
            (`r+`). The default is `w` for writing a new file.
    """
    _dataset = kwargs.get("dataset", "entry/data/data").strip("/")
    _root_group_name, _data_group_name, _data_key = _get_keys(_dataset)
    _mode = kwargs.get("write_mode", "w")
    with h5py.File(filename, _mode) as _h5file:
        nxs_write_root_metadata(_h5file)
        _root_group = nxs_create_nxentry(_h5file, entry=_root_group_name)
        _data_group = nxs_create_recursive_groups(
            _root_group, _data_group_name, group_type="NXdata"
        )
        nxs_write_nxdata(_data_group, _dataset, data)


def create_hdf5_results_file(
    filename: Path | str,
    data: Dataset,
    scan: Scan | dict[str, Any],
    diffraction_exp: DiffractionExperiment | dict[str, Any],
    processing_tree: ProcessingTree,
    **kwargs: Any,
) -> None:
    """
    Create a Hdf5 file from a dataset which can be read by the Hdf5 importer.

    This function explicitly does not use any of the generic exporters to check
    for consistency.

    Parameters
    ----------
    filename : str or Path
        The output filename.
    data : Dataset
        The data to be written.
    scan : Scan
        The Scan instance.
    diffraction_exp : DiffractionExperiment
        The DiffractionExperiment instance.
    processing_tree : ProcessingTree
        The ProcessingTree instance.
    **kwargs
        Any optional kwargs passed to the function. Supported arguments are

        dataset : str
            The name of the hdf5 dataset where the data is stored. The default
            is entry/data/data
        node_id : int, optional
            The node ID for the results. The default is 1.
        node_label : str, optional
            The label of the pydidas processing node. The default is "".
        plugin_name : str, optional
            The name of the pydidas plugin which `writes` this data.
            The default is "".
        scan_title : str, optional
            The scan title. The default is "".
        squeezed_scan_dims : list[int], optional
            The squeezed scan dimensions. The default is [].
    """
    _dataset = kwargs.get("dataset", "entry/data/data")
    _squeezed_dims = kwargs.get("squeezed_scan_dims", "")
    if _squeezed_dims:
        if isinstance(_squeezed_dims, str):
            pass
        elif isinstance(_squeezed_dims, Iterable):
            _squeezed_dims = ";".join(str(_item) for _item in _squeezed_dims)
        else:
            raise UserConfigError(
                "Squeezed scan dimensions must be a string or an iterable of integers."
            )
    _root_group_name, _data_group_name, _data_key = _get_keys(_dataset)
    if _root_group_name == "":
        raise UserConfigError(
            "The hdf5 dataset path is too shallow to allow writing all metadata. "
            "Please specify a dataset path with at least two groups levels, e.g. "
            "`entry/data/data`."
        )
    create_hdf5_io_file(filename, data, dataset=_dataset)
    with h5py.File(filename, "r+") as _file:
        _root = _file[_root_group_name]
        _node_group = nxs_create_recursive_groups(
            _root, "node_info", group_type="NXcollection"
        )
        _node_group.create_dataset("node_id", data=kwargs.get("node_id", 1))
        _node_group.create_dataset("node_label", data=kwargs.get("node_label", ""))
        _node_group.create_dataset("plugin_name", data=kwargs.get("plugin_name", ""))
        if _squeezed_dims:
            _node_group.create_dataset("squeezed_scan_dims", data=_squeezed_dims)

        # export Scan:
        _scan_group = nxs_create_recursive_groups(
            _root, "pydidas_scan", group_type="NXparameters"
        )
        for _key, _param in scan.params.items():
            _val, _attributes = nxs_param_config_for_dset(_param)
            nxs_write_dataset(_scan_group, _key, _val, **_attributes)

        # export DiffractionExp:
        _diff_exp_group = nxs_create_recursive_groups(
            _root, "pydidas_diffraction_exp", group_type="NXcollection"
        )
        for _key, _param in diffraction_exp.params.items():
            _val, _attributes = nxs_param_config_for_dset(_param)
            nxs_write_dataset(_diff_exp_group, _key, _val, **_attributes)

        # Export ProcessingTree:
        _workflow_group = nxs_create_recursive_groups(
            _root, "pydidas_workflow", group_type="NXprocess"
        )
        nxs_write_dataset(_workflow_group, "program", "pydidas")
        nxs_write_dataset(_workflow_group, "version", VERSION)
        nxs_write_dataset(_workflow_group, "date", iso_timestring())
        nxs_write_dataset(_workflow_group, "sequence_index", 1)
        _config_group = nxs_create_recursive_groups(
            _workflow_group, "workflow_info", group_type="NXparameters"
        )
        _node_names = [
            f"workflow_node_{_id:02d}" for _id in processing_tree.nodes.keys()
        ]
        nxs_write_dataset(_config_group, "nodes", _node_names)
        nxs_write_dataset(_config_group, "num_nodes", len(processing_tree.nodes))
        for _id, _node in processing_tree.nodes.items():
            _param_group = nxs_create_recursive_groups(
                _workflow_group, f"workflow_node_{_id:02d}", group_type="NXparameters"
            )
            _node_data = _node.dump()
            for _key in ["node_id", "parent", "children", "plugin_class"]:
                nxs_write_dataset(_param_group, _key, _node_data[_key])
            for _key, _param in _node.plugin.params.items():
                if _key.startswith("_"):
                    continue
                _val, _attributes = nxs_param_config_for_dset(_param)
                nxs_write_dataset(_param_group, _key, _val, **_attributes)
