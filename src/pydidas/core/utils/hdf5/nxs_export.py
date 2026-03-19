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
Module with utility functions to crawl HDF5 files / groups and determine
a list of all dataset keys which fulfill certain filter criteria.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2026, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = [
    "create_nx_entry_groups",
    "create_nx_dataset",
    "create_nxdata_entry",
    "export_context_to_nxs",
    "nx_dataset_config_from_param",
]


import os
from numbers import Integral, Number, Real
from pathlib import Path
from typing import Any

import h5py
import numpy as np

from pydidas.core.dataset import Dataset
from pydidas.core.object_with_parameter_collection import ObjectWithParameterCollection
from pydidas.core.parameter import Parameter


def create_nx_entry_groups(
    parent: h5py.File | h5py.Group,
    group_name: str,
    group_type: str = "NXdata",
    **attributes: Any,
) -> h5py.Group:
    """
    Create the NXentry groups recursively in the HDF5 file and return the final
    group.

    Note that the final group is set to be a NXdata group unless the `group_type`
    is specified differently. If the group already exists, the function will
    only update (and replace existing) metadata.

    Parameters
    ----------
    parent: h5py.File or h5py.Group
        The parent group or file object.
    group_name : str
        The name of the group to be created.
    group_type : str, optional
        The type of the last group. The default is "NXdata".
    **attributes : Any
        The attributes to be set for the last group.

    Returns
    -------
    h5py.Group
        The final group object which is accessed by the given group_name.
    """
    if group_name in parent:
        _group = parent[group_name]
        if _group.attrs.get("NX_class", "") != group_type:
            raise ValueError(
                f"Error when creating the group {group_name}: The group already exists "
                f"but is not of specified type {group_type} (existing group: "
                f"{_group.attrs.get('NX_class')})."
            )
        for key, value in attributes.items():
            _group.attrs[key] = value
        return _group
    _parent_groups = list(
        str(_path).replace(os.sep, "/") for _path in Path(group_name).parents
    )[:-1][::-1]
    _default = attributes.get("default", group_name.split("/")[1:])
    for _i, _intermediate_group_key in enumerate(_parent_groups):
        if _intermediate_group_key in parent:
            continue
        _group = parent.create_group(_intermediate_group_key)
        _group.attrs["NX_class"] = "NXentry"
        _group.attrs["default"] = _default[_i]
    _group = parent.create_group(group_name)
    _group.attrs["NX_class"] = group_type
    for key, value in attributes.items():
        _group.attrs[key] = value
    return _group


def create_nxdata_entry(
    parent: h5py.File | h5py.Group,
    name: str,
    data: np.ndarray,
    **attributes: Any,
) -> h5py.Group:
    """
    Create a NXdata entry in the given parent object.

    This function also writes the necessary attributes to the group. Necessary
    attributes for the axes will be created automatically.

    Parameters
    ----------
    parent : h5py.File or h5py.Group
        The parent group or file object.
    name: str
        The name of the NXdata data entry.
    data: np.ndarray
        The dataset to be stored in the group.
    **attributes : Any
        The attributes to be set for the group.
    """
    if not isinstance(data, Dataset):
        data = Dataset(data)
    _data_group_name, _dset_name = os.path.split(name)
    _data_group = create_nx_entry_groups(
        parent,
        _data_group_name,
        signal=_dset_name,
        axes=[f"axis_{_i}" for _i in range(data.ndim)],
        title=data.data_label,
        **{f"axis_{_n}_indices": [_n] for _n in range(data.ndim)},
        **attributes,
    )
    create_nx_dataset(_data_group, _dset_name, data, units=data.data_unit)
    for _dim in range(data.ndim):
        _ax = data.axis_ranges[_dim]
        _ = create_nx_dataset(
            _data_group,
            f"axis_{_dim}",
            _ax,
            units=data.axis_units[_dim],
            long_name=data.axis_labels[_dim],
            axis=_dim,
            NX_class=_get_nx_class_for_ndarray(_ax),
        )
    return _data_group


def create_nx_dataset(
    group: h5py.Group,
    name: str,
    data: dict | np.ndarray | str | Number,
    **attributes: Any,
) -> h5py.Dataset:
    """
    Create a NXdata dataset in the given Group (which should have an `NXdata` key).

    Parameters
    ----------
    group : h5py.Group
        The group to create the dataset in.
    name : str
        The name of the dataset.
    data: dict or np.ndarray or str or Number
        The data to be stored in the dataset. This should typically be a numpy array
        or a scalar value or a string. If a dict is given, this is interpreted as
        the arguments for calling the create_dataset method.
    **attributes : Any
        The attributes to be set for the dataset.
    """
    if name in group:
        del group[name]
    if isinstance(data, dict):
        _dataset = group.create_dataset(name, **data)
    else:
        _dataset = group.create_dataset(name, data=data)
    for key, value in attributes.items():
        _dataset.attrs[key] = value
    return _dataset


def nx_dataset_config_from_param(param: Parameter) -> tuple[Any, dict[str, Any]]:
    """
    Get a dict with NXdata configuration from a Parameter.

    Parameters
    ----------
    param : Parameter
        The parameter to get the configuration from.

    Returns
    -------
    Any
        The data to be stored in the dataset.
    dict[str, Any]
        The NXdata configuration dict.
    """
    _config: dict[str, Any] = {}
    if param.unit:
        _config["units"] = param.unit
    if param.name:
        _config["long_name"] = param.name
    _config["NX_class"] = _get_nx_class_for_param(param)
    return param.value_for_export, _config


def _get_nx_class_for_param(param: Parameter) -> str:
    """
    Get the NX class for a parameter.

    Parameters
    ----------
    param : Parameter
        The parameter.

    Returns
    -------
    str
        The NX class.
    """
    if issubclass(param.dtype, Integral):
        return "NX_INT"
    if issubclass(param.dtype, Real):
        return "NX_FLOAT"
    return "NX_CHAR"


def _get_nx_class_for_ndarray(array: np.ndarray) -> str:
    """
    Get the NX class for a numpy ndarray.

    Parameters
    ----------
    array : np.ndarray
        The input array.

    Returns
    -------
    str
        The NX class.
    """
    if np.issubdtype(array.dtype, np.integer):
        return "NX_INT"
    if np.issubdtype(array.dtype, np.floating):
        return "NX_FLOAT"
    return "NX_CHAR"


def export_context_to_nxs(
    filename: str | Path, context_object: ObjectWithParameterCollection, key: str
) -> None:
    """
    Export a context object to a HDF5 file.

    This function can be used to export Context objects like Scan or
    DiffractionExperiment to HDF5 files. The function overwrites any
    existing entries in the file.

    Parameters
    ----------
    filename : str or Path
        The filename of the HDF5 file to export to.
    context_object : ObjectWithParameterCollection
        The context object to export.
    key : str
        The key where the context object will be stored in the HDF5 file.
    """
    with h5py.File(filename, "a") as file:
        create_nx_entry_groups(file, key, group_type="NXcollection")
        _group = file[key]
        for _key, _param in context_object.params.items():
            _attributes = {"NX_class": _get_nx_class_for_param(_param)}
            if len(_param.unit) > 0:
                _attributes["units"] = _param.unit
            create_nx_dataset(_group, _key, _param.value_for_export, **_attributes)
