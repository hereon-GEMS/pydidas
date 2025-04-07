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
Module with utility functions to crawl hdf5 files / groups and determine
a list of all dataset keys which fulfill certain filter criteria.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = [
    "hdf5_dataset_check",
    "get_hdf5_populated_dataset_keys",
    "get_hdf5_metadata",
    "create_hdf5_dataset",
    "convert_data_for_writing_to_hdf5_dataset",
    "read_and_decode_hdf5_dataset",
    "is_hdf5_filename",
    "create_nx_entry_groups",
    "create_nx_dataset",
    "create_nxdata_entry",
    "_create_nxdata_axis_entry",
]


import os
from collections.abc import Iterable
from numbers import Integral, Real
from pathlib import Path
from typing import Literal

import h5py
import numpy as np

from pydidas.core.constants import HDF5_EXTENSIONS
from pydidas.core.dataset import Dataset
from pydidas.core.exceptions import FileReadError
from pydidas.core.object_with_parameter_collection import ObjectWithParameterCollection
from pydidas.core.parameter import Parameter
from pydidas.core.utils.file_utils import CatchFileErrors, get_extension


def get_hdf5_populated_dataset_keys(
    item: str | Path | h5py.File | h5py.Group | h5py.Dataset,
    min_size: int = 0,
    min_dim: int = 2,
    max_dim: int | None = None,
    file_ref: h5py.File | None = None,
    ignore_keys: list | None = None,
) -> list[str]:
    """
    Get the dataset keys of all datasets that match the conditions.

    Function which crawls through the full tree of a hdf5 file and finds
    all datasets which correspond to the search criteria. Allowed input items
    are h5py Files, Groups and Datasets as well as strings. If a string is
    passed, the function will open a :py:class:`h5py.File` object and close
    it after traversal. If an open h5py object is passed, this object will
    not be closed on return of the function.

    Parameters
    ----------
    item : str | Path | h5py.File | h5py.Group | h5py.Dataset
        The item to be checked recursively. A str will be interpreted as
        filepath to the Hdf5 file.
    min_size : int, optional
        A minimum size which datasets need to have. Any integer between 0
        and 1,000,000,000 are acceptable. The default is 0.
    min_dim : int, optional
        The minimum dimensionality of the dataset. Allowed entries are
        between 0 and 3. The default is 3.
    max_dim : int | None, optional
        The maximum dimension of the dataset. If None, no filtering will be
        performed.
    file_ref : h5py.File | None, optional
        A reference to the base hdf5 file. This information is used to
        detect external datasets. If not specified, this information will
        be queried from the base calling parameter <item>. The default is None.
    ignore_keys : list | None, optional
        Dataset keys (or snippets of key names) to be ignored. Any keys
        starting with any of the items in this list are ignored.
        The default is None.

    Raises
    ------
    KeyError
        If any Groups are links to external files, a KeyError is raised
        because h5py cannot get the reference name attributes from these
        keys but returns the name keys in the external file which does not
        allow to open these datasets.

    Returns
    -------
    list[str]
        A list with all dataset keys which correspond to the filter criteria.
    """
    _close_on_exit = isinstance(item, (str, Path))
    _ignore = ignore_keys if ignore_keys is not None else []

    if isinstance(item, h5py.Dataset):
        if hdf5_dataset_check(item, min_size, min_dim, max_dim, _ignore):
            return [item.name]
        return []

    if isinstance(item, (str, Path)):
        _hdf5_filename_check(item)
        item = h5py.File(item, "r")
    if not isinstance(item, (h5py.File, h5py.Group)):
        return []
    _datasets = []
    file_ref = item.file if file_ref is None else file_ref
    for key in item:
        _item = item[key]
        # add a check to filter external datasets. These are referenced
        # by their .name in the external datafile, not the current file.
        # if file_ref == _item.file, this is a local dataset.
        if file_ref == _item.file:
            _datasets += get_hdf5_populated_dataset_keys(
                item[key], min_size, min_dim, max_dim, file_ref, _ignore
            )
        else:
            if hdf5_dataset_check(_item, min_size, min_dim, max_dim, _ignore):
                _datasets += [f"{item.name}/{key}"]
            if isinstance(_item, (h5py.File, h5py.Group)):
                raise KeyError(
                    "Detected an external link to a hdf5.Group which cannot "
                    f"be followed: {item.name}/{key}."
                )
    if _close_on_exit:
        item.close()
    return _datasets


