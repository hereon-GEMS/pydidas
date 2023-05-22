# This file is part of pydidas.
#
# Copyright 2021-, Helmholtz-Zentrum Hereon
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
__copyright__ = "Copyright 2021-, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = [
    "hdf5_dataset_check",
    "get_hdf5_populated_dataset_keys",
    "get_hdf5_metadata",
    "create_hdf5_dataset",
    "convert_data_for_writing_to_hdf5_dataset",
    "read_and_decode_hdf5_dataset",
    "is_hdf5_filename",
]

import os
import pathlib

import numpy as np
import h5py
import hdf5plugin

from ..constants import HDF5_EXTENSIONS
from ..dataset import Dataset
from .file_utils import get_extension


def get_hdf5_populated_dataset_keys(
    item, min_size=50, min_dim=3, file_ref=None, ignore_keys=None
):
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
    item : Union[str, h5py.File, h5py.Group, h5py.Dataset]
        The item to be checked recursively. A str will be interpreted as
        filepath to the Hdf5 file.
    min_size : int, optional
        A minimum size which datasets need to have. Any integer between 0
        and 1,000,000,000 are acceptable. The default is 50.
    min_dim : int, optional
        The minimum dimensionality of the dataset. Allowed entries are
        between 0 and 3. The default is 3.
    file_ref : h5py.File reference, optional
        A reference to the base hdf5 file. This information is used to
        detect external datasets. If not specified, this information will
        be queried from the base calling parameter <item>. The default is None.
    ignore_keys : Union[list, None], optional
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
    list
        A list with all dataset keys which correspond to the filter criteria.
    """
    _close_on_exit = False
    _ignore = ignore_keys if ignore_keys is not None else []
    # return in case of a dataset
    if isinstance(item, h5py.Dataset):
        if hdf5_dataset_check(item, min_size, min_dim, _ignore):
            return [item.name]
        return []

    if isinstance(item, (str, pathlib.Path)):
        _hdf5_filename_check(item)
        item = h5py.File(item, "r")
        _close_on_exit = True
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
                item[key], min_size, min_dim, file_ref, _ignore
            )
        else:
            if hdf5_dataset_check(_item, min_size, min_dim, _ignore):
                _datasets += [f"{item.name}/{key}"]
            if isinstance(_item, (h5py.File, h5py.Group)):
                raise KeyError(
                    'External link to hdf5.Group detected: "{item.name}/{key}'
                    '". Cannot follow the link. Aborting ...'
                )
    if _close_on_exit:
        item.close()
    return _datasets


def is_hdf5_filename(filename):
    """
    Check whether the given filename has an hdf5 extension.

    Parameters
    ----------
    filename : Union[pathlib.Path, str]
        The filename to check.

    Returns
    -------
    bool
        Flag whether the filename extension is a registered hdf5 extension.
    """
    return get_extension(filename) in HDF5_EXTENSIONS


def _hdf5_filename_check(item):
    """
    Check that a specified filename is okay and points to an existing file.

    Parameters
    ----------
    item : Union[str, pathlib.Path]
        The filename.

    Raises
    ------
    TypeError
        If the file extension is not a recognized Hdf5 extension.
    FileNotFoundError
        If the file does not exist.
    """
    if not get_extension(item) in HDF5_EXTENSIONS:
        raise TypeError(
            "The file does not have any extension registered for hdf5 files."
        )
    if not os.path.exists(item):
        raise FileNotFoundError(f'The specified file "{item}" does not exist.')


def hdf5_dataset_check(item, min_size=50, min_dim=3, to_ignore=()):
    """
    Check if an h5py item is a dataset which corresponds to the filter
    criteria.

    This function checks if an item is an instance of :py:class:`h5py.Dataset`
    and if it fulfills the defined filtering criteria for minimum data size,
    minimum data dimensionality and and filtered keys.

    Parameters
    ----------
    item : object
        This is the object to be checked for being an instance of
        :py:class:`h5py.Dataset`.
    min_size : int, optional
        The minimum data size of the item. This is the total size of the
        dataset, not the size along any one dimension. The default is 50.
    min_dim : int, optional
        The minimum dimensionality of the item. The default is 3.
    to_ignore : Union[list, tuple], optional
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
        return True
    return False


