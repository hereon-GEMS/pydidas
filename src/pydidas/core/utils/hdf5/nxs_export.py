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
    "nxs_create_recursive_groups",
    "nxs_write_root_metadata",
    "nxs_update_nxroot_timestamp",
    "nxs_create_nxentry",
    "nxs_recursive_update_default_attr",
    "nxs_write_dataset",
    "nxs_write_nxdata",
    "nxs_export_context",
    "nxs_param_config_for_dset",
]

import os
from numbers import Number
from pathlib import Path
from typing import Any, Sequence

import h5py
import numpy as np

from pydidas.core.dataset import Dataset
from pydidas.core.exceptions import UserConfigError
from pydidas.core.object_with_parameter_collection import ObjectWithParameterCollection
from pydidas.core.parameter import Parameter
from pydidas.core.utils.str_utils import iso_timestring
from pydidas.version import VERSION


def _name_with_leading_slash(name: str) -> str:
    """
    Get the name with a guaranteed leading slash.

    Parameters
    ----------
    name : str
        The input name to be modified.

    Returns
    -------
    str
        The modified name with a leading slash.
    """
    return name if name.startswith("/") else f"/{name}"


def nxs_create_recursive_groups(
    parent: h5py.File | h5py.Group,
    group_name: str,
    group_type: str = "NXdata",
    **attributes: Any,
) -> h5py.Group:
    """
    Create the NXentry groups recursively and return the final group.

    Note that the final group is set to be a NXdata group unless the `group_type`
    is specified differently. If the group already exists, the function will
    only update (and replace existing) metadata.

    Parameters
    ----------
    parent: h5py.File or h5py.Group
        The parent group or file object.
    group_name : str
        The name of the group to be created.
    group_type : str
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
                f"Error when creating the group {group_name}: The group already "
                f"exists but is not of specified type {group_type} (existing group: "
                f"{_group.attrs.get('NX_class')})."
            )
        for key, value in attributes.items():
            _group.attrs[key] = value
        return _group
    _parent_groups = [_p.as_posix() for _p in Path(group_name).parents[::-1]][1:]
    if isinstance(parent, h5py.File) and _parent_groups:
        nxs_write_root_metadata(parent, default=_parent_groups[0])
    _group = parent.create_group(group_name)
    _group.attrs["NX_class"] = group_type
    for key, value in attributes.items():
        _group.attrs[key] = value
    for _intermediate_group_key in _parent_groups:
        _temp_group = parent[_intermediate_group_key]
        _nx_key = _temp_group.attrs.get("NX_class")
        if _nx_key is None:
            _temp_group.attrs["NX_class"] = "NXentry"
    return _group


def nxs_write_root_metadata(h5file: h5py.File, default: str = "entry") -> None:
    """
    Write the NxRoot metadata in the given NeXus file.

    Parameters
    ----------
    h5file : h5py.File
        The HDF5 file to create the NxRoot metadata from.
    default : str
        The default entry. The default is `entry`.
    """
    _time_string = iso_timestring()
    for _key, _val in [
        ("NX_class", "NXroot"),
        ("HDF5_version", h5py.version.hdf5_version),
        ("h5py_version", h5py.version.version),
        ("creator", "pydidas"),
        ("creator_version", VERSION),
        ("default", default),
        ("file_update_time", _time_string),
        ("file_name", h5file.filename),
    ]:
        h5file.attrs[_key] = _val
    if "file_time" not in h5file.attrs:
        h5file.attrs["file_time"] = _time_string


def nxs_update_nxroot_timestamp(h5file: h5py.File) -> None:
    """
    Update the file update time in the given NeXus file.

    Parameters
    ----------
    h5file : h5py.File
        The NeXus file to update the file update time.
    """
    h5file.attrs["file_update_time"] = iso_timestring()


def nxs_create_nxentry(h5file: h5py.File, entry: str = "entry") -> h5py.Group:
    """
    Create a basic NXentry group in the given HDF5 file.

    Parameters
    ----------
    h5file : h5py.File
        The HDF5 file to create the NXentry group in.
    entry : str
        The name of the NXentry group to be created. The default is `entry`.

    Returns
    -------
    h5py.Group
        The created NXentry group.
    """
    nxs_update_nxroot_timestamp(h5file)
    h5file.attrs["default"] = entry
    if entry not in h5file.keys():
        _entry = h5file.create_group(entry)
    else:
        _entry = h5file[entry]
    _entry.attrs["NX_class"] = "NXentry"
    _prg = nxs_write_dataset(_entry, "program_name", "pydidas")
    _prg.attrs["version"] = VERSION
    return _entry


def nxs_recursive_update_default_attr(
    root: h5py.File | h5py.Group, default: str
) -> None:
    """
    Set the default entry attribute from the given root up to the default.

    This function sets the `default` attribute on groups, starting from the root
    and descending to the final target group. Parent groups outside the root path
    are not updated.

    Parameters
    ----------
    root : h5py.File or h5py.Group
        The root group or file to set the default attribute in.
    default : str
        The default entry path to be set (e.g., "test1/test2/data").
    """
    default = _name_with_leading_slash(default)
    if isinstance(root, h5py.File):
        _parent_keys = [_p.as_posix() for _p in Path(default).parents[::-1]]
        _rel_default = _name_with_leading_slash(default)
        _defaults = _rel_default.split("/")[1:]
    else:
        _rel_default = default.removeprefix(root.name).removeprefix("/")
        _parent_keys = [_p.as_posix() for _p in Path(_rel_default).parents[::-1]]
        _defaults = _rel_default.split("/")
    if len(_defaults) != len(_parent_keys) or _rel_default not in root:
        raise UserConfigError(
            "Error in `set_recursive_nx_default`: The given default path "
            f"`{default}` is not valid for the given file or group."
        )
    for _key, _val in zip(_parent_keys, _defaults):
        root[_key].attrs["default"] = _val


def nxs_write_nxdata(
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
    _data_group = nxs_create_recursive_groups(
        parent,
        _data_group_name,
        signal=_dset_name,
        axes=[f"axis_{_i}" for _i in range(data.ndim)],
        title=data.data_label,
        **{f"axis_{_n}_indices": [_n] for _n in range(data.ndim)},
        **attributes,
    )
    nxs_write_dataset(_data_group, _dset_name, data, units=data.data_unit)
    for _dim in range(data.ndim):
        _ax = data.axis_ranges[_dim]
        _ = nxs_write_dataset(
            _data_group,
            f"axis_{_dim}",
            _ax,
            units=data.axis_units[_dim],
            long_name=data.axis_labels[_dim],
            axis=_dim,
        )
    return _data_group


def nxs_write_dataset(
    group: h5py.Group,
    name: str,
    data: dict[str, Any] | np.ndarray | str | Number | Sequence[str | Number],
    **attributes: Any,
) -> h5py.Dataset:
    """
    Create a dataset with NeXus metadata in the given Group
    (which should be a `NXdata` object).

    Parameters
    ----------
    group : h5py.Group
        The group to create the dataset in.
    name : str
        The name of the dataset.
    data: dict or np.ndarray or str or Number or Sequence[str | Number]
        The data to be stored in the dataset. This should typically be a numpy array
        or a scalar value or a string. If a dict is given, this is interpreted as
        the arguments for calling the create_dataset method.
    **attributes : Any
        The attributes to be set for the dataset.
    """
    if name in group:
        del group[name]
    if data is None:
        _dataset = group.create_dataset(name, data="::None::")
    elif isinstance(data, dict):
        _dataset = group.create_dataset(name, **data)
    else:
        _dataset = group.create_dataset(name, data=data)
    for key, value in attributes.items():
        _dataset.attrs[key] = value
    return _dataset


def nxs_param_config_for_dset(
    param: Parameter,
) -> tuple[Any, dict[str, Any]]:
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
    if param.tooltip:
        _config["description"] = param.tooltip
    return param.value_for_export, _config


def nxs_export_context(
    h5file: h5py.File, context_object: ObjectWithParameterCollection, key: str
) -> None:
    """
    Export a context object to a HDF5 file.

    This function can be used to export Context objects like Scan or
    DiffractionExperiment to HDF5 files. The function overwrites any
    existing entries in the file.

    Parameters
    ----------
    h5file : h5py.File
        The  file instance of the HDF5 file to export to.
    context_object : ObjectWithParameterCollection
        The context object to export.
    key : str
        The key where the context object will be stored in the HDF5 file.
    """
    # parents[-2] is the first parent group which is not the root, i.e. the main entry:
    _entry = Path(key).parents[-2].name.removeprefix("/")
    nxs_write_root_metadata(h5file, default=_entry)
    nxs_create_nxentry(h5file, entry=_entry)
    _group = nxs_create_recursive_groups(h5file, key, group_type="NXparameters")
    for _key, _param in context_object.params.items():
        _val, _attributes = nxs_param_config_for_dset(_param)
        nxs_write_dataset(_group, _key, _val, **_attributes)
