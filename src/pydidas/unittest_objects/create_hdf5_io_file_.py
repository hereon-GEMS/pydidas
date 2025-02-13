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
Function to create hdf5 files which are compatible with the ProcessingResults hdf5
importer/exporter.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["create_hdf5_io_file", "create_hdf5_results_file"]


import os.path
from pathlib import Path
from typing import NewType, Union

import h5py

from pydidas.contexts import DiffractionExperiment, Scan
from pydidas.core import Dataset, UserConfigError
from pydidas.version import VERSION
from pydidas.workflow import ProcessingTree


WorkflowTree = NewType("WorkflowTree", type)


def create_hdf5_results_file(
    filename: Union[Path, str],
    data: Dataset,
    scan: Union[Scan, dict],
    diffraction_exp: Union[DiffractionExperiment, dict],
    workflow: Union[WorkflowTree, str],
    **kwargs: dict,
):
    """
    Create a Hdf5 file from a dataset which can be read by the Hdf5 importer.

    Parameters
    ----------
    filename : Union[str, pathlib.Path]
        The output filename.
    data : Dataset
        The data to be written.
    scan : Union[Scan, dict]
        The Scan or its parameter. The Scan can be either passed as instance or
         its Parameter keys and values as dict (in exportable types).
    diffraction_exp : Union[DiffractionExperiment, dict]
        The DiffractionExperiment or its parameter. The DiffractionExperiment
        can be either passed as instance or its Parameter keys and values as dict
        (in exportable types).
    workflow : Union[WorkflowTree, str]
        The WorkflowTree instance or its string representation.
    **kwargs : dict
        Any optional kwargs passed to the function. Supported arguments are

        dataset : str
            The name of the hdf5 dataset where the data is stored.
        node_label : str
            The label of the pydidas processing node.
        plugin_name : str
            The name of the pydidas plugin which `writes` this data.
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
    _root_group_name = os.path.dirname(os.path.dirname(_dataset))
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
        for _key, _value in scan.items():
            _scan_group.create_dataset(_key, data=_value)
        for _key, _value in diffraction_exp.items():
            _diff_exp_group.create_dataset(_key, data=_value)
        _config_group.create_dataset("workflow", data=workflow)
        _config_group.create_dataset("pydidas_version", data=VERSION)


def create_hdf5_io_file(
    filename: Union[Path, str],
    data: Dataset,
    **kwargs: dict,
):
    """
    Create a Hdf5 file from a dataset which can be read by the Hdf5 importer.

    Parameters
    ----------
    filename : Union[str, pathlib.Path]
        The output filename.
    data : Dataset
        The data to be written.
    **kwargs : dict
        Any optional kwargs passed to the function. Supported arguments are

        dataset : str, optional
            The name of the hdf5 dataset where the data is stored. The default
            is entry/data/data
        write_mode : str, optional
        The mode to write the hdf5 file (`w`) or to append to the file (`r+`).
        The default is `w` for writing a new file.
    """
    _dataset = kwargs.get("dataset", "entry/data/data")
    _data_group_name = os.path.dirname(_dataset)
    _root_group_name = os.path.dirname(_data_group_name)
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
