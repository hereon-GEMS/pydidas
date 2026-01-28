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
    "hdf5_dataset_filter_check",
    "get_hdf5_populated_dataset_keys",
    "get_hdf5_metadata",
    "create_hdf5_dataset",
    "convert_data_for_writing_to_hdf5_dataset",
    "read_and_decode_hdf5_dataset",
    "create_nx_entry_groups",
    "create_nx_dataset",
    "create_nxdata_entry",
    "get_nx_class_for_param",
    "get_generic_dataset",
    "verify_hdf5_dset_exists_in_file",
]


import os
from collections.abc import Iterable
from numbers import Integral, Number, Real
from pathlib import Path
from typing import Any, Literal, Sequence

import h5py
import numpy as np

from pydidas.core.constants import HDF5_EXTENSIONS
from pydidas.core.dataset import Dataset
from pydidas.core.exceptions import FileReadError, UserConfigError
from pydidas.core.object_with_parameter_collection import ObjectWithParameterCollection
from pydidas.core.parameter import Parameter
from pydidas.core.utils import verify_file_exists_and_extension_matches
from pydidas.core.utils.file_utils import CatchFileErrors


def get_hdf5_populated_dataset_keys(
    item: str | Path | h5py.File | h5py.Group | h5py.Dataset,
    **kwargs: Any,
) -> list[str]:
    """
    Get the dataset keys of all datasets that match the conditions.

    Function which crawls through the full tree of a HDF5 file and finds
    all datasets which correspond to the search criteria. Allowed input items
    are h5py Files, Groups and Datasets as well as strings. If a string is
    passed, the function will open a :py:class:`h5py.File` object and close
    it after traversal. If an open h5py object is passed, this object will
    not be closed on return of the function.

    Parameters
    ----------
    item : str or Path or h5py.File or h5py.Group or h5py.Dataset
        The item to be checked recursively. A str will be interpreted as
        filepath to the Hdf5 file.
    **kwargs : Any
        Any optional keyword arguments. Supported keywords are:

        min_size : int, optional
            A minimum size which datasets need to have. Any integer between 0
            and 1,000,000,000 are acceptable. The default is 0.
        min_dim : int, optional
            The minimum dimensionality of the dataset. Allowed entries are
            0 or a positive integer. The default is 2.
        max_dim : int or None, optional
            The maximum dimension of the dataset. If None, no filtering will be
            performed.
        file_ref : h5py.File or None, optional
            A reference to the base HDF5 file. This information is used to
            detect external datasets. If not specified, this information will
            be queried from the base calling parameter <item>. The default is None.
        ignore_keys : list or tuple or None, optional
            Dataset keys (or snippets of key names) to be ignored. Any keys
            starting with any of the items in this list are ignored.
            The default is None.
        nxdata_signal_only : bool, optional
            Flag to toggle displaying only datasets in NXdata groups which
            have the 'signal' attribute set to 1. If the group
            does not have an NXdata attribute, all datasets in the group are
            returned. The default is True.

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
    if isinstance(item, h5py.Dataset):
        return [item.name] if hdf5_dataset_filter_check(item, **kwargs) else []

    _file_to_open = isinstance(item, (str, Path))
    if _file_to_open:
        item = Path(item)
        verify_file_exists_and_extension_matches(item, HDF5_EXTENSIONS)
        item = h5py.File(item, "r")
    if not isinstance(item, (h5py.File, h5py.Group)):
        return []
    file_ref = kwargs.get("file_ref", None) or item.file

    _datasets = []
    if item.attrs.get("NX_class", "") == "NXdata" and kwargs.get(
        "nxdata_signal_only", True
    ):
        _signal_key = item.attrs.get("signal", None)
        if _signal_key is not None and _signal_key in item:
            _datasets.append(f"{item}/{_signal_key}")
    else:
        for key in item:
            _item = item[key]
            # add a check to filter external datasets.
            # if file_ref == _item.file, this is a local dataset.
            if file_ref == _item.file:
                _datasets += get_hdf5_populated_dataset_keys(item[key], **kwargs)
            else:
                if hdf5_dataset_filter_check(_item, **kwargs):
                    # external datasets are referenced by their .name
                    # in the external datafile, not the current file.
                    _datasets += [f"{item.name}/{key}"]
                if isinstance(_item, (h5py.File, h5py.Group)):
                    raise KeyError(
                        "Detected an external link to a h5py.Group which cannot "
                        f"be followed: {item.name}/{key}."
                    )
    if _file_to_open:
        item.close()
    return _datasets


def hdf5_dataset_filter_check(item: Any, **kwargs: Any) -> bool:
    """
    Check if a h5py item is a dataset which corresponds to the filter criteria.

    This function checks if an item is an instance of :py:class:`h5py.Dataset`
    and if it fulfills the defined filtering criteria for minimum data size,
    minimum data dimensionality and filtered keys.

    Parameters
    ----------
    item : Any
        This is the object to be checked for being an instance of
        :py:class:`h5py.Dataset`.
    **kwargs : Any
        Any optional keyword arguments. Supported keywords are:

        min_size : int, optional
            The minimum data size of the item. This is the total size of the
            dataset, not the size along any one dimension. The default is 0.
        min_dim : int, optional
            The minimum dimensionality of the item. The default is 2.
        max_dim : int or None, optional
            The maximum acceptable dimension of the Dataset.
        ignore_keys : list or tuple, optional
            A list or tuple of strings. If the dataset key starts with any
            of the entries, the dataset is ignored. The default is an
            empty tuple.

    Returns
    -------
    bool
        The result of the check: Is the item an :py:class:`h5py.Dataset`
        and fulfills the requirements of minimum data size and dimensionality
        and does not start with any keys specified in the ignore_keys?
    """
    if not isinstance(item, h5py.Dataset):
        return False
    _max_dim = kwargs.get("max_dim", None)
    return (
        item.size >= kwargs.get("min_size", 0)
        and not item.name.startswith(tuple(kwargs.get("ignore_keys", ())))
        and kwargs.get("min_dim", 2) <= len(item.shape)
        and (_max_dim is None or (len(item.shape) <= _max_dim))
    )


def get_hdf5_metadata(
    fname: str | Path,
    meta: Iterable[str] | Literal["dtype", "shape", "size", "ndim", "nbytes"],
    dset: str | None = None,
) -> type | tuple[int, ...] | int | dict[str, type | tuple[int, ...] | int]:
    """
    Get metadata about a HDF5 dataset.

    This function will return the requested metadata of a HDF5 dataset.
    Input can be given either with file name and dataset parameters or using
    the HDF5 nomenclature with <filename>://</dataset> (note the total of
    3 slashes). Dataset metadata include the following: dtype, shape, size,
    ndim, nbytes

    Parameters
    ----------
    fname : str or Path
        The filepath or path to filename and dataset.
    meta : Iterable[str] or Literal["dtype", "shape", "size", "ndim", "nbytes"]
        The metadata item(s). Accepted values are either an iterable (list,
        set or tuple) of the Literal entries or a single string of the
        given literal value.
    dset : str or None, optional
        The optional dataset key, if not specified in the fname.
        The default is None.

    Returns
    -------
    type or tuple[int, ...] or int or dict[str, type | tuple[int, ...] | int]
        The return value. If exactly one metadata information has been
        requested, this information is returned directly. If more
        than one piece of information has been requested, a dictionary with
        the information will be returned.
    """
    _fname, _dset = _split_hdf5_file_and_dataset_names(fname, dset)
    if not isinstance(meta, (str, set, list, tuple)):
        raise TypeError("meta parameter must be of type str, set, list, tuple.")
    _results = {}
    with (
        CatchFileErrors(_fname, error_suffix="as HDF5 file."),
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


def _split_hdf5_file_and_dataset_names(
    entry: Path | str, dset: str | None = None
) -> tuple[str, str]:
    """
    Get the name of the file and a HDF5 dataset.

    This function will return the file name and dataset name. Input can be
    given either with file name and dataset parameters or using the hdf5
    nomenclature with <filename>://</dataset> (note the total of 3 slashes).

    Parameters
    ----------
    entry : str or Path
        The filepath or path to filename and dataset.
    dset : str or None, optional
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
    str
        The filename (without and possible reference to the dataset).
    str
        The internal path to the dataset.
    """
    if not isinstance(entry, (str, Path)):
        raise TypeError("The path must be specified as string or Path")
    entry = str(entry)
    if entry.find("://") > 0:
        entry, dset = entry.split("://")
    if dset is None:
        raise KeyError("No dataset specified. Cannot access information.")
    return entry, dset


def create_hdf5_dataset(
    origin: h5py.File | h5py.Group,
    dset_name: str,
    group: str | None = None,
    **dset_kws: Any,
) -> None:
    """
    Create a HDF5 dataset at the specified location.

    If the specified group does not exist, this function will create the
    necessary group for the dataset.

    Note that this function will replace any existing datasets.

    Parameters
    ----------
    origin : h5py.File or h5py.Group
        The original object where the data shall be appended.
    dset_name : str
        The name of the dataset
    group : str or None, optional
        The path to the group, relative to origin. If None, the dataset will be
        created directly in the origin.
    **dset_kws : Any
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