def is_hdf5_filename(filename: Path | str) -> bool:
    """
    Check whether the given filename has a hdf5 extension.

    Parameters
    ----------
    filename : Union[Path, str]
        The filename to check.

    Returns
    -------
    bool
        Flag whether the filename extension is a registered hdf5 extension.
    """
    return get_extension(filename) in HDF5_EXTENSIONS


def _hdf5_filename_check(item: Path | str):
    """
    Check that a specified filename is okay and points to an existing file.

    Parameters
    ----------
    item : str |Path
        The filename.

    Raises
    ------
    TypeError
        If the file extension is not a recognized Hdf5 extension.
    FileNotFoundError
        If the file does not exist.
    """
    if get_extension(item) not in HDF5_EXTENSIONS:
        raise TypeError(
            "The file does not have any extension registered for hdf5 files."
        )
    if not os.path.exists(item):
        raise FileNotFoundError(f'The specified file "{item}" does not exist.')


def hdf5_dataset_check(
    item: object,
    min_size: int = 0,
    min_dim: int = 3,
    max_dim: int | None = None,
    to_ignore: list | tuple = (),
) -> bool:
    """
    Check if a h5py item is a dataset which corresponds to the filter criteria.

    This function checks if an item is an instance of :py:class:`h5py.Dataset`
    and if it fulfills the defined filtering criteria for minimum data size,
    minimum data dimensionality and filtered keys.

    Parameters
    ----------
    item : object
        This is the object to be checked for being an instance of
        :py:class:`h5py.Dataset`.
    min_size : int, optional
        The minimum data size of the item. This is the total size of the
        dataset, not the size along any one dimension. The default is 0.
    min_dim : int, optional
        The minimum dimensionality of the item. The default is 3.
    max_dim : list | None, optional
        The maximum acceptable dimension of the Dataset.
    to_ignore : list | tuple, optional
        A list or tuple of strings. If the dataset key starts with any
        of the entries, the dataset is ignored. The default is ().

    Returns
    -------
    bool
        The result of the check: Is the item an :py:class:`h5py.Dataset`
        and fulfills the requirements of minimum data size and dimensionality
        and does not start with any keys specified in the to_ignore?
    """
    if (
        isinstance(item, h5py.Dataset)
        and len(item.shape) >= min_dim
        and item.size >= min_size
        and not item.name.startswith(tuple(to_ignore))
    ):
        return max_dim is None or len(item.shape) <= max_dim
    return False


def _get_hdf5_file_and_dataset_names(
    fname: Path | str, dset: str | None = None
) -> tuple[str]:
    """
    Get the name of the file and a hdf5 dataset.

    This function will return the file name and dataset name. Input can be
    given either with file name and dataset parameters or using the hdf5
    nomenclature with <filename>://</dataset> (note the total of 3 slashes).

    Parameters
    ----------
    fname : str | Path
        The filepath or path to filename and dataset.
    dset : str | None, optional
        The optional dataset key, if not specified in the fname.
        The default is None.

    Raises
    ------
    KeyError
        If the dataset has not been specified.
    TypeError
        If fname is not of type str or Path.

    Returns
    -------
    fname : str
        The filename (without and possible reference to the dataset).
    dset : str
        The internal path to the dataset.
    """
    fname = str(fname) if isinstance(fname, Path) else fname
    if not isinstance(fname, str):
        raise TypeError("The path must be specified as string or Path")
    if fname.find("://") > 0:
        fname, dset = fname.split("://")
    if dset is None:
        raise KeyError("No dataset specified. Cannot access information.")
    return fname, dset


