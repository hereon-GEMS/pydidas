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
The dataset module includes the Dataset subclasses of numpy.ndarray with additional
embedded metadata.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["Dataset"]


import warnings
from collections.abc import Iterable
from copy import deepcopy
from functools import partialmethod
from numbers import Integral
from typing import Callable, Literal, Optional, Self, Union

import numpy as np
from numpy import ndarray
from numpy.typing import ArrayLike, DTypeLike

from pydidas.core.exceptions import UserConfigError
from pydidas.core.utils.dataset_utils import (
    FLATTEN_DIM_DEFAULTS,
    METADATA_KEYS,
    convert_ranges_and_check_length,
    dataset_default_attribute,
    get_axis_item_representation,
    get_corresponding_dims,
    get_dict_with_string_entries,
    get_input_as_dict,
    get_number_of_entries,
    update_dataset_properties_from_kwargs,
)


class Dataset(ndarray):
    """
    Dataset class, a subclass of a numpy.ndarray with metadata.

    The Dataset creates a new ndarray object from the array-like input and provides a
    view of the underlying ndarray as Dataset instance. This subclass extends ndarray
    with additional metadata, accessible and modifiable through the respective
    properties:

    - axis_units : The units of the axis ranges (in str format).
    - axis_labels : The descriptive labels for all array axes (in str format).
    - axis_ranges : The data values corresponding to the respective axes indices,
      given in form of 1-d np.ndarrays, lists or tuples. All axis_ranges values
      will be internally converted to np.ndarrays. The axis_ranges keys are
      integers corresponding to the axis indices.
    - data_unit : The unit for the data values (in str format).
    - data_label : The label for the data values (in str format).

    PLEASE NOTE:

    1.  While axis metadata is preserved during operations like reshaping or
        transposing, units are not automatically converted. The operator is responsible
        for ensuring that the units are consistent.
        For example, if the data_unit is meters, Dataset**2 will still have the unit
        meters which must be updated in the calling function
    2.  Metadata is **not** preserved when operating on two datasets. The second dataset
        will be interpreted as a numpy.ndarray and the metadata will be lost.
    3.  The ndarray.base property of Datasets is never None because the Dataset class
        is a subclass of ndarray. This means that the base property will always point to
        an ndarray. However, Dataset views never share memory and each Dataset view
        will create a new memory object.

    The following numpy ufuncs are reimplemented to preserver the metadata:
    flatten, max, mean, min, repeat, reshape, shape, sort, squeeze, sum, take,
    transpose.
    For other numpy ufuncs, metadata preservation is not guaranteed.

    Parameters
    ----------
    array : ndarray
        The data array.
    **kwargs : dict
        Optional keyword arguments. Supported keywords are:

        axis_labels : Union[dict, list, tuple], optional
            The labels for the axes. The length must correspond to the array
            dimensions. The default is None.
        axis_ranges : Union[list, tuple, dict[int, Union[np.ndarray, list, tuple]]], optional
            The ranges for the axes. If a dictionary is provided, the keys must
            correspond to the axis indices, and the values must be sequences
            (e.g., np.ndarray, list , or tuple ) with lengths matching the
            dimension of the array. The length of each sequence must correspond
            to the array dimension for that axis. Empty axis_ranges (e.g. None)
            will be converted to indices. The default is None.
        axis_ranges : Union[dict[int, Sequence], list, tuple], optional
            The ranges for the axes. The length for each range must correspond
            to the array dimensions. The default is None.
        axis_units : Union[dict, list, tuple], optional
            The units for the axes. The length must correspond to the array
            dimensions. The default is None.
        metadata : Union[dict, None], optional
            A dictionary with metadata. The default is None.
        data_unit : str, optional
            The description of the data unit. The default is an empty string.
        data_label : str, optional
            The description of the data. The default is an empty string.
    """

    def __new__(cls, array: ArrayLike, **kwargs: dict) -> Self:
        """
        Create a new Dataset.

        Parameters
        ----------
        array : ndarray
            The data array.
        **kwargs : type
            Accepted keywords are axis_labels, axis_ranges, axis_units,
            metadata, data_unit. For information on the keywords please refer
            to the class docstring.

        Returns
        -------
        Dataset
            The new dataset object.
        """
        obj = np.array(array).view(cls)
        update_dataset_properties_from_kwargs(obj, kwargs)
        return obj

    def __getitem__(self, key: Union[tuple, int]):
        """
        Overwrite the generic __getitem__ method to catch the slicing keys.

        Parameters
        ----------
        key : Union[int, tuple]
            The slicing objects.

        Returns
        -------
        Dataset
            The sliced new dataset.
        """
        self._meta["_get_item_key"] = key if isinstance(key, tuple) else (key,)
        _item = ndarray.__getitem__(self, key)
        if not isinstance(_item, ndarray):
            self._meta["_get_item_key"] = ()
        return _item

    def __array_finalize__(self, obj: Self):
        """
        Finalization of numpy.ndarray object creation.

        This method will delete or append dimensions to the associated
        axis_labels/_ranges/_units attributes, depending on the object
        dimensionality.
        """
        if obj is None or self.shape == tuple():
            return
        self.__update_keys_from_object(obj)
        if hasattr(obj, "_meta"):
            obj._meta["_get_item_key"] = ()
        self._meta["_get_item_key"] = ()

    def __update_keys_from_object(self, obj: object):
        """
        Update the axis keys from the original object.

        Parameters
        ----------
        obj : Union[Dataset, object]
            The original object. This can be another Dataset, a numpy ndarray or any
            acceptable object to create a ndarray, e.g. tuple, list.
        """
        self._meta = {
            _key: getattr(obj, _key, dataset_default_attribute(_key, self.shape))
            for _key in METADATA_KEYS
        }
        for _dim, _slicer in enumerate(self._meta["_get_item_key"]):
            if (
                isinstance(_slicer, ndarray)
                and _slicer.dtype == np.bool_
                and _slicer.size == obj.size
            ):
                # in the case of a masked array, keep all axis keys.
                break
            if isinstance(_slicer, Integral):
                for _item in ["axis_labels", "axis_units", "axis_ranges"]:
                    del self._meta[_item][_dim]
            elif isinstance(_slicer, (slice, Iterable, ndarray)):
                if isinstance(_slicer, tuple):
                    _slicer = list(_slicer)
                self._meta["axis_ranges"][_dim] = self._meta["axis_ranges"][_dim][
                    _slicer
                ]
            elif _slicer is None:
                self.__insert_axis_keys(_dim)
        # finally, shift all keys to have a consistent numbering:
        for _item in ["axis_labels", "axis_units", "axis_ranges"]:
            self._meta[_item] = {
                _dim: _item
                for _dim, (_key, _item) in enumerate(sorted(self._meta[_item].items()))
            }

    def __insert_axis_keys(self, dim: int):
        """
        Insert a new axis key at the specified dimension.

        Parameters
        ----------
        dim : int
            The dimension in front of which the new key shall be inserted.
        """
        for _item in ["axis_labels", "axis_units", "axis_ranges"]:
            _dict = self._meta[_item]
            _new_entry = np.arange(self.shape[dim]) if _item == "axis_ranges" else ""
            _vals = [_dict[_key] for _key in sorted(_dict)]
            _vals.insert(dim, _new_entry)
            self._meta[_item] = {_i: _val for _i, _val in enumerate(_vals)}

    def flatten_dims(self, *args: tuple[int], **kwargs: dict):
        """
        Flatten the specified dimensions **in place** in the Dataset.

        This method will reduce the dimensionality of the Dataset by len(args).

        Warning: Flattening distributed dimensions throughout the dataset will
        destroy the data organisation and only adjacent dimensions can be
        processed.

        Parameters
        ----------
        *args : tuple[int]
            The tuple of the dimensions to be flattened. Each dimension must
            be an integer entry.
        **kwargs: dict
            Additional keyword arguments. Supported keywords are:

            new_dim_label : str, optional
                The label for the new, flattened dimension. The default is
                'Flattened'.
            new_dim_unit : str, optional
                The unit for the new, flattened dimension. The default is ''.
            new_dim_range : Union[None, ndarray, Iterable], optional
                The new range for the flattened dimension. If None, a simple The
                default is None.
        """
        if len(args) < 2:
            return
        if set(np.diff(args)) != {1}:
            raise ValueError("The dimensions to flatten must be adjacent.")
        _new = {"axis_labels": [], "axis_units": [], "axis_ranges": []}
        _new_shape = []
        for _dim in range(self.ndim):
            if _dim not in args:
                _new_shape.append(self.shape[_dim])
                for _key in ["axis_labels", "axis_units", "axis_ranges"]:
                    _new[_key].append(self._meta[_key][_dim])
            elif _dim == args[0]:
                _new_shape.append(np.prod([self.shape[_arg] for _arg in args]))
                for _key in ["axis_labels", "axis_units", "axis_ranges"]:
                    _kwarg_key = _key[:-1].replace("axis", "new_dim")
                    _new[_key].append(
                        kwargs.get(_kwarg_key, FLATTEN_DIM_DEFAULTS[_kwarg_key])
                    )
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            self.shape = _new_shape
        for _key in ["axis_labels", "axis_units", "axis_ranges"]:
            setattr(self, _key, _new[_key])

    def get_rebinned_copy(self, binning: int) -> Self:
        """
        Get a binned copy of the Dataset.

        This method will create a binned copy and copy all axis metadata.
        It will also modify the ranges, if required.

        Parameters
        ----------
        binning : int
            The binning factor.

        Returns
        -------
        Dataset
            The re-binned Dataset.
        """
        from pydidas.core.utils.rebin_ import get_cropping_slices, rebin

        if binning == 1:
            return self.copy()
        _kwargs = self.property_dict
        _kwargs.pop("axis_ranges")
        _copy = self.__new__(self.__class__, rebin(self.array, binning), **_kwargs)
        _slices = get_cropping_slices(self.shape, binning)
        for _dim, _range in self.axis_ranges.items():
            if isinstance(_range, ndarray):
                _new = _range[_slices[_dim]]
                _new = _new.reshape(_new.size // binning, binning).mean(-1)
                _copy.update_axis_range(_dim, _new)
        return _copy

    # ##########
    # Properties
    # ##########

    @property
    def T(self) -> Self:
        """
        Get the transposed Dataset.

        Returns
        -------
        Dataset
            The transposed Dataset.
        """
        return self.transpose()

    @property
    def property_dict(self) -> dict:
        """
        Get a copy of the properties dictionary.

        Returns
        -------
        dict
            A dictionary with copies of all properties.
        """
        return {
            _key: deepcopy(_val)
            for _key, _val in self._meta.items()
            if not _key.startswith("_")
        }

    @property
    def data_unit(self) -> str:
        """
        Get the data unit.

        Returns
        -------
        str
            The data unit.
        """
        return self._meta["data_unit"]

    @data_unit.setter
    def data_unit(self, data_unit: str):
        """
        Set the data unit.

        Parameters
        ----------
        data_unit : str
            The new data_unit.

        Raises
        ------
        ValueError
            If data_unit is not str
        """
        if not isinstance(data_unit, str):
            raise TypeError("Data unit must be a string.")
        self._meta["data_unit"] = data_unit

    @property
    def data_label(self) -> str:
        """
        Get the data label.

        Returns
        -------
        str
            The data label.
        """
        return self._meta["data_label"]

    @data_label.setter
    def data_label(self, data_label: str):
        """
        Set the data label.

        Parameters
        ----------
        data_label: str
            The new data label.

        Raises
        ------
        ValueError
            If data_label is not str
        """
        if not isinstance(data_label, str):
            raise TypeError("Data label must be a string.")
        self._meta["data_label"] = data_label

    @property
    def metadata(self) -> dict:
        """
        Get the dataset metadata.

        Returns
        -------
        dict
            The metadata dictionary. There is no enforced structure of the
            dictionary.
        """
        return self._meta["metadata"].copy()

    @metadata.setter
    def metadata(self, metadata: Union[dict, None]):
        """
        Set the Dataset metadata.

        Parameters
        ----------
        metadata : Union[dict, None]
            The Dataset metadata.

        Raises
        ------
        ValueError
            If metadata is not None or dict
        """
        if not (isinstance(metadata, dict) or metadata is None):
            raise TypeError("Metadata must be a dictionary or None.")
        self._meta["metadata"] = metadata

    @property
    def array(self) -> ndarray:
        """
        Get the raw array data of the dataset.

        Returns
        -------
        ndarray
            The array data.
        """
        return self.view(ndarray)

    @property
    def _get_item_key(self) -> tuple:
        """
        Return the getitem key.

        Note

        Returns
        -------
        tuple
            The getitem key.
        """
        return deepcopy(self._meta["_get_item_key"])

    @property
    def axis_units(self) -> dict:
        """
        Get the axis units.

        Returns
        -------
        dict
            The axis units: A dictionary with keys corresponding to the
            dimension in the array and respective values.
        """
        self.__check_property_length("axis_units")
        return self._meta["axis_units"].copy()

    @axis_units.setter
    def axis_units(self, units: Union[Iterable, dict]):
        """
        Set the axis_units metadata.

        Parameters
        ----------
        units : Union[Iterable, dict]
            The new axis units. Both Iterables (of length ndim) as well as
            dictionaries (with keys [0, 1, ..., ndim -1]) are accepted.
        """
        self._meta["axis_units"] = get_dict_with_string_entries(
            units, self.shape, "axis_units"
        )

    @property
    def axis_labels(self) -> dict:
        """
        Get the axis_labels.

        Returns
        -------
        dict
            The axis labels: A dictionary with keys corresponding to the
            dimension in the array and respective values.
        """
        self.__check_property_length("axis_labels")
        return self._meta["axis_labels"].copy()

    @axis_labels.setter
    def axis_labels(self, labels: Union[Iterable, dict]):
        """
        Set the axis_labels metadata.

        Parameters
        ----------
        labels : Union[Iterable, dict]
            The new axis labels. Both Iterables (of length ndim) as well as
            dictionaries (with keys [0, 1, ..., ndim -1]) are accepted.
        """
        self._meta["axis_labels"] = get_dict_with_string_entries(
            labels, self.shape, "axis_labels"
        )

    @property
    def axis_ranges(self) -> dict:
        """
        Get the axis ranges.

        These arrays for every dimension give the range of the data
        (in conjunction with the units).

        Returns
        -------
        dict
            The axis ranges: A dictionary with keys corresponding to the
            dimension in the array and respective values.
        """
        self.__check_property_length("axis_ranges")
        return self._meta["axis_ranges"].copy()

    @axis_ranges.setter
    def axis_ranges(
        self, ranges: Union[list, tuple, dict[int, Union[ndarray, list, tuple]]]
    ):
        """
        Set the axis_ranges metadata.

        If a tuple or list is provided, the entries will be interpreted as sorted
        for all dimensions, starting with dimension 0 and counting up.

        If a dictionary is provided, the keys must be integer entries and
        correspond to the axis indices.

        Parameters
        ----------
        ranges : Union[Iterable, dict]
            The new axis ranges. Both Iterables (of length ndim) as well as
            dictionaries (with keys [0, 1, ..., ndim -1]) are accepted.
        """
        _ranges = get_input_as_dict(ranges, self.shape, "axis_ranges")
        self._meta["axis_ranges"] = convert_ranges_and_check_length(_ranges, self.shape)

    def __check_property_length(self, key: str):
        """
        Check the length of the axis properties.

        Parameters
        ----------
        key : str
            The name of the property to be checked.
        """
        if len(self._meta[key]) != self.ndim:
            warnings.warn(
                f"The number of {key.replace('_', ' ')} entries "
                f"does not match the number of dimensions of the Dataset. "
                f"Resetting the {key}."
            )
            self._meta[key] = {
                i: (np.arange(_length) if key == "axis_ranges" else "invalid")
                for i, _length in enumerate(self.shape)
            }

    # ######################################
    # Update methods for the axis properties
    # ######################################

    def update_axis_range(self, index: int, item: Union[ndarray, Iterable]):
        """
        Update a single axis range value.

        Parameters
        ----------
        index : int
            The dimension to be updated.
        item : Union[ndarray, Iterable]
            The new item for the range of the selected dimension.

        Raises
        ------
        ValueError
            If the index is not in range of the Dataset dimensions.
        """
        if not 0 <= index < self.ndim:
            raise ValueError(f"The index '{index}' is out of bounds (0..{self.ndim}).")
        _new = convert_ranges_and_check_length({index: item}, self.shape)
        self._meta["axis_ranges"][index] = _new[index]

    def update_axis_label(self, index: int, item: str):
        """
        Update a single axis label value.

        Parameters
        ----------
        index : int
            The dimension to be updated.
        item : str
            The new item for the range of the selected dimension.

        Raises
        ------
        ValueError
            If the index is not in range of the Dataset dimensions or if the item is
            not a string.
        """
        if not 0 <= index < self.ndim:
            raise ValueError(f"The index *{index}* is out of bounds (0..{self.ndim}).")
        if not isinstance(item, str):
            raise ValueError(
                f"The item `{item}` is not a string. Cannot update the axis label."
            )
        self._meta["axis_labels"][index] = item

    def update_axis_unit(self, index: int, item: str):
        """
        Update a single axis unit value.

        Parameters
        ----------
        index : int
            The dimension to be updated.
        item : str
            The new item for the range of the selected dimension.

        Raises
        ------
        ValueError
            If the index is not in range of the Dataset dimensions or if the item is
            not a string.
        """
        if not 0 <= index < self.ndim:
            raise ValueError(f"The index '{index}' is out of bounds (0..{self.ndim}).")
        if not isinstance(item, str):
            raise ValueError(
                f"The item *{item}* is not a string. Cannot update the axis label."
            )
        self._meta["axis_units"][index] = item

    # ################################
    # Metadata and description methods
    # ################################

    def get_axis_description(self, index: int) -> str:
        """
        Get the description for the given axis, based on the axis label and unit.

        Parameters
        ----------
        index : int
            The axis index.

        Returns
        -------
        str
            The description for the given axis.
        """
        return self._meta["axis_labels"][index] + (
            " / " + self._meta["axis_units"][index]
            if len(self._meta["axis_units"][index]) > 0
            else ""
        )

    def get_axis_range(self, index: int) -> ndarray:
        """
        Get a copy of the range for the specified axis.

        Parameters
        ----------
        index : int
            The axis index.

        Returns
        -------
        ndarray
            The range of the axis.
        """
        return self._meta["axis_ranges"][index].copy()

    def is_axis_nonlinear(self, index: int, threshold: float = 1e-4) -> bool:
        """
        Check if the axis range is nonlinear.

        Parameters
        ----------
        index : int
            The axis index.
        threshold : float, optional
            The threshold for the standard deviation of the range differences. The
            default is 1e-4.

        Returns
        -------
        bool
            True if the axis range is nonlinear, False otherwise.
        """
        _range = self._meta["axis_ranges"][index]
        _range_diff = np.diff(_range[np.isfinite(_range)])
        return abs(_range_diff.std() / _range_diff.mean()) > threshold

    @property
    def data_description(self) -> str:
        """
        Get a descriptive string for the data.

        Returns
        -------
        str
            The descriptive string for the data.
        """
        return self.data_label + (
            " / " + self.data_unit if len(self.data_unit) > 0 else ""
        )

    def get_description_of_point(self, indices: Iterable) -> str:
        """
        Get the metadata description of a single point in the array.

        Index values of "None" will be interpreted as request to skip this axis.

        Parameters
        ----------
        indices : Iterable
            The indices for each dimension.

        Returns
        -------
        str
            A string description of the selected point.
        """
        _str = ""
        if len(indices) != self.ndim:
            raise ValueError("Wrong number of indices for Dataset dimensions.")
        for _dim, _index in enumerate(indices):
            if _index is None:
                continue
            _label = self._meta["axis_labels"][_dim]
            _value = self._meta["axis_ranges"][_dim][_index]
            _unit = self._meta["axis_units"][_dim]
            _s = f"{_label}: {_value:.4f} {_unit}"
            _str = _str + "; " + _s if len(_str) > 0 else _s
        return _str

    # ###########################################
    # Reimplementation of generic ndarray methods
    # ###########################################

    def transpose(self, *axes: tuple[int]) -> Self:
        """
        Overload the generic transpose method to transpose the metadata as well.

        Note that contrary to the generic method, transpose creates a deepcopy of the
        data and not only a view to prevent inconsistent metadata.

        Parameters
        ----------
        *axes : tuple
            The axes to be transposed. If not given, the generic order is used.

        Returns
        -------
        pydidas.core.Dataset
            The transposed Dataset.
        """
        if axes is tuple():
            axes = tuple(np.arange(self.ndim)[::-1])
        _new = ndarray.transpose(deepcopy(self), axes)
        _new.axis_labels = [self.axis_labels[_index] for _index in axes]
        _new.axis_units = [self.axis_units[_index] for _index in axes]
        _new.axis_ranges = [self.axis_ranges[_index] for _index in axes]
        return _new

    def flatten(self, order: Literal["C", "F", "A", "K"] = "C") -> Self:
        """
        Clear the metadata when flattening the array.

        Parameters
        ----------
        order : {'C', 'F', 'A', 'K'}, optional
            'C' means to flatten in row-major (C-style) order.
            'F' means to flatten in column-major (Fortran-style) order.
            'A' means to flatten in column-major order if `a` is Fortran
            *contiguous* in memory, row-major order otherwise.
            'K' means to flatten `a` in the order the elements occur in memory.
            The default is 'C'.
        """
        _new = ndarray.flatten(self, order)
        _new._update_keys_in_flattened_array()
        return _new

    def reshape(self, *new_shape: Union[int, tuple[int]], order="C"):
        """
        Overload the generic reshape method to update the metadata.

        Parameters
        ----------
        new_shape : Union[int, tuple[int]]
            The new shape of the array.
        order : {'C', 'F', 'A', 'K'}, optional
            The order of the reshaping. The default is 'C'.

        Returns
        -------
        pydidas.core.Dataset
            The reshaped Dataset.
        """
        if len(new_shape) == 1:
            if isinstance(new_shape[0], list):
                new_shape = tuple(new_shape[0])
            elif isinstance(new_shape[0], tuple):
                new_shape = new_shape[0]
        _new = ndarray.reshape(self, new_shape, order=order)
        _dim_matches = (
            {} if self.shape == () else get_corresponding_dims(self.shape, _new.shape)
        )

        for _key in ["axis_labels", "axis_units"]:
            _values = [
                self._meta[_key][_dim_matches[_dim]] if _dim in _dim_matches else ""
                for _dim in range(_new.ndim)
            ]
            setattr(_new, _key, _values)
        _new.axis_ranges = [
            (
                self._meta["axis_ranges"][_dim_matches[_dim]]
                if _dim in _dim_matches
                else np.arange(_len)
            )
            for _dim, _len in enumerate(_new.shape)
        ]
        return _new

    def repeat(self, repeats, axis: Optional[int] = None) -> Self:
        """
        Overload the generic repeat method to update the metadata.

        Parameters
        ----------
        repeats : int
            The number of repetitions.
        axis : int, optional
            The axis along which to repeat. If None, the flattened array is returned.
            The default is None.

        Returns
        -------
        Dataset
            The repeated array.
        """
        _new = ndarray.repeat(self, repeats, axis)
        if axis is None:
            _new._update_keys_in_flattened_array()
        else:
            _new._meta["axis_ranges"][axis] = np.repeat(self.axis_ranges[axis], repeats)
        return _new

    @property
    def shape(self) -> tuple:
        """
        Get the shape of the array.

        Returns
        -------
        tuple
            The shape of the array.
        """
        return ndarray.shape.__get__(self)

    @shape.setter
    def shape(self, shape: tuple[int]):
        """
        Set the shape of the array.

        Parameters
        ----------
        shape : tuple[int]
            The new shape of the array.
        """
        _reshaped = self.reshape(shape)
        ndarray.shape.__set__(self, shape)
        self._meta = _reshaped._meta

    def _update_keys_in_flattened_array(self):
        """
        Update the keys in flattened arrays i.e. if the new dimension is one.

        Note that the metadata keys are updated in place.
        """
        if self.ndim == 1 and (
            len(self._meta["axis_ranges"]) > 1
            or len(self._meta["axis_units"]) > 1
            or len(self._meta["axis_labels"]) > 1
        ):
            self._meta["axis_labels"] = {0: "Flattened"}
            self._meta["axis_ranges"] = {0: np.arange(self.size)}
            self._meta["axis_units"] = {0: ""}

    def squeeze(self, axis: Union[None, int] = None) -> Self:
        """
        Squeeze the array and remove dimensions of length one.

        Parameters
        ----------
        axis : Union[None, int], optional
            The axis to be squeezed. If None, all axes of length one will be
            squeezed. The default is None.

        Returns
        -------
        Dataset
            The squeezed Dataset.
        """
        if axis is None:
            _axes = [_index for _index, _shape in enumerate(self.shape) if _shape != 1]
        else:
            _axes = [_index for _index, _ in enumerate(self.shape) if _index != axis]
        if self.size == 1:
            _new = Dataset(
                np.array(self).reshape(1),
                metadata=self.metadata,
                data_unit=self.data_unit,
                data_label=self.data_label,
            )
        else:
            _new = ndarray.squeeze(self, axis)
            for _key in ["axis_labels", "axis_ranges", "axis_units"]:
                _entry = [_v for _k, _v in getattr(self, _key).items() if _k in _axes]
                setattr(_new, _key, _entry)
        return _new

    def take(
        self,
        indices: Union[int, ArrayLike],
        axis: Optional[int] = None,
        out: Optional[ndarray] = None,
        mode: Literal["raise", "wrap", "clip"] = "raise",
    ) -> Self:
        """
        Take elements from an array along an axis.

        This method overloads the ndarray.take method to process the axis properties
        as well.

        Parameters
        ----------
        indices : Union[int, ArrayLike]
            The indices of the values to extract.
        axis : int, optional
            The axis to take the data from. If None, data will be taken from the
            flattened array. The default is None.
        out : ndarray, optional
            An optional output array. If None, a new array is created. The default is
            None.
        mode : str, optional
            Specifies how out-of-bounds indices will behave. The default is "raise".

        Returns
        -------
        Dataset
            The new dataset.
        """
        _new = ndarray.take(self, indices, axis, out, mode)
        if not isinstance(_new, Dataset) or axis is None:
            return _new
        _nindices = get_number_of_entries(indices)
        if _nindices == 1 and not isinstance(indices, Iterable):
            for _key in ["axis_labels", "axis_units", "axis_ranges"]:
                _item = _new._meta[_key]
                _item.pop(axis)
                setattr(_new, _key, _item.values())
        else:
            if isinstance(_new._meta["axis_ranges"][axis], ndarray):
                _new._meta["axis_ranges"][axis] = np.take(
                    self.axis_ranges[axis], indices
                )
        return _new

    def __reimplement_numpy_method(
        self,
        numpy_method: Callable,
        has_dtype_arg: bool = True,
        axis: Optional[Union[int, tuple[int]]] = None,
        dtype: DTypeLike = None,
        out: Optional[ArrayLike] = None,
        **kwargs: dict,
    ) -> Self:
        """
        Reimplement a NumPy method with additional metadata handling.

        Note that if `out` is an instance of ndarray (and not Dataset), only the raw
        values without metadata will be returned.

        Parameters
        ----------
        axis : Union[int, tuple[int], None], optional
            Axis or axes along which the means are computed. None corresponds to the
            mean over the full array. The default is None.
        dtype : DTypeLike, optional
            The type of the returned array and of the accumulator in which the elements
            are summed. The default is None.
        out : ndarray, optional
            Alternative output array in which to place the result. It must have the
            same shape as the expected output but the type will be cast if necessary.
            The default is None.
        **kwargs : dict
            Additional keyword arguments which are only passed when specified.
            Supported keywords are:

            keepdims : bool, optional
                If this is set to True, the axes which are reduced are left in the
                result as dimensions with size one. With this option, the result will
                broadcast correctly against the original array. The default is False.
            where : array_like, optional
                This condition is broadcast over the input. At locations where the
                condition is True, the out array will be set to the ufunc result.
                Elsewhere, the out array will retain its original value. Note that
                if an uninitialized out array is created via the default out=None,
                locations within it where the condition is False will remain
                uninitialized. The default is None.

        Returns
        -------
        Union[Dataset, ndarray]
            The result of applying the NumPy method to the array. This method will
            always return a Dataset with the singular exception of using the `out`
            argument with an ndarray instance.
            If using the `out` argument, the out object reference will be returned.
        """
        if axis is not None:
            axis = tuple(
                np.mod(_ax, self.ndim)
                for _ax in ((axis,) if isinstance(axis, int) else axis)
            )
        if has_dtype_arg:
            kwargs["dtype"] = dtype
        _result = numpy_method(self, axis=axis, out=out, **kwargs)
        if axis is None or (not isinstance(_result, ndarray)):
            return _result
        if out is not None and not isinstance(out, Dataset):
            return _result
        _result.data_label = (
            f"{numpy_method.__name__.capitalize()} of " + self.data_label
        )
        _result.data_unit = self.data_unit
        if not kwargs.get("keepdims", False):
            axis = (axis,) if isinstance(axis, int) else axis
            for _key in ["axis_labels", "axis_units", "axis_ranges"]:
                _items = [
                    _val for _i, _val in self._meta[_key].items() if _i not in axis
                ]
                setattr(_result, _key, _items)
        return _result

    mean = partialmethod(__reimplement_numpy_method, ndarray.mean)
    sum = partialmethod(__reimplement_numpy_method, ndarray.sum)
    max = partialmethod(__reimplement_numpy_method, ndarray.max, has_dtype_arg=False)
    min = partialmethod(__reimplement_numpy_method, ndarray.min, has_dtype_arg=False)

    def sort(
        self,
        axis: Optional[int] = -1,
        kind: Optional[str] = None,
        order: Optional[Union[str, list[str]]] = None,
        stable: Optional[bool] = None,
    ) -> None:
        """
        Sort the Dataset in place.

        Parameters
        ----------
        axis : int, optional
            The axis to sort the array. The default is -1.
        kind : str, optional
            Please see the numpy.sort documentation for more information on the
            `kind` parameter.
        order : Union[str, list[str]], optional
            Please see the numpy.sort documentation for more information on the
            `order` parameter.
        stable : bool, optional
            Please see the numpy.sort documentation for more information on the
            `stable` parameter.
        """
        if axis is not None and self.ndim > 1:
            raise UserConfigError(
                "Sorting a non-flattened Dataset with more than one dimension is not "
                "allowed because it would destroy the metadata. "
                "\nPlease either flatten the array or specifically sort the ndarray "
                "representation available as Dataset.array. Note that the latter will "
                "remove any Dataset metadata and the resulting class will be ndarray."
            )
        if axis is None:
            if self.ndim > 1:
                self.shape = (-1,)
            axis = 0
            _new_ax = None
        else:
            axis = np.mod(axis, self.ndim)
            _new_indices = np.argsort(self, axis=axis, kind=kind, order=order)
            _new_ax = self._meta["axis_ranges"][axis][_new_indices]
        ndarray.sort(self, axis=axis, kind=kind, order=order, stable=stable)
        if _new_ax is not None:
            self._meta["axis_ranges"][axis] = _new_ax

    def argsort(
        self,
        axis: Optional[int] = -1,
        kind: Optional[str] = None,
        order: Optional[Union[str, list[str]]] = None,
        stable: Optional[bool] = None,
    ) -> ndarray:
        """
        Get the indices which would sort the Dataset.

        Parameters
        ----------
        axis : int, optional
            The axis to sort the array. The default is -1.
        kind : str, optional
            Please see the numpy.argsort documentation for more information on the
            `kind` parameter.
        order : Union[str, list[str]], optional
            Please see the numpy.argsort documentation for more information on the
            `order` parameter.
        stable : bool, optional
            Please see the numpy.argsort documentation for more information on the
            `stable` parameter.
        """
        return ndarray.argsort(
            self, axis=axis, kind=kind, order=order, stable=stable
        ).array

    def copy(self, order: Literal["C", "F", "A", "K"] = "C") -> Self:
        """
        Overload the generic nd.ndarray copy method to copy metadata as well.

        Parameters
        ----------
        order : Literal["C", "F", "A", "K"], optional
            The memory layout. The default is "C".

        Returns
        -------
        Dataset
            The copied dataset.
        """
        _new = ndarray.copy(self, order)
        _new._meta = {
            _key: self._meta[_key].copy()
            for _key in ["axis_labels", "axis_units", "axis_ranges"]
        } | {
            _key: self._meta[_key]
            for _key in ["data_unit", "data_label", "_get_item_key"]
        }
        _new._meta["metadata"] = {}
        for _key, _val in self._meta["metadata"].items():
            try:
                _new._meta["metadata"][_key] = _val.copy()
            except AttributeError:
                _new._meta["metadata"][_key] = _val
        return _new

    def __repr__(self) -> str:
        """
        Reimplementation of the numpy.ndarray.__repr__ method.

        Returns
        -------
        str
            The representation of the Dataset class.
        """
        _print_options = np.get_printoptions()
        _edgeitems = 2 if self.ndim > 1 else 3
        np.set_printoptions(threshold=20, edgeitems=_edgeitems, precision=6)
        _meta_repr = "\n".join(
            get_axis_item_representation("metadata", self._meta["metadata"])
        )
        _info = {
            "axis_labels": self.__get_axis_item_repr("axis_labels"),
            "axis_ranges": self.__get_axis_item_repr("axis_ranges"),
            "axis_units": self.__get_axis_item_repr("axis_units"),
            "metadata": _meta_repr,
            "data_unit": "data_unit: " + self.data_unit,
            "data_label": "data_label: " + self.data_label,
            "array": self.view(ndarray).__repr__(),
        }
        _repr = (
            self.__class__.__name__
            + "(\n"
            + ",\n".join(_str for _str in _info.values())
            + "\n)"
        )
        np.set_printoptions(**_print_options)
        return _repr

    def __get_axis_item_repr(
        self, obj_name: Literal["axis_labels", "axis_ranges", "axis_units"]
    ) -> str:
        """
        Get a string representation for a metadata entry.

        Supported entries are 'axis_labels', 'axis_ranges', and 'axis_units'.

        Parameters
        ----------
        obj_name : Literal["axis_labels", "axis_ranges", "axis_units"]
            The name of the dictionary to be represented as a string.

        Returns
        -------
        str
            The representation.
        """
        _obj = getattr(self, obj_name)
        _str_entries = []
        for _key, _item in _obj.items():
            _lines = get_axis_item_representation(_key, _item)
            _str_entries.extend([" " * 4 + _line for _line in _lines])
        _str = f"{obj_name}:" + " {\n" + "\n".join(_str_entries) + "}"
        return _str

    def __str__(self) -> str:
        """
        Reimplementation of the numpy.ndarray.__str__ method.

        Returns
        -------
        str
            The Dataset.__repr__ string.
        """
        return self.__repr__()

    def __reduce__(self) -> tuple:
        """
        Reimplementation of the numpy.ndarray.__reduce__ method to add
        the Dataset metadata to the pickled version.

        This method will add the cls.__dict__ items to the generic
        numpy.ndarray__reduce__ results to pass and store the Dataset axis
        items and metadata.

        Returns
        -------
        tuple
            The arguments required for pickling. Please refer to
            https://docs.python.org/3/library/pickle.html#object.__reduce__
            for the full documentation. The class' state is appended with
            the class' __dict__
        """
        _ndarray_reduced = ndarray.__reduce__(self)
        _dataset_state = _ndarray_reduced[2] + (self.__dict__,)
        return _ndarray_reduced[0], _ndarray_reduced[1], _dataset_state

    def __setstate__(self, state: tuple):
        """
        Reimplementation of the numpy.ndarray.__setstate__.

        This method is called after pickling to restore the object. The
        Dataset's __setstate__ method adds the restoration of the __dict__
        to the generic numpy.ndarray.__setstate__.

        Parameters
        ----------
        state : tuple
            The pickled object state.
        """
        self.__dict__ = state[-1]
        ndarray.__setstate__(self, state[0:-1])

    def __array_wrap__(
        self, obj: ndarray, context: Optional[object] = None, return_scalar=False
    ) -> Self:
        """
        Return 0-d results from ufuncs as single values.

        This method overloads the generic __array_wrap__ to return values and not
        0-d results for Dataset arrays.

        Parameters
        ----------
        obj : Union[ndarray, pydidas.core.Dataset]
            The output array from the ufunc call.
        context : Union[None, object], optional
            The calling context. The default is None.

        Returns
        -------
        Union[pydidas.core.Dataset, object]
            The output will be a new Dataset if the output has a dimension
            greater zero or of the basic datatype for 0-d return values.
        """
        if obj.shape == ():
            return obj[()]
        return ndarray.__array_wrap__(self, obj, context, return_scalar)

    def __hash__(self) -> int:
        """
        Generate a hash value for the dataset.

        Returns
        -------
        int
            The hash value.
        """
        _datahash = hash(self.data.tobytes())
        _metahash = hash(
            (
                id(self),
                self.axis_labels.values(),
                self.axis_units.values(),
                self.data_label,
                self.data_unit,
            )
        )
        return hash((_datahash, _metahash))
