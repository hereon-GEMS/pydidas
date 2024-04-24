# This file is part of pydidas.
#
# Copyright 2023 - 2024, Helmholtz-Zentrum Hereon
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
Module with utility functions required for the Dataset class.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2024, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = [
    "update_dataset_properties_from_kwargs",
    "dataset_property_default_val",
    "dataset_ax_str_default",
    "dataset_ax_default_ranges",
    "get_number_of_entries",
    "get_axis_item_representation",
    "convert_data_to_dict",
    "item_is_iterable_but_not_array",
]

import textwrap
import warnings
from collections.abc import Iterable
from numbers import Integral
from typing import List, Literal, NewType, Tuple, Union

import numpy as np

from ..exceptions import PydidasConfigError


Dataset = NewType("Dataset", np.ndarray)


def update_dataset_properties_from_kwargs(obj: Dataset, kwargs: dict) -> Dataset:
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
    obj._meta = {"getitem_key": ()}
    obj.axis_units = kwargs.get("axis_units", dataset_ax_str_default(obj.ndim))
    obj.axis_labels = kwargs.get("axis_labels", dataset_ax_str_default(obj.ndim))
    obj.axis_ranges = kwargs.get("axis_ranges", dataset_ax_default_ranges(obj.shape))
    obj.metadata = kwargs.get("metadata", {})
    obj.data_unit = kwargs.get("data_unit", "")
    obj.data_label = kwargs.get("data_label", "")
    return obj


def dataset_property_default_val(entry: str) -> Union[dict, str, tuple]:
    """
    Generate default values for the properties in a Dataset.

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
    if entry in ["data_unit", "data_label"]:
        return ""
    if entry == "getitem_key":
        return tuple()
    raise ValueError(f"No default available for '{entry}'.")


def dataset_ax_str_default(ndim: int) -> dict:
    """
    Generate default values for the string-based axis properties in a Dataset.

    Parameters
    ----------

    ndim : int
        The number of dimensions in the Dataset.

    Returns
    -------
    dict
        The default entries: a dictionary with None entries for each dimension.
    """
    return {i: "" for i in range(ndim)}


def dataset_ax_default_ranges(shape: Tuple[int]) -> dict:
    """
    Generate default values for the axis ranges in a Dataset.

    Parameters
    ----------

    shape : tuple
        The shape of the Dataset.
    get_string : bool
        Keyword to return an empty string instead of "None".

    Returns
    -------
    dict
        The default entries: a dictionary with None entries for each dimension.
    """
    return {index: np.arange(length) for index, length in enumerate(shape)}


def get_number_of_entries(obj: object) -> int:
    """
    Get the number of entries / items of an object.

    This function works with ndarrays, numbers and Iterables.

    Parameters
    ----------
    obj : object
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
    if isinstance(obj, Integral):
        return 1
    if isinstance(obj, Iterable) and not isinstance(obj, str):
        return len(obj)
    raise TypeError(f"Cannot calculate the number of entries for type {type(obj)}.")


def get_axis_item_representation(
    key: Literal["axis_labels", "axis_ranges", "axis_units"],
    item: object,
    use_key: bool = True,
) -> List[str]:
    """
    Get a string representation for a dictionary item.

    Parameters
    ----------
    key : Literal['axis_labels', 'axis_ranges', 'axis_units']
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


def convert_data_to_dict(
    data: Union[dict, Iterable[float, ...]],
    target_shape: Tuple[int],
    entry_type: Literal["str", "array"] = "str",
    calling_method_name: str = "undefined method",
) -> dict:
    """
    Get an ordered dictionary with the axis keys for the input data.

    This method will create a dictionary from iterable inputs and sort
    dictionary keys for dict inputs. The new keys will be 0, 1, ...,
    ndim - 1.

    Parameters
    ----------
    data : Union[dict, Iterable[float, ...]]
        The keys for the axis meta data.
    target_shape: Tuple[int]
        The shape of the target Dataset. This number is needed to sanity-check that
        the input has the correct length.
    entry_type : str, optional
        The type of entries. Can be either 'str' or 'array'. The default is 'str'.
    calling_method_name : str
        The name of the calling method (for exception handling)

    Raises
    ------
    PydidasConfigError
        If a dictionary is passed as data and the keys do not correspond
        to the set(0, 1, ..., ndim - 1) or if a tuple or list is passed and the length
        of entries is not equal to ndim.

    Returns
    -------
    dict
        A dictionary with keys [0, 1, ..., ndim - 1] and the corresponding
        values from the input _data.
    """
    if isinstance(data, dict):
        if set(data.keys()) != set(np.arange(len(target_shape))):
            warnings.warn(
                "The key numbers do not match the number of array dimensions. Changing "
                f"keys to defaults. (Error encountered in {calling_method_name})."
            )
            return dict(enumerate(data.values()))
        return data
    if isinstance(data, Iterable) and not isinstance(data, str):
        if len(data) != len(target_shape):
            warnings.warn(
                "The number of given keys does not match the number of array "
                "dimensions. Resettings keys to defaults. (Error encountered in "
                f"{calling_method_name})."
            )
            if entry_type == "array":
                return dataset_ax_default_ranges(target_shape)
            return dataset_ax_str_default(len(target_shape))
        return dict(enumerate(data))
    raise PydidasConfigError(
        f"Input {data} cannot be converted to dictionary for property"
        f" {calling_method_name}"
    )


def item_is_iterable_but_not_array(item: object) -> bool:
    """
    Check whether an item is iterable (ignoring strings) but not an array.

    Parameters
    ----------
    item : object
        Any object.

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
