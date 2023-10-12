# This file is part of pydidas.
#
# Copyright 2023, Helmholtz-Zentrum Hereon
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
__copyright__ = "Copyright 2023, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["Dataset"]


import warnings
from collections.abc import Iterable
from copy import deepcopy
from numbers import Integral
from typing import Literal, Self, Union

import numpy as np
from numpy.typing import ArrayLike

from .utils.dataset_utils import (
    convert_data_to_dict,
    dataset_ax_default_ranges,
    dataset_ax_str_default,
    dataset_property_default_val,
    get_axis_item_representation,
    get_number_of_entries,
    item_is_iterable_but_not_array,
    update_dataset_properties_from_kwargs,
)


class Dataset(np.ndarray):
    """
    Dataset class, a subclass of a numpy.ndarray with metadata.

    Parameters
    ----------
    array : np.ndarray
        The data array.
    **kwargs : dict
        Optional keyword arguments.
    **axis_labels : Union[dict, list, tuple], optional
        The labels for the axes. The length must correspond to the array
        dimensions. The default is None.
    **axis_ranges : Union[dict, list, tuple], optional
        The ranges for the axes. The length must correspond to the array
        dimensions. The default is None.
    **axis_units : Union[dict, list, tuple], optional
        The units for the axes. The length must correspond to the array
        dimensions. The default is None.
    **metadata : Union[dict, None], optional
        A dictionary with metadata. The default is None.
    **data_unit : str, optional
        The description of the data unit. The default is an empty string.
    **data_label : str, optional
        The description of the data. The default is an empty string.
    """

    def __new__(cls, array: np.ndarray, **kwargs: dict) -> Self:
        """
        Create a new Dataset.

        Parameters
        ----------
        array : np.ndarray
            The data array.
        **kwargs : type
            Accepted keywords are axis_labels, axis_ranges, axis_units,
            metadata, data_unit. For information on the keywords please refer
            to the class docstring.

        Returns
        -------
        obj : Dataset
            The new dataset object.
        """
        obj = np.asarray(array).view(cls)
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
        pydidas.core.Dataset
            The sliced new dataset.
        """
        self._meta["getitem_key"] = key if isinstance(key, tuple) else (key,)
        _item = np.ndarray.__getitem__(self, key)
        if not isinstance(_item, np.ndarray):
            self._meta["getitem_key"] = ()
        return _item

    def __array_finalize__(self, obj: Self):
        """
        Finalizazion of numpy.ndarray object creation.

        This method will delete or append dimensions to the associated
        axis_labels/_ranges/_units attributes, depending on the object
        dimensionality.
        """
        if obj is None or self.shape == tuple():
            return
        self.__update_keys_from_object(obj)
        if hasattr(obj, "_meta"):
            obj._meta["getitem_key"] = ()
        self._meta["getitem_key"] = ()

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
            _key: deepcopy(getattr(obj, _key, _default))
            for _key, _default in [
                ["axis_labels", dataset_ax_str_default(self.ndim)],
                ["axis_units", dataset_ax_str_default(self.ndim)],
                ["axis_ranges", dataset_ax_default_ranges(self.shape)],
                ["metadata", dataset_property_default_val("metadata")],
                ["data_unit", dataset_property_default_val("data_unit")],
                ["data_label", dataset_property_default_val("data_label")],
            ]
        }
        self._meta["getitem_key"] = getattr(obj, "_meta", {}).get("getitem_key", ())
        for _dim, _slicer in enumerate(self._meta["getitem_key"]):
            if isinstance(_slicer, np.ndarray) and _slicer.size == obj.size:
                # in the case of a masked array, keep all axis keys.
                break
            if isinstance(_slicer, Integral):
                for _item in ["axis_labels", "axis_units", "axis_ranges"]:
                    del self._meta[_item][_dim]
            elif isinstance(_slicer, (slice, Iterable, np.ndarray)):
                if isinstance(_slicer, tuple):
                    _slicer = list(_slicer)
                if self._meta["axis_ranges"][_dim] is not None:
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
            _new_entry = np.arange(self.shape[dim]) if _item == "axis_ranges" else ""
            _copy = {}
            _dict = self._meta[_item]
            for _key in sorted(_dict):
                if _key < dim:
                    _copy[_key] = _dict[_key]
                elif _key == dim:
                    _copy[dim] = _new_entry
                    _copy[_key + 1] = _dict[_key]
                else:
                    _copy[_key + 1] = _dict[_key]
            if dim not in _copy:
                _copy[dim] = _new_entry
            self._meta[_item] = _copy

    def flatten_dims(
        self,
        *args: tuple,
        new_dim_label: str = "Flattened",
        new_dim_unit: str = "",
        new_dim_range: Union[None, np.ndarray, Iterable] = None,
    ):
        """
        Flatten the specified dimensions in place in the Dataset.

        This method will reduce the dimensionality of the Dataset by len(args).

        Warning: Flattening distributed dimensions throughout the dataset will
        destroy the data organisation and only adjacent dimensions can be
        processed.

        Parameters
        ----------
        *args : tuple
            The tuple of the dimensions to be flattened. Each dimension must
            be an integer entry.
        new_dim_label : str, optional
            The label for the new, flattened dimension. The default is
            'Flattened'.
        new_dim_unit : str, optional
            The unit for the new, flattened dimension. The default is ''.
        new_dim_range : Union[None, np.ndarray, Iterable], optional
            The new range for the flattened dimension. If None, a simple The
            default is None.
        """
        if len(args) < 2:
            return
        if set(np.diff(args)) != {1}:
            raise ValueError("The dimensions to flatten must be adjacent.")
        _axis_labels = []
        _axis_units = []
        _axis_ranges = []
        _new_shape = []
        for _dim in range(self.ndim):
            if _dim not in args:
                _axis_labels.append(self._meta["axis_labels"][_dim])
                _axis_units.append(self._meta["axis_units"][_dim])
                _axis_ranges.append(self._meta["axis_ranges"][_dim])
                _new_shape.append(self.shape[_dim])
            elif _dim == args[0]:
                _axis_labels.append(new_dim_label)
                _axis_units.append(new_dim_unit)
                _axis_ranges.append(new_dim_range)
                _new_shape.append(np.prod([self.shape[_arg] for _arg in args]))
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            self.shape = _new_shape
        self.axis_labels = _axis_labels
        self.axis_units = _axis_units
        self.axis_ranges = _axis_ranges

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
        pydidas.core.Dataset
            The binned Dataset.
        """
        if binning == 1:
            return self.copy()
        _shape = np.asarray(self.shape)
        _lowlim = (_shape % binning) // 2
        _highlim = _shape - (_shape % binning) + _lowlim
        _highlim[_highlim == _lowlim] += 1
        _slices = tuple(slice(low, high) for low, high in zip(_lowlim, _highlim))
        _copy = self[_slices]
        _newshape = tuple()
        for _s in self.shape:
            _addon = (1, 1) if _s == 1 else (_s // binning, binning)
            _newshape = _newshape + _addon
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            _copy.shape = _newshape
            _copy = np.mean(_copy, axis=tuple(np.arange(1, _copy.ndim, 2)))
        _copy.axis_labels = self.axis_labels.copy()
        _copy.axis_units = self.axis_units.copy()
        _axis_ranges = self.axis_ranges.copy()
        for _dim, _range in _axis_ranges.items():
            if isinstance(_range, np.ndarray):
                _new = _range[_slices[_dim]]
                _new = _new.reshape(_new.size // binning, binning).mean(-1)
                _axis_ranges[_dim] = _new
        _copy.axis_ranges = _axis_ranges
        return _copy

    # ##########
    # Properties
    # ##########

    @property
    def property_dict(self) -> dict:
        """
        Get a copy of the properties dictionary.

        Returns
        -------
        dict
            A dictionary with copies of all properties.
        """
        return {_key: deepcopy(_val) for _key, _val in self._meta.items()}

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
    def array(self) -> np.ndarray:
        """
        Get the raw array data of the dataset.

        Returns
        -------
        np.ndarray
            The array data.
        """
        return self.__array__()

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
        return self._meta["axis_units"].copy()

    @axis_units.setter
    def axis_units(self, units: Union[Iterable, dict]):
        """
        Set the axis_units metadata.

        Parameters
        ----------
        labels : Union[Iterable, dict]
            The new axis units. Both Iterables (of length ndim) as well as
            dictionaries (with keys [0, 1, ..., ndim -1]) are accepted.
        """
        self._meta["axis_units"] = convert_data_to_dict(units, self.shape, "axis_units")

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
        self._meta["axis_labels"] = convert_data_to_dict(
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
        return self._meta["axis_ranges"].copy()

    @axis_ranges.setter
    def axis_ranges(self, ranges: Union[Iterable, dict]):
        """
        Set the axis_ranges metadata.

        Parameters
        ----------
        labels : Union[Iterable, dict]
            The new axis ranges. Both Iterables (of length ndim) as well as
            dictionaries (with keys [0, 1, ..., ndim -1]) are accepted.
        """
        _ranges = convert_data_to_dict(ranges, self.shape, "axis_ranges")
        self._convert_ranges_and_verify_length_okay(_ranges)
        self._meta["axis_ranges"] = _ranges

    def _convert_ranges_and_verify_length_okay(self, ranges: dict):
        """
        Convert ranges to ndarray.

        Verify that all given true ranges (i.e. with more than one item) are of type
        np.ndarray and that the length of all given ranges matches the data shape.

        Parameters
        ----------
        ranges : dict
            The dictionary with the loaded ranges.

        Raises
        ------
        ValueError
            If the given lengths do not match the data length.
        """
        _wrong_dims = []
        for _dim, _range in ranges.items():
            if item_is_iterable_but_not_array(_range):
                _range = np.asarray(_range)
                ranges[_dim] = _range
            if isinstance(_range, np.ndarray) and _range.size != self.shape[_dim]:
                _wrong_dims.append([_dim, _range.size, self.shape[_dim]])
        if len(_wrong_dims) > 0:
            _error = (
                "The length of the given ranges does not match the size of the data."
            )
            for _dim, _len, _ndata in _wrong_dims:
                _error += (
                    f"\nDimension {_dim}: Given range: {_len}; target length: {_ndata}."
                )
            raise ValueError(_error)

    # ######################################
    # Update methods for the axis properties
    # ######################################

    def update_axis_range(self, index: int, item: Union[np.ndarray, Iterable]):
        """
        Update a single axis range value.

        Parameters
        ----------
        index : int
            The dimension to be updated.
        item : Union[np.ndarray, Iterable]
            The new item for the range of the selected dimension.

        Raises
        ------
        ValueError
            If the index is not in range of the Dataset dimensions.
        """
        if not 0 <= index < self.ndim:
            raise ValueError(f"The index '{index}' is out of bounds (0..{self.ndim}).")
        self._convert_ranges_and_verify_length_okay({index: item})
        self._meta["axis_ranges"][index] = item

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
                f"The item *{item}* is not a string. Cannot update the axis label."
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

    # ############################################
    # Reimplementations of generic ndarray methods
    # ############################################

    def transpose(self, *axes: tuple) -> Self:
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
        _new = np.ndarray.transpose(deepcopy(self), axes)
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
        self._meta["axis_labels"] = {0: "Flattened"}
        self._meta["axis_ranges"] = {0: np.arange(self.size)}
        self._meta["axis_units"] = {0: ""}
        _new = np.ndarray.flatten(self, order)
        _new._update_keys_in_flattened_array()
        return _new

    def _update_keys_in_flattened_array(self):
        """
        Update the keys in flattened arrays i.e. if the new dimension is one.

        Note that the metadara keys are updated in place.
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
        pydidas.core.Dataset
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
            _new = np.ndarray.squeeze(self, axis)
            for _key in ["axis_labels", "axis_ranges", "axis_units"]:
                _entry = [_v for _k, _v in getattr(self, _key).items() if _k in _axes]
                setattr(_new, _key, _entry)
        return _new

    def take(
        self,
        indices: Union[int, ArrayLike],
        axis: Union[int, None] = None,
        out: Union[None, np.ndarray] = None,
        mode: Literal["raise", "wrap", "clip"] = "raise",
    ) -> Self:
        """
        Take elements from an array along an axis.

        This method overloads the ndarray.take method to process the axis properties
        as well.

        Parameters
        ----------
        indices : Union[int, ArrayLike]
            The indicies of the values to extract.
        axis : Union[None, int], optional
            The axis to take the data from. If None, data will be taken from the
            flattened array. The default is None.
        out : Union[np.ndarray, None], optional
            An optional output array. If None, a new array is created. The default is
            None.
        mode : str, optional
            Specifies how out-of-bounds indices will behave. The default is "raise".

        Returns
        -------
        new : pydidas.core.Dataset
            The new dataset.
        """
        _new = np.ndarray.take(self, indices, axis, out, mode)
        if not isinstance(_new, Dataset) or axis is None:
            return _new
        _nindices = get_number_of_entries(indices)
        if _nindices == 1 and not isinstance(indices, Iterable):
            for _key in ["axis_labels", "axis_units", "axis_ranges"]:
                _item = getattr(_new, _key)
                _item.pop(axis)
                setattr(_new, _key, _item.values())
        else:
            if isinstance(_new._meta["axis_ranges"][axis], np.ndarray):
                _new._meta["axis_ranges"][axis] = np.take(
                    self.axis_ranges[axis], indices
                )
        return _new

    def copy(self, order: Literal["C", "F", "A", "K"] = "C") -> Self:
        """
        Overload the generic nd.ndarray copy method to copy metadata as well.

        Parameters
        ----------
        order : {‘C’, ‘F’, ‘A’, ‘K’},, optional
            The memory layout. The default is "C".

        Returns
        -------
        Dataset
            The copied dataset.
        """
        _new = np.ndarray.copy(self, order)
        _new._meta = {
            _key: self._meta[_key].copy()
            for _key in ["axis_labels", "axis_units", "axis_ranges"]
        } | {
            _key: self._meta[_key]
            for _key in ["data_unit", "data_label", "getitem_key"]
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
        _thresh = np.get_printoptions()["threshold"]
        _edgeitems = 2 if self.ndim > 1 else 3
        np.set_printoptions(threshold=20, edgeitems=_edgeitems)
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
            "array": self.__array__().__repr__(),
        }
        _repr = (
            self.__class__.__name__
            + "(\n"
            + ",\n".join(_str for _str in _info.values())
            + "\n)"
        )
        np.set_printoptions(threshold=_thresh, edgeitems=3)
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
            https://docs.python.org/2/library/pickle.html#object.__reduce__
            for the full documentation. The class' state is appended with
            the class' __dict__
        """
        _ndarray_reduced = np.ndarray.__reduce__(self)
        _dataset_state = _ndarray_reduced[2] + (self.__dict__,)
        return (_ndarray_reduced[0], _ndarray_reduced[1], _dataset_state)

    def __setstate__(self, state: tuple):
        """
        Reimplementation of the numpy.ndarray.__setstate__.

        This method is called after pickling to restore the object. The
        Dataset's __setstate__ method adds the restoration of the __dict__
        to the generic numpy.ndarray.__setstate__.

        Parameters
        ----------
        state : tuple
            The pickled objcts state.
        """
        self.__dict__ = state[-1]
        np.ndarray.__setstate__(self, state[0:-1])

    def __array_wrap__(
        self, obj: np.ndarray, context: Union[None, object] = None
    ) -> Self:
        """
        Return 0-d results from ufuncs as single values.

        This method overloads the generic __array_wrap__ to return values and not
        0-d results for Dataset arrays.

        Parameters
        ----------
        obj : Union[np.ndarray, pydidas.core.Dataset]
            The output array from the ufunc call.
        context : Union[None, object], optional
            The calling context. The default is None.

        Returns
        -------
        Union[pydidas.core.Dataset, type]
            The output will be be a new Dataset if the output has a dimension
            greater zero or of the basic datatype for 0-d return values.
        """
        if obj.shape == ():
            return np.atleast_1d(obj)[0]
        return np.ndarray.__array_wrap__(self, obj, context)

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
