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
Module with utility functions required for the Dataset class.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = [
    "FLATTEN_DIM_DEFAULTS",
    "METADATA_KEYS",
    "get_default_property_dict",
    "dataset_default_attribute",
    "update_dataset_properties_from_kwargs",
    "get_number_of_entries",
    "get_axis_item_representation",
    "get_dict_with_string_entries",
    "get_input_as_dict",
    "replace_none_entries",
    "convert_ranges_and_check_length",
    "get_corresponding_dims",
]


import textwrap
import warnings
from collections.abc import Iterable
from numbers import Integral, Real
from typing import List, Literal, NewType, Tuple, Union

import numpy as np

from pydidas.core.exceptions import PydidasConfigError, UserConfigError


Dataset = NewType("Dataset", np.ndarray)

FLATTEN_DIM_DEFAULTS = {
    "new_dim_label": "Flattened",
    "new_dim_unit": "",
    "new_dim_range": None,
}

METADATA_KEYS = [
    "data_unit",
    "data_label",
    "metadata",
    "_get_item_key",
    "axis_units",
    "axis_labels",
    "axis_ranges",
]


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
    obj._meta = {"_get_item_key": ()}
    for _key in METADATA_KEYS:
        if _key.startswith("_"):
            continue
        setattr(obj, _key, kwargs.get(_key, dataset_default_attribute(_key, obj.shape)))
    if not set(kwargs.keys()).issubset(set(METADATA_KEYS)):
        warnings.warn("Unknown keys in the input dictionary. Please check the inputs.")
    return obj


def get_default_property_dict(shape: tuple[int], full_properties: bool = False) -> dict:
    """
    Get the default metadata property dictionary for a Dataset.

    Parameters
    ----------
    shape : tuple[int]
        The shape of the Dataset.
    full_properties : bool, optional
        Flag to get the full metadata dictionary. If False, the keys for
        `metadata` and `_get_item_key` are omitted. The default is False.

    Returns
    -------
    dict
        The default metadata dictionary.
    """
    _meta = {}
    for _key in METADATA_KEYS:
        if not full_properties and _key in ["metadata", "_get_item_key"]:
            continue
        _meta[_key] = dataset_default_attribute(_key, shape)
    return _meta


def dataset_default_attribute(key: str, shape: tuple[int]) -> Union[str, dict]:
    """
    Get the default value for a Dataset attribute.

    Parameters
    ----------
    key : str
        The key to be processed.
    shape : tuple[int]
        The shape of the Dataset.

    Returns
    -------
    Union[str, dict]
        The default value for the given key.
    """
    if key in ["data_unit", "data_label"]:
        return ""
    if key == "_get_item_key":
        return tuple()
    if key == "metadata":
        return {}
    if key in ["axis_units", "axis_labels"]:
        return {i: "" for i in range(len(shape))}
    if key == "axis_ranges":
        return _dataset_ax_default_ranges(shape)
    raise ValueError(f"No default available for `{key}`.")


