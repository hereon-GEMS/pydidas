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


import os.path
from pathlib import Path
from typing import Any, Iterable

import h5py  # type: ignore[import-untyped]

from pydidas.contexts import DiffractionExperiment, Scan
from pydidas.core import Dataset, UserConfigError
from pydidas.version import VERSION
from pydidas.workflow import ProcessingTree


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
    _dataset = kwargs.get("dataset", "entry/data/data")
    _data_group_name = os.path.dirname(_dataset)
    _root_group_name = os.path.dirname(_data_group_name)  # type: ignore[arg-type]
    _key = os.path.basename(_dataset)
    _mode = kwargs.get("write_mode", "w")
    with h5py.File(filename, _mode) as _file:
        _root_group = _file.create_group(_root_group_name)
        _data_group = _file.create_group(_data_group_name)
        _root_group.create_dataset("data_label", data=data.data_label)
        _root_group.create_dataset("data_unit", data=data.data_unit)
        _data_group.create_dataset(_key, data=data.array)
        for _dim in range(data.ndim):
            _group = _data_group.create_group(f"axis_{_dim}")
            _group.create_dataset("label", data=data.axis_labels[_dim])
            _group.create_dataset("unit", data=data.axis_units[_dim])
            _group.create_dataset("range", data=data.axis_ranges[_dim])


def create_hdf5_results_file(
    filename: Path | str,
    data: Dataset,
    scan: Scan | dict,
    diffraction_exp: DiffractionExperiment | dict,
    workflow: ProcessingTree | str,
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
    scan : Scan or dict
        The Scan or its parameter. The Scan can be either passed as instance
        or its Parameter keys and values as dict (in exportable types).
    diffraction_exp : DiffractionExperiment or dict
        The DiffractionExperiment or its parameter. The DiffractionExperiment
        can be either passed as instance or its Parameter keys and values as
        dict (in exportable types).
    workflow : ProcessingTree or str
        The ProcessingTree instance or its string representation.
    **kwargs
        Any optional kwargs passed to the function. Supported arguments are

        dataset : str
            The name of the hdf5 dataset where the data is stored.
        node_id : int, optional
            The node ID for the results. The default is -1.
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
    if isinstance(scan, Scan):
        scan = scan.get_param_values_as_dict(filter_types_for_export=True)
    if isinstance(diffraction_exp, DiffractionExperiment):
        diffraction_exp = diffraction_exp.get_param_values_as_dict(
            filter_types_for_export=True
        )
    if isinstance(workflow, ProcessingTree):
        workflow = workflow.export_to_string()
    _dataset = kwargs.get("dataset", "entry/data/data")
    _dataset_inner = os.path.dirname(_dataset)  # type: ignore[arg-type]
    _root_group_name = os.path.dirname(_dataset_inner)  # type: ignore[arg-type]
    if _root_group_name == "":
        raise UserConfigError(
            "The hdf5 dataset path is too shallow to allow writing all metadata. "
            "Please specify a dataset path with at least two groups levels, e.g. "
            "`entry/data/data`."
        )
    create_hdf5_io_file(filename, data, dataset=_dataset)
    with h5py.File(filename, "r+") as _file:
        _root = _file[_root_group_name]
        _config_group = _root.create_group("pydidas_config")
        _scan_group = _root.create_group("pydidas_config/scan")
        _diff_exp_group = _root.create_group("pydidas_config/diffraction_exp")
        _root.create_dataset("node_id", data=kwargs.get("node_id", -1))
        _root.create_dataset("node_label", data=kwargs.get("node_label", ""))
        _root.create_dataset("plugin_name", data=kwargs.get("plugin_name", ""))
        _root.create_dataset("scan_title", data=kwargs.get("scan_title", ""))
        _squeezed_dims = kwargs.get("squeezed_scan_dims", "")
        if _squeezed_dims:
            if isinstance(_squeezed_dims, Iterable):
                _squeezed_dims = ",".join(str(_item) for _item in _squeezed_dims)
            if not isinstance(_squeezed_dims, str):
                raise UserConfigError(
                    "Squeezed scan dimensions must be a string or list of integers."
                )
        _config_group.create_dataset("squeezed_scan_dims", data=_squeezed_dims)
        for _key, _value in scan.items():
            _scan_group.create_dataset(_key, data=_value)
        for _key, _value in diffraction_exp.items():
            _diff_exp_group.create_dataset(_key, data=_value)
        _config_group.create_dataset("workflow", data=workflow)
        _config_group.create_dataset("pydidas_version", data=VERSION)