def get_hdf5_metadata(
    fname: str | Path,
    meta: Iterable[str] | Literal["dtype", "shape", "size", "ndim", "nbytes"],
    dset: str | None = None,
) -> dict | object:
    """
    Get metadata about a hdf5 dataset.

    This function will return the requested metadata of a hdf5 dataset.
    Input can be given either with file name and dataset parameters or using
    the hdf5 nomenclature with <filename>://</dataset> (note the total of
    3 slashes). Dataset metadata include the following: dtype, shape, size,
    ndim, nbytes

    Parameters
    ----------
    fname : str |Path
        The filepath or path to filename and dataset.
    meta : Iterable[str] | Literal["dtype", "shape", "size", "ndim", "nbytes"]
        The metadata item(s). Accepted values are either an iterable (list or
        tuple) of entries or a single string of the given literal values.
    dset : str | None, optional
        The optional dataset key, if not specified in the fname.
        The default is None.

    Returns
    -------
    meta : dict | object
        The return value. If exactly one metadata information has been
        requested, this information is returned directly. If more
        than one piece of information has been requested, a dictionary with
        the information will be returned.
    """
    _fname, _dset = _get_hdf5_file_and_dataset_names(fname, dset)
    meta = [meta] if isinstance(meta, str) else meta
    if not isinstance(meta, (set, list, tuple)):
        raise TypeError("meta parameter must be of type str, set, list, tuple.")
    _results = {}
    with (
        CatchFileErrors(fname, error_suffix="as HDF5 file."),
        h5py.File(_fname, "r") as _file,
    ):
        if _dset not in _file:
            raise FileReadError(
                f"The specified dataset `{_dset}` does not exist in the given file. "
                "Please check the file and dataset name."
            )
        if "dtype" in meta:
            _results["dtype"] = _file[_dset].dtype
        if "shape" in meta:
            _results["shape"] = _file[_dset].shape
        if "size" in meta:
            _results["size"] = _file[_dset].size
        if "ndim" in meta:
            _results["ndim"] = _file[_dset].ndim
        if "nbytes" in meta:
            _results["nbytes"] = _file[_dset].nbytes
    if len(_results) == 1:
        _results = tuple(_results.values())[0]
    return _results


def create_hdf5_dataset(
    origin: h5py.File | h5py.Group,
    group: str | None,
    dset_name: str,
    **dset_kws: dict,
):
    """
    Create a hdf5 dataset at the specified location.

    If the specified group does not exist, this function will create the
    necessary group for the dataset.

    Note that this function will replace any existing datasets.

    Parameters
    ----------
    origin : h5py.File | h5py.Group
        The original object where the data shall be appended.
    group : str | None
        The path to the group, relative to origin. If None, the dataset will be
        created directly in origin.
    dset_name : str
        The name of the dataset
    **dset_kws : dict
        Any creation keywords for the h5py.Dataset.
    """
    if group is None:
        _group = origin
    else:
        _group = origin.get(group)
        if _group is None:
            _group = origin.create_group(group)
    if dset_name in _group.keys():
        del _group[dset_name]
    if "data" in dset_kws:
        dset_kws["data"] = convert_data_for_writing_to_hdf5_dataset(dset_kws["data"])
    _group.create_dataset(dset_name, **dset_kws)


def convert_data_for_writing_to_hdf5_dataset(data: object) -> object:
    """
    Convert specific datatypes which cannot be written directly with hdf5.

    Parameters
    ----------
    data : object
        The input data.

    Returns
    -------
    data : object
        The sanitized input data.
    """
    if data is None:
        data = "::None::"
    return data


def read_and_decode_hdf5_dataset(
    h5object: h5py.File | h5py.Dataset,
    group: str | None = None,
    dataset: h5py.Dataset | None = None,
    return_dataset: bool = True,
) -> object:
    """
    Read and decode hdf5 dataset.

    This function reads the data from a hdf5 dataset and converts the data type,
    if necessary.
    The direct link to the dataset can be given in the h5object variable or the group
    and dataset can be specified separately. Note that group and dataset will only be
    used if both group and dataset are specified.

    Parameters
    ----------
    h5object: h5py.File | h5py.Dataset
        The input dataset. If the group and dataset are not given, this will be
        interpreted as the full access path to the dataset.
    group : str | None
        The hdf5 group of the dataset. If None, the h5object will be read directly.
    dataset : h5py.Dataset | None, optional
        The input dataset. If not specified, the h5object will be used directly.
    return_dataset : bool, optional
        Flag to toggle returning arrays as pydidas.core.Dataset. If False, generic
        np.ndarrays are returned. The default is True.

    Returns
    -------
    _data : object
        The data stored in the hdf5 dataset.
    """
    _data = (
        h5object[group][dataset][()]
        if group is not None and dataset is not None
        else h5object[()]
    )
    if isinstance(_data, bytes):
        _data = _data.decode("UTF-8")
        if _data == "::None::":
            return None
    if isinstance(_data, np.ndarray) and return_dataset:
        return Dataset(_data)
    return _data