def _get_hdf5_file_and_dataset_names(fname, dset=None):
    """
    Get the name of the file and an hdf5 dataset.

    This function will return the file name and dataset name. Input can be
    given either with file name and dataset parameters or using the hdf5
    nomenclature with <filename>://</dataset> (note the total of 3 slashes).

    Parameters
    ----------
    fname : Union[str, pathlib.Path]
        The filepath or path to filename and dataset.
    dset : str, optional
        The optional dataset key, if not specified in the fname.
        The default is None.

    Raises
    ------
    KeyError
        If the dataset has not been specified.
    TypeError
        If fname is not of type str or pathlib.Path.

    Returns
    -------
    fname : str
        The filename (without and possible reference to the dataset).
    dset : str
        The internal path to the dataset.
    """
    fname = str(fname) if isinstance(fname, pathlib.Path) else fname
    if not isinstance(fname, str):
        raise TypeError("The path must be specified as string or pathlib.Path")
    if fname.find("://") > 0:
        fname, dset = fname.split("://")
    if dset is None:
        raise KeyError("No dataset specified. Cannot access information.")
    return fname, dset


def get_hdf5_metadata(fname, meta, dset=None):
    """
    Get metadata about an hdf5 dataset.

    This function will return the requested metadata of an hdf5 dataset.
    Input can be given either with file name and dataset parameters or using
    the hdf5 nomenclature with <filename>://</dataset> (note the total of
    3 slashes). Dataset metadata include the following: dtype, shape, size,
    ndim, nbytes

    Parameters
    ----------
    fname : Union[str, pathlib.Path]
        The filepath or path to filename and dataset.
    meta : Union[str, iterable]
        The metadata item(s). Accepted values are either an iterable (list or
        tuple) of entries or a single string of the following: "dtype",
        "shape", "size", "ndim" or "nbytes".
    dset : str, optional
        The optional dataset key, if not specified in the fname.
        The default is None.

    Returns
    -------
    meta : dict or type
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
    with h5py.File(_fname, "r") as _file:
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


def create_hdf5_dataset(origin, group, dset_name, **dset_kws):
    """
    Create an hdf5 dataset at the specified location.

    If the specified group does not exist, this function will create the
    necessary group for the dataset.

    Note that this function will replace any existing datasets.

    Parameters
    ----------
    origin : Union[h5py.File, h5py.Group]
        The original object where the data shall be appended.
    group : Union[str, None]
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


def convert_data_for_writing_to_hdf5_dataset(data):
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
    h5object, group=None, dataset=None, return_dataset=True
):
    """
    Read and decode hdf5 dataset.

    This function reads the data from a hdf5 dataset and converts the data type,
    if necessary.
    The direct link to the dataset can be given in the h5object variable or the group
    and dataset can be specificed separately. Note that group and dataset will only be
    used if both group and dataset are specified.

    Parameters
    ----------
    h5object: Union[h5py.Dataset, h5py.File]
        The input dataset. If the group and dataset are not given, this will be
        interpreted as the full access path to the dataset.
    group : Union[None, str]
        The hdf5 group of the dataset.
    dataset : h5py.Dataset
        The input dataset.
    return_dataset : bool, optional
        Flag to toggle returning arrays as pydidas.core.Dataset. If False, generic
        np.ndarrays are returned. The default is True.

    Returns
    -------
    _data : object
        The data stored in the hdf5 dataset.
    """
    if group is not None and dataset is not None:
        _data = h5object[group][dataset][()]
    else:
        _data = h5object[()]
    if isinstance(_data, bytes):
        _data = _data.decode("UTF-8")
        if _data == "::None::":
            return None
    if isinstance(_data, np.ndarray) and return_dataset:
        return Dataset(_data)
    return _data
