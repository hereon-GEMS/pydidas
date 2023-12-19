# This file is part of pydidas.
#
# Copyright 2023, Helmholtz-Zentrum Hereon
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
Function to create hdf5 files which are compatible with the WorkflowResults hdf5
importer/exporter.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["create_hdf5_io_file"]


from pathlib import Path
from typing import NewType, Union

import h5py

from pydidas.core import Dataset
from pydidas.core.utils import create_hdf5_dataset


WorkflowTree = NewType("WorkflowTree", type)


def create_hdf5_io_file(
    filename: Union[Path, str],
    data: Dataset,
    scan_params: dict,
    diffraction_exp_params: dict,
    workflow: WorkflowTree,
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
    scan_params : dict
        The scan parameter keys and values (in exportable types).
    diffraction_exp_params : dict
        The diffraction experiment parameter keys and values (in exportable types).
    workflow : WorkflowTree
        The WorkflowTree instance.
    **kwargs : dict
        Any optional kwargs passed to the function.
    """
    with h5py.File(filename, "w") as _file:
        _file.create_group("entry")
        _file.create_group("entry/data")
        _file.create_group("entry/pydidas_config")
        _file.create_group("entry/pydidas_config/scan")
        _file.create_group("entry/pydidas_config/diffraction_exp")
        _file["entry"].create_dataset("node_id", data=6)
        _file["entry"].create_dataset("node_label", data=kwargs.get("node_label", ""))
        _file["entry"].create_dataset("plugin_name", data=kwargs.get("plugin_name", ""))
        _file["entry"].create_dataset("data_label", data=data.data_label)
        _file["entry"].create_dataset("data_unit", data=data.data_unit)
        _file["entry/data"].create_dataset("data", data=data.array)
        for _key, _value in scan_params.items():
            _file["entry/pydidas_config/scan"].create_dataset(_key, data=_value)
        for _key, _value in diffraction_exp_params.items():
            _file["entry/pydidas_config/diffraction_exp"].create_dataset(
                _key, data=_value
            )
        _file["entry/pydidas_config"].create_dataset(
            "workflow", data=workflow.export_to_string()
        )
        for _dim in range(data.ndim):
            create_hdf5_dataset(
                _file,
                f"entry/data/axis_{_dim}",
                "label",
                data=data.axis_labels[_dim],
            )
            create_hdf5_dataset(
                _file,
                f"entry/data/axis_{_dim}",
                "unit",
                data=data.axis_units[_dim],
            )
            create_hdf5_dataset(
                _file,
                f"entry/data/axis_{_dim}",
                "range",
                data=data.axis_ranges[_dim],
            )
        for _dim in range(scan_params["scan_dim"]):
            create_hdf5_dataset(
                _file,
                f"entry/scan/dim_{_dim}",
                "range",
                data=data.axis_ranges[_dim],
            )
            create_hdf5_dataset(
                _file,
                f"entry/scan/dim_{_dim}",
                "label",
                data=data.axis_labels[_dim],
            )
            create_hdf5_dataset(
                _file,
                f"entry/scan/dim_{_dim}",
                "unit",
                data=data.axis_units[_dim],
            )
