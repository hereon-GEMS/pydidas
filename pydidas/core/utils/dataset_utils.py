# This file is part of pydidas.
#
# pydidas is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Pydidas is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Pydidas. If not, see <http://www.gnu.org/licenses/>.

"""
Module with utility functions required for the Dataset class.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = [
    "update_dataset_properties_from_kwargs",
    "dataset_property_default_val",
    "dataset_ax_default_range",
    "get_number_of_entries",
    "get_axis_item_representation",
    "convert_data_to_dict",
    "item_is_iterable_but_not_array",
]

import textwrap
import warnings
from collections.abc import Iterable
from numbers import Integral


import numpy as np

from ..exceptions import DatasetConfigException


def update_dataset_properties_from_kwargs(obj, kwargs):
    """
    Update the required properties for the Dataset from the given keyword arguments.

    Parameters
    ----------
    obj : pydidas.core.Dataset
        The new Dataset.
    kwargs : dict
        The keyword arguments to be used as input.

    Returns
    -------
    obj : pydidas.core.Dataset
        The updated Dataset.
    """
    obj._keys = {}
    obj.axis_units = kwargs.get("axis_units", dataset_ax_default_range(obj.ndim))
    obj.axis_labels = kwargs.get("axis_labels", dataset_ax_default_range(obj.ndim))
    obj.axis_ranges = kwargs.get("axis_ranges", dataset_ax_default_range(obj.ndim))
    obj.metadata = kwargs.get("metadata", {})
    obj.data_unit = kwargs.get("data_unit", "")
    obj.data_label = kwargs.get("data_label", "")
    obj.getitem_key = None
    return obj


def dataset_property_default_val(entry):
    """
    Generate default values for the properties in a Dataset.

    of None for a number of dimensions.

    Parameters
    ----------
    entry : str
        The entry to be processed. This must be a defined string to get the default
        keys for these entries.

    Returns
    -------
    Union[str, dict]
        The default entries for different properties. This is an empty string for the
        data unit, an empty dictionary for the metadata.
    """
    if entry == "metadata":
        return {}
    elif entry in ["data_unit", "data_label"]:
        return ""
    elif entry == "getitem_key":
        return None
    raise ValueError(f"No default available for '{entry}'.")


def dataset_ax_default_range(ndim):
    """
    Generate default values for the properties in a Dataset.

    of None for a number of dimensions.

    Parameters
    ----------
    ndim : int
        The number of dimensions in the Dataset.

    Returns
    -------
    dict
        The default entries: a dictionary with None entries for each dimension.
    """
    return {i: None for i in range(ndim)}


def get_number_of_entries(obj):
    """
    Get the number of entries / items of an object.

    This function works with ndarrays, numbers and Iterables.

    Parameters
    ----------
    obj : type
        The object to be analyzed.

    Raises
    ------
    TypeError
        If the type of the object is not supported.

    Returns
    -------
    int
        The number of entries in the object.
    """
    if isinstance(obj, np.ndarray):
        return obj.size
    elif isinstance(obj, Integral):
        return 1
    elif isinstance(obj, Iterable) and not isinstance(obj, str):
        return len(obj)
    raise TypeError(f"Cannot calculate the number of entries for type {type(obj)}.")


def get_axis_item_representation(key, item, use_key=True):
    """
    Get a string representation for a dictionary item of 'axis_labels',
    'axis_ranges' or 'axis_units'

    Parameters
    ----------
    key : str
        The key (i.e. reference name) for the item.
    item : object
        The item to be represented as a string.
    use_key : bool, optional
        Keyword to print the key name in front of the values. The default
        is True.

    Returns
    -------
    list
        A list with a representation for each line.
    """
    _repr = (f"{key}: " if use_key else "") + item.__repr__()
    if isinstance(item, np.ndarray):
        _repr = _repr.replace("\n      ", "")
        _lines = textwrap.wrap(
            _repr, initial_indent="", width=75, subsequent_indent=" " * 10
        )
        _i0 = _lines[0].find(",")
        for _index in range(1, len(_lines)):
            _ii = _lines[_index].find(",")
            _lines[_index] = " " * (_i0 - _ii) + _lines[_index]
    else:
        _lines = textwrap.wrap(
            _repr, initial_indent="", width=75, subsequent_indent=" " * 3
        )
    return _lines


def convert_data_to_dict(data, target_length, calling_method_name="undefined method"):
    """
    Get an ordered dictionary with the axis keys for the input data.

    This method will create a dictionary from iterable inputs and sort
    dictionary keys for dict inputs. The new keys will be 0, 1, ...,
    ndim - 1.

    Parameters
    ----------
    data : Union[dict, Iterable]
        The keys for the axis meta data.
    target_length : int
        The required number of entries. This number is needed to sanity-check that
        the input has the correct length.
    calling_method_name : str
        The name of the calling method (for exception handling)

    Raises
    ------
    DatasetConfigException
        If a dictionary is passed as data and the keys do not correspond
        to the set(0, 1, ..., ndim - 1)
    DatasetConfigException
        If a tuple or list is passed and the length of entries is not
        equal to ndim.

    Returns
    -------
    dict
        A dictionary with keys [0, 1, ..., ndim - 1] and the corresponding
        values from the input _data.
    """
    if isinstance(data, dict):
        if set(data.keys()) != set(np.arange(target_length)):
            warnings.warn(
                "The key numbers do not match the number of array dimensions. Changing "
                f"keys to defaults. (Error encountered in {calling_method_name})."
            )
            return {_dim: _val for _dim, _val in enumerate(data.values())}
        return data
    if isinstance(data, Iterable) and not isinstance(data, str):
        if len(data) != target_length:
            warnings.warn(
                "The number of given keys does not match the number of array "
                "dimensions. Resettings keys to defaults. (Error encountered in "
                f"{calling_method_name})."
            )
            return dataset_ax_default_range(target_length)
        return dict(enumerate(data))
    raise DatasetConfigException(
        f"Input {data} cannot be converted to dictionary for property"
        f" {calling_method_name}"
    )


def item_is_iterable_but_not_array(item):
    """
    Check whether an item is iterable (ignoring strings) but not an array.

    Parameters
    ----------
    item : type
        Any object

    Returns
    -------
    bool
        Flag whether the item is iterable (without being a string or ndarray)
    """
    return (
        isinstance(item, Iterable)
        and not isinstance(item, str)
        and not isinstance(item, np.ndarray)
    )
