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
    "get_hdf5_populated_dataset_keys",
    "get_hdf5_populated_dataset_keys_visititems",
    "get_hdf5_populated_dataset_keys_visititems_links",
    "get_hdf5_metadata",
    "create_hdf5_dataset",
    "convert_data_for_writing_to_hdf5_dataset",
    "read_and_decode_hdf5_dataset",
    "get_generic_dataset",
    "verify_hdf5_dset_exists_in_file",
]

from collections.abc import Iterable
from numbers import Integral, Real
from pathlib import Path
from typing import Any, Literal, Sequence

import h5py
import numpy as np

from pydidas.core.constants import HDF5_EXTENSIONS
from pydidas.core.dataset import Dataset
from pydidas.core.exceptions import FileReadError, UserConfigError
from pydidas.core.utils.file_checks import verify_file_exists_and_extension_matches
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
    passed, the function will open a h5py.File object and close it after
    traversal. If an open h5py object is passed, this object will not be
    closed on return of the function.

    Parameters
    ----------
    item : str or Path or h5py.File or h5py.Group or h5py.Dataset
        The item to be checked recursively. A str will be interpreted as
        filepath to the Hdf5 file.
    **kwargs : Any
        Any optional keyword arguments. Supported keywords are:

        min_size : int, optional
            A minimum size which datasets need to have. Any integer between
            0 and 1,000,000,000 are acceptable. The default is 0.
        min_dim : int, optional
            The minimum dimensionality of the dataset. Allowed entries are
            0 or a positive integer. The default is 2.
        max_dim : int or None, optional
            The maximum dimension of the dataset. If None, no filtering
            will be performed. The default is None.
        file_ref : h5py.File or None, optional
            A reference to the base HDF5 file. This information is used to
            detect external datasets. If not specified, this information
            will be queried from the base calling parameter <item>. The
            default is None.
        ignore_keys : list or tuple or None, optional
            Dataset keys (or snippets of key names) to be ignored. Any keys
            starting with any of the items in this list are ignored. The
            default is None.
        ignore_key_exceptions : list or tuple or None, optional
            Dataset keys (or snippets of key names) which are exceptions to the
            ignore_keys. Any item in this group is  not ignored, even if they
            start with any of the items in the ignore_keys list.
            The default is None.
        nxdata_signal_only : bool, optional
            Flag to toggle displaying only datasets in NXdata groups which
            have the 'signal' attribute set to 1. If the group does not
            have an NXdata attribute, all datasets in the group are
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
        A list with all dataset keys which correspond to the filter
        criteria.
    """
    if isinstance(item, h5py.Dataset):
        return [item.name] if _dataset_selection_valid_check(item, **kwargs) else []

    _file_to_open = isinstance(item, (str, Path))
    if _file_to_open:
        item = Path(item)
        verify_file_exists_and_extension_matches(item, HDF5_EXTENSIONS)
        item = h5py.File(item, "r")
    if not isinstance(item, (h5py.File, h5py.Group)):
        return []

    # Update kwargs with default values if not already set:
    file_ref = kwargs.get("file_ref", None) or item.file
    # Ensure file_ref is in kwargs for recursive calls
    if "file_ref" not in kwargs:
        kwargs = {**kwargs, "file_ref": file_ref}

    _datasets = []
    nxdata_signal_only = kwargs.get("nxdata_signal_only", False)
    if item.attrs.get("NX_class", "") == "NXdata" and nxdata_signal_only:
        _signal_key = item.attrs.get("signal", None)
        if _signal_key is not None and _signal_key in item:
            _datasets.append(f"{item.name}/{_signal_key}")
    else:
        item_name = item.name
        for key in item:
            _item = item[key]
            # add a check to filter external datasets.
            # if file_ref == _item.file, this is a local dataset.
            if file_ref == _item.file:
                _datasets.extend(get_hdf5_populated_dataset_keys(_item, **kwargs))
            else:
                if _dataset_selection_valid_check(_item, **kwargs):
                    # external datasets are referenced by their .name
                    # in the external datafile, not the current file.
                    _datasets.append(f"{item_name}/{key}")
                if isinstance(_item, (h5py.File, h5py.Group)):
                    raise KeyError(
                        "Detected an external link to a h5py.Group which cannot "
                        f"be followed: {item_name}/{key}."
                    )
    if _file_to_open:
        item.close()
    return _datasets


def get_hdf5_populated_dataset_keys_visititems(
    item: str | Path | h5py.File | h5py.Group | h5py.Dataset,
    **kwargs: Any,
) -> list[str]:
    """
    Get the dataset keys of all datasets that match the conditions using visititems.

    This function was written by GitHub Copilot using the Claude Haiku model.

    This function uses h5py's visititems() method for traversal as an alternative
    approach to the original recursive implementation. It crawls through the full
    tree of a HDF5 file and finds all datasets which correspond to the search
    criteria. Allowed input items are h5py Files, Groups and Datasets as well as
    strings. If a string is passed, the function will open a h5py.File object and
    close it after traversal. If an open h5py object is passed, this object will
    not be closed on return of the function.

    Note: This implementation handles external links by manually checking for
    them, as h5py.visititems() does not follow external links by default.

    Performance Note: Benchmarks show this implementation is ~38% slower than
    get_hdf5_populated_dataset_keys() for typical use cases, primarily due to
    the need for separate external link detection. The requirement to manually
    traverse for external links (since visititems() doesn't expose link types)
    results in dual traversal overhead. Use get_hdf5_populated_dataset_keys()
    for better performance. This implementation is provided as an alternative
    for specific use cases or educational purposes.

    Parameters
    ----------
    item : str or Path or h5py.File or h5py.Group or h5py.Dataset
        The item to be checked recursively. A str will be interpreted as
        filepath to the Hdf5 file.
    **kwargs : Any
        Any optional keyword arguments. Supported keywords are:

        min_size : int, optional
            A minimum size which datasets need to have. Any integer between
            0 and 1,000,000,000 are acceptable. The default is 0.
        min_dim : int, optional
            The minimum dimensionality of the dataset. Allowed entries are
            0 or a positive integer. The default is 2.
        max_dim : int or None, optional
            The maximum dimension of the dataset. If None, no filtering
            will be performed. The default is None.
        file_ref : h5py.File or None, optional
            A reference to the base HDF5 file. This information is used to
            detect external datasets. If not specified, this information
            will be queried from the base calling parameter <item>. The
            default is None.
        ignore_keys : list or tuple or None, optional
            Dataset keys (or snippets of key names) to be ignored. Any keys
            starting with any of the items in this list are ignored. The
            default is None.
        ignore_key_exceptions : list or tuple or None, optional
            Dataset keys (or snippets of key names) which are exceptions to the
            ignore_keys. Any item in this group is  not ignored, even if they
            start with any of the items in the ignore_keys list.
            The default is None.
        nxdata_signal_only : bool, optional
            Flag to toggle displaying only datasets in NXdata groups which
            have the 'signal' attribute set to 1. If the group does not
            have an NXdata attribute, all datasets in the group are
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
        A list with all dataset keys which correspond to the filter
        criteria.
    """
    if isinstance(item, h5py.Dataset):
        return [item.name] if _dataset_selection_valid_check(item, **kwargs) else []

    _file_to_open = isinstance(item, (str, Path))
    if _file_to_open:
        item = Path(item)
        verify_file_exists_and_extension_matches(item, HDF5_EXTENSIONS)
        item = h5py.File(item, "r")
    if not isinstance(item, (h5py.File, h5py.Group)):
        return []

    # Extract file_ref and other parameters once
    file_ref = kwargs.get("file_ref", None) or item.file
    nxdata_signal_only = kwargs.get("nxdata_signal_only", False)

    # Pre-process kwargs for efficiency
    if "ignore_keys" in kwargs and kwargs["ignore_keys"]:
        if "ignore_keys_tuple" not in kwargs:
            kwargs["ignore_keys_tuple"] = tuple(kwargs["ignore_keys"])

    _datasets = []
    _nxdata_groups = {}  # Track NXdata groups to handle signal attribute
    _external_links = {}  # Track external links (visititems doesn't follow them)

    # First pass: collect external links since visititems doesn't follow them
    # Note: External links never occur at root level, only within groups
    def collect_external_links(grp: h5py.Group) -> None:
        """Recursively collect external links in the hierarchy."""
        for key in grp:
            try:
                # Get the link object WITHOUT dereferencing it
                link_obj = grp.get(key, getlink=True)
                # Check if it's an external link
                if isinstance(link_obj, h5py.ExternalLink):
                    # Use grp.name (item_name in original) to construct path
                    # This will never be "/" since external links only occur in groups
                    full_path = f"{grp.name}/{key}"
                    # Store the path - don't access yet to avoid file locks
                    _external_links[full_path] = (grp, key)
                elif not isinstance(link_obj, h5py.ExternalLink):
                    # It's a local object - check if it's a group
                    obj = grp[key]
                    if isinstance(obj, h5py.Group):
                        # Recurse into subgroups
                        collect_external_links(obj)
            except (KeyError, ValueError, OSError):
                # If we can't access it, skip it
                continue

    # Collect external links starting from groups within the root
    # Don't check root level itself since external links only occur in groups
    for key in item:
        try:
            obj = item[key]
            if isinstance(obj, h5py.Group):
                collect_external_links(obj)
        except (KeyError, ValueError, OSError):
            continue

    def visitor(name: str, obj: h5py.Group | h5py.Dataset) -> None:
        """Visitor function for h5py.visititems()."""
        # Handle NXdata groups with signal attribute
        if isinstance(obj, h5py.Group):
            if obj.attrs.get("NX_class", "") == "NXdata" and nxdata_signal_only:
                _signal_key = obj.attrs.get("signal", None)
                if _signal_key is not None:
                    # Store the full path to the signal dataset
                    signal_path = f"{obj.name}/{_signal_key}"
                    _nxdata_groups[obj.name] = signal_path
            return

        # Only process datasets
        if not isinstance(obj, h5py.Dataset):
            return

        # Check if this dataset is in an NXdata group with signal-only mode
        if nxdata_signal_only and _nxdata_groups:
            # Check if any parent group is an NXdata group
            dataset_path = obj.name
            for nxdata_path, signal_path in _nxdata_groups.items():
                if dataset_path.startswith(nxdata_path + "/"):
                    # This dataset is in an NXdata group
                    if dataset_path != signal_path:
                        # Not the signal dataset, skip it
                        return
                    break

        # Local dataset - check if it passes the filter
        if _dataset_selection_valid_check(obj, **kwargs):
            _datasets.append(obj.name)

    # Use visititems to traverse the hierarchy (won't follow external links)
    item.visititems(visitor)

    # Now handle external links separately
    for link_path, (grp, key) in _external_links.items():
        try:
            # Access the external dataset
            ext_dset = grp[key]
            # Check if the external dataset is valid
            if _dataset_selection_valid_check(ext_dset, **kwargs):
                _datasets.append(link_path)
            elif isinstance(ext_dset, (h5py.File, h5py.Group)):
                raise KeyError(
                    f"Detected an external link to a h5py.Group which "
                    f"cannot be followed: {link_path}."
                )
            # Important: Close the external file to avoid file locks
            if hasattr(ext_dset, 'file') and ext_dset.file != file_ref:
                ext_dset.file.close()
        except (KeyError, ValueError, OSError):
            # If we can't access the external dataset, skip it
            continue

    if _file_to_open:
        item.close()
    return _datasets


def get_hdf5_populated_dataset_keys_visititems_links(
    item: str | Path | h5py.File | h5py.Group | h5py.Dataset,
    **kwargs: Any,
) -> list[str]:
    """
    Get the dataset keys using h5py's visititems_links() for single-pass traversal.

    This function was written by GitHub Copilot using the Claude Haiku model.

    This is the most optimized version using visititems_links() which provides
    link information directly, allowing detection of external links during
    traversal without needing a separate pass. This achieves single-pass
    performance similar to the original recursive implementation.

    This function crawls through the full tree of a HDF5 file and finds all
    datasets which correspond to the search criteria. Allowed input items are
    h5py Files, Groups and Datasets as well as strings. If a string is passed,
    the function will open a h5py.File object and close it after traversal.

    Parameters
    ----------
    item : str or Path or h5py.File or h5py.Group or h5py.Dataset
        The item to be checked recursively. A str will be interpreted as
        filepath to the Hdf5 file.
    **kwargs : Any
        Any optional keyword arguments. Supported keywords are:

        min_size : int, optional
            A minimum size which datasets need to have. The default is 0.
        min_dim : int, optional
            The minimum dimensionality of the dataset. The default is 2.
        max_dim : int or None, optional
            The maximum dimension of the dataset. The default is None.
        file_ref : h5py.File or None, optional
            A reference to the base HDF5 file. The default is None.
        ignore_keys : list or tuple or None, optional
            Dataset keys to be ignored. The default is None.
        ignore_key_exceptions : list or tuple or None, optional
            Exceptions to ignore_keys. The default is None.
        nxdata_signal_only : bool, optional
            Flag to only return NXdata signal datasets. The default is True.

    Returns
    -------
    list[str]
        A list with all dataset keys which correspond to the filter criteria.

    Note
    ----
    Performance: This implementation uses visititems_links() which provides
    link type information, enabling single-pass traversal. Benchmarks show it
    is similar in performance to the original recursive implementation while
    providing a pure visititems-based approach.
    """
    if isinstance(item, h5py.Dataset):
        return [item.name] if _dataset_selection_valid_check(item, **kwargs) else []

    _file_to_open = isinstance(item, (str, Path))
    if _file_to_open:
        item = Path(item)
        verify_file_exists_and_extension_matches(item, HDF5_EXTENSIONS)
        item = h5py.File(item, "r")
    if not isinstance(item, (h5py.File, h5py.Group)):
        return []

    file_ref = kwargs.get("file_ref", None) or item.file
    nxdata_signal_only = kwargs.get("nxdata_signal_only", False)

    _datasets = []
    _nxdata_groups = {}

    # Pre-process kwargs
    if "ignore_keys" in kwargs and kwargs["ignore_keys"]:
        if "ignore_keys_tuple" not in kwargs:
            kwargs["ignore_keys_tuple"] = tuple(kwargs["ignore_keys"])

    # First pass: identify NXdata groups (use visititems for this)
    def nxdata_visitor(name: str, obj: Any) -> None:
        """Identify NXdata groups."""
        if isinstance(obj, h5py.Group):
            if obj.attrs.get("NX_class", "") == "NXdata" and nxdata_signal_only:
                _signal_key = obj.attrs.get("signal", None)
                if _signal_key is not None:
                    signal_path = f"{obj.name}/{_signal_key}"
                    _nxdata_groups[obj.name] = signal_path

    if nxdata_signal_only:
        item.visititems(nxdata_visitor)

    def link_visitor(name: str, link: Any) -> None:
        """Visitor for visititems_links - processes both links and datasets."""
        # Skip groups - only collect datasets
        try:
            obj = item[name]

            # Skip groups
            if isinstance(obj, h5py.Group):
                return

            # Only process datasets
            if not isinstance(obj, h5py.Dataset):
                return

            # Normalize name: visititems_links reports names without leading /
            # For root-level items, this means we need to add / prefix
            # For nested items like "group_1/data", we need to add / prefix
            normalized_name = f"/{name}" if not name.startswith("/") else name

            # Check if in NXdata signal-only mode
            if nxdata_signal_only and _nxdata_groups:
                for nxdata_path, signal_path in _nxdata_groups.items():
                    if normalized_name.startswith(nxdata_path + "/"):
                        if normalized_name != signal_path:
                            return
                        break

            # Validate and add
            if _dataset_selection_valid_check(obj, **kwargs):
                _datasets.append(normalized_name)
        except (KeyError, ValueError, OSError):
            pass

    # Use visititems_links for single-pass traversal with link information
    item.visititems_links(link_visitor)

    if _file_to_open:
        item.close()
    return _datasets


def _dataset_selection_valid_check(item: Any, **kwargs: Any) -> bool:
    """
    Check if a h5py item is a valid selection based on kwargs settings.

    This function checks if an item is an instance of h5py.Dataset and if it
    fulfills the defined filtering criteria for minimum data size, minimum
    data dimensionality and filtered keys.

    Parameters
    ----------
    item : Any
        This is the object to be checked for being an instance of
        h5py.Dataset.
    **kwargs : Any
        Any optional keyword arguments. Supported keywords are:

        min_size : int, optional
            The minimum data size of the item. This is the total size of
            the dataset, not the size along any one dimension. The default
            is 0.
        min_dim : int, optional
            The minimum dimensionality of the item. The default is 2.
        max_dim : int or None, optional
            The maximum acceptable dimension of the Dataset. The default is
            None.
        ignore_keys : list or tuple, optional
            A list or tuple of strings. If the dataset key starts with any
            of the entries, the dataset is ignored. The default is an
            empty tuple.
        ignore_key_exceptions : list or tuple or None, optional
            Dataset keys (or snippets of key names) which are exceptions to the
            ignore_keys. Any item in this group is  not ignored, even if they
            start with any of the items in the ignore_keys list.
            The default is None.

    Returns
    -------
    bool
        The result of the check: Is the item a h5py.Dataset and fulfills
        the requirements of minimum data size and dimensionality and does
        not start with any keys specified in the ignore_keys?
    """
    if not isinstance(item, h5py.Dataset):
        return False
    # Check size first (cheapest check)
    min_size = kwargs.get("min_size", 0)
    if item.size < min_size:
        return False
    # Check shape/dimensionality
    min_dim = kwargs.get("min_dim", 2)
    max_dim = kwargs.get("max_dim", None)
    ndim = item.ndim
    if ndim < min_dim or (max_dim is not None and ndim > max_dim):
        return False
    # Check name filtering (potentially expensive with startswith)
    ignore_keys = kwargs.get("ignore_keys", ())
    if ignore_keys:
        ignore_key_exceptions = kwargs.get("ignore_key_exceptions", ())
        item_name = item.name
        if ignore_key_exceptions and item_name in ignore_key_exceptions:
            return True
        if "ignore_keys_tuple" not in kwargs:
            # Cache tuple conversion if not already cached
            kwargs["ignore_keys_tuple"] = tuple(ignore_keys)
        if item_name.startswith(kwargs["ignore_keys_tuple"]):
            return False

    return True


def get_hdf5_metadata(
    fname: str | Path,
    meta: Iterable[str] | Literal["dtype", "shape", "size", "ndim", "nbytes"],
    dset: str | None = None,
) -> type | tuple[int, ...] | int | dict[str, type | tuple[int, ...] | int]:
    """
    Get metadata about a HDF5 dataset.

    This function will return the requested metadata of a HDF5 dataset.
    Input can be given either with file name and dataset parameters or
    using the HDF5 nomenclature with <filename>://</dataset> (note the
    total of 3 slashes). Dataset metadata include the following: dtype,
    shape, size, ndim, nbytes.

    Parameters
    ----------
    fname : str or Path
        The filepath or path to filename and dataset.
    meta : Iterable[str] or Literal["dtype", "shape", "size", "ndim",
           "nbytes"]
        The metadata item(s). Accepted values are either an iterable
        (list, set or tuple) of the Literal entries or a single string
        of the given literal value.
    dset : str or None, optional
        The optional dataset key, if not specified in the fname. The
        default is None.

    Returns
    -------
    type or tuple[int, ...] or int or dict
        The return value. If exactly one metadata information has been
        requested, this information is returned directly. If more than
        one piece of information has been requested, a dictionary with
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
    nomenclature with <filename>://</dataset> (note the total of 3
    slashes).

    Parameters
    ----------
    entry : str or Path
        The filepath or path to filename and dataset.
    dset : str or None, optional
        The optional dataset key, if not specified in the fname. The
        default is None.

    Raises
    ------
    KeyError
        If the dataset has not been specified.
    TypeError
        If fname is not of type str or Path.

    Returns
    -------
    str
        The filename (without any possible reference to the dataset).
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
        The name of the dataset.
    group : str or None, optional
        The path to the group, relative to origin. If None, the dataset
        will be created directly in the origin. The default is None.
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
) -> Any:
    """
    Read and decode HDF5 dataset.

    This function reads the data from a HDF5 dataset and converts the data
    type, if necessary. The direct link to the dataset can be given in the
    h5object variable or the group and dataset can be specified separately.
    Note that group and dataset will only be used if both group and dataset
    are specified.

    Parameters
    ----------
    h5object : h5py.File or h5py.Group or h5py.Dataset
        The input HDF5 object. If the group and dataset are not given,
        this will be interpreted as the direct dataset link.
    group : str or None, optional
        The HDF5 group of the dataset. If None, the h5object will be read
        directly. The default is None.
    dataset : str or None, optional
        The dataset key. If not specified, the h5object will be used
        directly. The default is None.
    return_dataset : bool, optional
        Flag to toggle returning arrays as pydidas.core.Dataset. If False,
        generic np.ndarrays are returned. The default is True.

    Returns
    -------
    Any
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
    if "/entry/data/data" in datasets:
        # this is the standard NeXus path for generic data
        return "/entry/data/data"
    if "/entry/data/data_000001" in datasets:
        # this is the standard HDF5 path for Eiger data when not
        # stored in a NeXus file.
        return "/entry/data/data_000001"
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