def _dataset_ax_default_ranges(shape: Tuple[int]) -> dict:
    """
    Generate default values for the axis ranges in a Dataset.

    Parameters
    ----------

    shape : tuple
        The shape of the Dataset.

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


def get_dict_with_array_entries(
    entries: Union[Iterable, dict], shape: Tuple[int], name_reference: str
) -> dict:
    """
    Get a dictionary with array entries.

    Parameters
    ----------
    entries : Union[Iterable, dict]
        The entries to be processed.
    shape : Tuple[int]
        The shape of the calling Dataset.
    name_reference : str
        The reference name from the calling method for a possible error message.

    Returns
    -------
    dict
        A dictionary with array entries.
    """


def get_dict_with_string_entries(
    entries: Union[Iterable, dict], shape: Tuple[int], name_reference: str
) -> dict:
    """
    Get a dictionary with string entries.

    Parameters
    ----------
    entries : Union[Iterable, dict]
        The entries to be processed.
    shape : int
        The shape of the calling Dataset.
    name_reference : str
        The reference name from the calling method for a possible error message.

    Returns
    -------
    dict
        A dictionary with string entries.
    """
    entries = replace_none_entries(get_input_as_dict(entries, shape, name_reference))
    if not all(isinstance(_val, str) for _val in entries.values()):
        raise UserConfigError(
            f"Invalid entries for `{name_reference}`. All entries must be strings."
        )
    return entries


def get_input_as_dict(
    data: Union[dict, Iterable[float, ...]],
    target_shape: Tuple[int],
    calling_method_name: str = "axis_labels",
) -> dict:
    """
    Get an ordered dictionary with the axis keys for the input data.

    This method will create a dictionary from iterable inputs and sort
    dictionary keys for dict inputs. The new keys will be 0, 1, ...,
    ndim - 1.

    Parameters
    ----------
    data : Union[dict, Iterable[float, ...]]
        The keys for the axis metadata.
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
        If the entries is not Iterable or the length of the keys does not match the
        number of dimensions.

    Returns
    -------
    dict
        A dictionary with keys [0, 1, ..., ndim - 1] and the corresponding
        values from the input data.
    """
    target_length = len(target_shape)
    if isinstance(data, dict):
        _target_keys = set(np.arange(target_length))
        if set(data.keys()) == _target_keys:
            return data
        warnings.warn(
            "The key numbers do not match the number of array dimensions. Updating "
            "missing keys with default values. (Error encountered in "
            "`{calling_method_name}`)."
        )
        _default_data = dataset_default_attribute(calling_method_name, target_shape)
        _default_data.update({k: v for k, v in data.items() if k in _target_keys})
        return _default_data
    if isinstance(data, Iterable) and not isinstance(data, str):
        if len(data) == target_length:
            return dict(enumerate(data))
        raise PydidasConfigError(
            "The number of given keys does not match the number of array dimensions. "
            "Resetting keys to defaults. (Error encountered in "
            f"`{calling_method_name}`)."
        )
    raise PydidasConfigError(
        f"Input `{data}` cannot be converted to dictionary for property "
        f"`{calling_method_name}`."
    )


def replace_none_entries(metadict: dict) -> dict:
    """
    Replace all None-type entries in the given metadata dictionary.

    Parameters
    ----------
    metadict : dict
        The input metadata.

    Returns
    -------
    The sanitized metadata dictionary.
    """
    return {
        _key: (_val if _val is not None else "None") for _key, _val in metadict.items()
    }


def convert_ranges_and_check_length(
    ranges: dict[int, Union[np.ndarray, tuple, list]], shape: tuple[int]
) -> dict[int, np.ndarray]:
    """
    Convert ranges to ndarrays and check their length with respect to the shape.

    Verify that all given true ranges (i.e. with more than one item) are of type
    np.ndarray and that the length of all given ranges matches the data shape.

    Warning: This function modifies the input dictionary in place!

    Parameters
    ----------
    ranges : dict[int, Union[np.ndarray, tuple, list]]
        The dictionary with the loaded ranges.
    shape : tuple[int]
        The shape of the Dataset.

    Raises
    ------
    ValueError
        If the given lengths do not match the data length.

    Returns
    -------
    dict[int, np.ndarray]
        The modified ranges dictionary.
    """
    _wrong_dims = []
    for _dim, _range in ranges.items():
        if _range is None:
            ranges[_dim] = np.arange(shape[_dim])
            continue
        if isinstance(_range, list) or isinstance(_range, tuple):
            _range = np.asarray(_range)
            ranges[_dim] = _range
        if isinstance(_range, Real) and shape[_dim] == 1:
            _range = np.array([_range])
            ranges[_dim] = _range
        if not isinstance(_range, np.ndarray):
            _wrong_dims.append([_dim, 1, shape[_dim]])
            continue
        if isinstance(_range, np.ndarray) and _range.size != shape[_dim]:
            _wrong_dims.append([_dim, _range.size, shape[_dim]])
    if len(_wrong_dims) > 0:
        _error = (
            "The type and or length of the given ranges does not match the size of "
            "the data."
        )
        for _dim, _len, _ndata in _wrong_dims:
            _error += (
                f"\nDimension {_dim}: Given range length: `{_len}`; "
                f"target length: `{_ndata}`."
            )
        raise ValueError(_error)
    return ranges


def get_corresponding_dims(ref_shape: tuple[int], new_shape: tuple[int]) -> dict:
    """
    Get the corresponding dimensions for two shapes.

    Parameters
    ----------
    ref_shape : tuple[int]
        The old shape.
    new_shape : tuple[int]
        The new shape.

    Returns
    -------
    dict
        The corresponding dimensions. This dictionary will have the new dimensions
        as keys and the corresponding old dimensions as values.
    """
    _index_ref = 0
    _index_new_offset = 0
    _ref = [[_shape, _cp] for _shape, _cp in zip(ref_shape, np.cumprod(ref_shape))]
    _new = [[_shape, _cp] for _shape, _cp in zip(new_shape, np.cumprod(new_shape))]
    _current_ref = _ref.pop(0)
    _current_new = _new.pop(0)
    _key_indices = {}
    _factorized = False
    while True:
        if _current_new == _current_ref and not _factorized:
            _key_indices[_index_ref + _index_new_offset] = _index_ref
        if (len(_ref) == 0 and _current_new[1] >= _current_ref[1]) or (
            len(_new) == 0 and _current_new[1] <= _current_ref[1]
        ):
            break
        if _current_ref[1] == _current_new[1]:
            _factorized = False
            _current_ref = _ref.pop(0)
            _current_new = _new.pop(0)
            _index_ref += 1
        while _current_ref[0] == 1 and len(_ref) > 0 and _current_new[0] > 1:
            _current_ref = _ref.pop(0)
            _index_ref += 1
            _index_new_offset -= 1
        while _current_new[0] == 1 and len(_new) > 0 and _current_ref[0] > 1:
            _current_new = _new.pop(0)
            _index_new_offset += 1
        while _current_ref[1] < _current_new[1] and len(_ref) > 0:
            _factorized = True
            _current_ref = _ref.pop(0)
            _index_ref += 1
            _index_new_offset -= 1
        while _current_ref[1] > _current_new[1] and len(_new) > 0:
            _factorized = True
            _current_new = _new.pop(0)
            _index_new_offset += 1
    return _key_indices