def create_nx_entry_groups(
    parent: h5py.File | h5py.Group,
    group_name: str,
    group_type: str = "NXdata",
    **attributes: dict,
) -> h5py.Group:
    """
    Create the NXentry groups in the hdf5 file and return the final group.

    Note that the final group is set to be a NXdata group unless the `group_type`
    is specified differently. If the group already exists, the function will
    only update (and replace existing) metadata.

    Parameters
    ----------
    parent: h5py.File | h5py.Group
        The parent group or file object.
    group_name : str
        The name of the group to be created.
    group_type : str, optional
        The type of the last group. The default is "NXdata".
    attributes : dict
        The attributes to be set for the last group.

    Returns
    -------
    h5py.Group
        The final group object which is accessed by the given group_name.
    """
    if group_name in parent:
        _group = parent[group_name]
        if _group.attrs.get("NX_class", group_type) != group_type:
            raise ValueError(
                "Error when creating the group {group_name}: The group already exists"
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
    **attributes: dict,
) -> h5py.Group:
    """
    Create a NXdata entry in the given parent object.

    This function also writes the necessary attributes to the group. Necessary
    attributes for the axes will be created automatically.

    Parameters
    ----------
    parent : h5py.File | h5py.Group
        The parent group or file object.
    name: str
        The name of the NXdata data entry.
    data: np.ndarray
        The dataset to be stored in the group.
    **attributes : dict
        The attributes to be set for the group.
    """
    if not isinstance(data, Dataset):
        data = Dataset(data)
    _data_group_name, _dset_name = os.path.split(name)
    _data_group = create_nx_entry_groups(
        parent,
        _data_group_name,
        signal=_dset_name,
        axes=[f"axis_{_i}_repr" for _i in range(data.ndim)],
        title=data.data_label,
        **{f"axis_{_n}_repr_indices": [_n] for _n in range(data.ndim)},
        **attributes,
    )
    create_nx_dataset(
        _data_group,
        _dset_name,
        data,
        units=data.data_unit,
        long_name=data.data_description,
        NX_class="NX_NUMBER",
    )
    for _dim in range(data.ndim):
        _create_nxdata_axis_entry(
            _data_group,
            _dim,
            data.axis_labels[_dim],
            data.axis_units[_dim],
            data.axis_ranges[_dim],
        )
    return _data_group


def _create_nxdata_axis_entry(
    group: h5py.Group, dim: int, label: str, unit: str, axdata: np.ndarray
):
    """
    Create an entry for the given axis in the given group.

    Parameters
    ----------
    group : h5py.Group
        The group to create the axis entry in.
    dim : int
        The dimension of the axis.
    label : str
        The label of the axis.
    unit : str
        The unit of the axis.
    axdata : np.ndarray
        The data of the axis.

    Returns
    -------
    h5py.Dataset
        The created dataset.
    """
    _group = group.create_group(f"axis_{dim}")
    _group.create_dataset("label", data=label)
    _group.create_dataset("unit", data=unit)
    _ax = _group.create_dataset("range", data=axdata)
    _ = create_nx_dataset(
        group,
        f"axis_{dim}_repr",
        _ax,
        units=unit,
        long_name=label + (" / " + unit if len(unit) > 0 else ""),
        axis=dim,
    )


def create_nx_dataset(
    group: h5py.Group,
    name: str,
    data: dict | np.ndarray | str | Real | Integral,
    **attributes: dict,
) -> h5py.Dataset:
    """
    Create a NXdata dataset in the given Group (which should have an `NXdata` key).

    Parameters
    ----------
    group : h5py.Group
        The group to create the dataset in.
    name : str
        The name of the dataset.
    data: Union[dict, np.ndarray, str, Real, Integral]
        The data to be stored in the dataset. This should typically be a numpy array
        or a scalar value or a string. If a dict is given, this is interpreted as
        the arguments for calling the create_dataset method.
    **attributes : dict
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


def get_nx_class_for_param(param: Parameter) -> str:
    """
    Get the NX class for a parameter.

    Parameters
    ----------
    param : str
        The parameter name.

    Returns
    -------
    str
        The NX class.
    """
    if param.dtype == Integral:
        return "NX_INT"
    if param.dtype == Real:
        return "NX_FLOAT"
    return "NX_CHAR"


def export_context_to_hdf5(
    filename: str | Path, context_object: ObjectWithParameterCollection, key: str
):
    """
    Export a context object to a HDF5 file.

    This function can be used to export Context objects like Scan or
    DiffractionExperiment to HDF5 files. The function overwrites any
    existing entries in the file.

    Parameters
    ----------
    filename : str | Path
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
            _attributes = {"NX_class": get_nx_class_for_param(_param)}
            if len(_param.unit) > 0:
                _attributes["units"] = _param.unit
            create_nx_dataset(_group, _key, _param.value_for_export, **_attributes)