def convert_data_for_writing_to_hdf5_dataset(data: Any | None) -> Any:
    """
    Convert specific datatypes which cannot be written directly with hdf5.

    This function converts None values to a string representation which can
    be written to HDF5 datasets. More conversions can be added as needed.

    Parameters
    ----------
    data : Any or None
        The input data.

    Returns
    -------
    data : Any
        The sanitized input data.
    """
    if data is None:
        data = "::None::"
    return data


def read_and_decode_hdf5_dataset(
    h5object: h5py.File | h5py.Group | h5py.Dataset,
    group: str | None = None,
    dataset: str | None = None,
    return_dataset: bool = True,
) -> object:
    """
    Read and decode HDF5 dataset.

    This function reads the data from a HDF5 dataset and converts the data type,
    if necessary.
    The direct link to the dataset can be given in the h5object variable or the
    group and dataset can be specified separately. Note that group and dataset
    will only be used if both group and dataset are specified.

    Parameters
    ----------
    h5object: h5py.File or h5py.Group or h5py.Dataset
        The input HDF5 object. If the group and dataset are not given,
        this will be interpreted as the direct dataset link.
    group : str or None
        The HDF5 group of the dataset. If None, the h5object will be read
        directly.
    dataset : str or None, optional
        The dataset key. If not specified, the h5object will be used directly.
    return_dataset : bool, optional
        Flag to toggle returning arrays as pydidas.core.Dataset. If False,
        generic np.ndarrays are returned. The default is True.

    Returns
    -------
    object
        The data stored in the HDF5 dataset.
    """
    if group is not None and dataset is not None:
        _data = h5object[group][dataset][()]
    else:
        if not isinstance(h5object, h5py.Dataset):
            raise UserConfigError(
                "Error in read_and_decode_hdf5_dataset: If group and dataset "
                "are not specified, h5object must be a h5py.Dataset instance."
            )
        _data = h5object[()]
    if isinstance(_data, Integral):
        return int(_data)
    if isinstance(_data, Real):
        return float(_data)
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
    create_nx_dataset(_data_group, _dset_name, data, units=data.data_unit, signal=1)
    for _dim in range(data.ndim):
        _ = create_nx_dataset(
            _data_group,
            f"axis_{_dim}",
            data.axis_ranges[_dim],
            units=data.axis_units[_dim],
            long_name=data.axis_labels[_dim],
            axis=_dim,
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


def get_nx_class_for_param(param: Parameter) -> str:
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


def export_context_to_hdf5(
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
            _attributes = {"NX_class": get_nx_class_for_param(_param)}
            if len(_param.unit) > 0:
                _attributes["units"] = _param.unit
            create_nx_dataset(_group, _key, _param.value_for_export, **_attributes)


def get_generic_dataset(datasets: Sequence[str]) -> str:
    """
    Get the best standard dataset from a list of dataset names.

    This function checks a list of dataset names and returns the one which
    corresponds best to standard naming conventions for generic datasets.

    Parameters
    ----------
    datasets : Sequence[str]
        A sequence of dataset names to check.

    Returns
    -------
    str
        The best matching generic dataset name. If no match is found,
        the first entry in the list is returned.
    """
    if len(datasets) == 0:
        raise ValueError(
            "The datasets list is empty. Cannot determine generic dataset."
        )
    if "entry/data/data" in datasets:
        # this is the standard NeXus path for generic data
        return "entry/data/data"
    if "/entry/instrument/detector/data" in datasets:
        # this is the standard NeXus path for LAMBDA detectors
        return "/entry/instrument/detector/data"
    return datasets[0]


def verify_hdf5_dset_exists_in_file(fname: Path | str, key: str) -> None:
    """
    Verify that the selected file has a dataset with the given key.

    Parameters
    ----------
    fname : Path or str
        The filename and path.
    key : str
        The dataset key.

    Raises
    ------
    UserConfigError
        If the dataset key is not found in the hdf5 file.
    """
    key = key if key.startswith("/") else f"/{key}"
    dsets = get_hdf5_populated_dataset_keys(fname, min_dim=0)
    if key not in dsets:
        raise UserConfigError(
            f"hdf5_key `{key}` is not a valid key for the file `{fname}`."
        )
