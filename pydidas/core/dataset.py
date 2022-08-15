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
The dataset module includes subclasses of numpy.ndarray with additional
embedded metadata.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ["Dataset", "EmptyDataset"]

import warnings
from numbers import Integral
from collections.abc import Iterable
from copy import deepcopy

import numpy as np

from pydidas.core.utils.dataset_utils import (
    get_number_of_entries,
    get_axis_item_representation,
    convert_data_to_dict,
    update_dataset_properties_from_kwargs,
    dataset_property_default_val,
    dataset_ax_default_range,
    item_is_iterable_but_not_array,
)


class EmptyDataset(np.ndarray):
    """
    Base class of an empty dataset (numpy.ndarray subclass) for instantiation.
    """

    __safe_for_unpickling__ = True

    def __new__(cls, *args, **kwargs):
        """
        __new__ method for creation of new numpy.ndarray object.
        """
        local_kws = kwargs.copy()
        for item in [
            "axis_labels",
            "axis_ranges",
            "axis_units",
            "metadata",
            "data_unit",
            "data_label",
        ]:
            if item in kwargs:
                del kwargs[item]
        obj = np.ndarray.__new__(cls, *args, **kwargs)
        update_dataset_properties_from_kwargs(obj, local_kws)
        return obj

    def __getitem__(self, key):
        """
        Overwrite the generic __getitem__ method to catch the slicing
        keys.

        Parameters
        ----------
        key : Union[int, tuple]
            The slicing objects

        Returns
        -------
        pydidas.core.Dataset
            The sliced new dataset.
        """
        self.getitem_key = key if isinstance(key, tuple) else (key,)
        return np.ndarray.__getitem__(self, key)

    def __array_finalize__(self, obj):
        """
        Finalizazion of numpy.ndarray object creation.

        This method will delete or append dimensions to the associated
        axis_labels/_ranges/_units attributes, depending on the object
        dimensionality.
        """
        if obj is None or self.shape == tuple():
            return
        for _property in ["metadata", "data_unit", "data_label", "getitem_key"]:
            _obj_prop = getattr(obj, _property, dataset_property_default_val(_property))
            setattr(self, _property, _obj_prop)
        self.__update_keys_from_object(obj)
        if isinstance(obj, EmptyDataset):
            obj.getitem_key = None
        self.getitem_key = None

    def __update_keys_from_object(self, obj):
        """
        Update the axis keys from the original object
        """
        self._keys = {
            _key: deepcopy(getattr(obj, _key, dataset_ax_default_range(self.ndim)))
            for _key in ["axis_labels", "axis_ranges", "axis_units"]
        }
        self.getitem_key = [] if self.getitem_key is None else self.getitem_key
        for _dim, _slicer in enumerate(self.getitem_key):
            # in the case of a masked array, keep all axis keys.
            if isinstance(_slicer, np.ndarray) and _slicer.ndim > 1:
                break
            if isinstance(_slicer, Integral):
                for _item in ["axis_labels", "axis_units", "axis_ranges"]:
                    del self._keys[_item][_dim]
            elif isinstance(_slicer, (slice, Iterable, np.ndarray)):
                if self._keys["axis_ranges"][_dim] is not None:
                    self._keys["axis_ranges"][_dim] = self._keys["axis_ranges"][_dim][
                        _slicer
                    ]
            elif _slicer is None:
                self.__insert_axis_keys(_dim)
        # finally, shift all keys to have a consistent numbering:
        for _item in ["axis_labels", "axis_units", "axis_ranges"]:
            self._keys[_item] = dict(enumerate(self._keys[_item].values()))

    def __insert_axis_keys(self, dim):
        """
        Insert a new axis key at the specified dimension.

        Parameters
        ----------
        dim : int
            The dimension in front of which the new key shall be inserted.
        """
        for _item in ["axis_labels", "axis_units", "axis_ranges"]:
            _copy = {}
            _dict = self._keys[_item]
            for _key in sorted(_dict):
                if _key < dim:
                    _copy[_key] = _dict[_key]
                elif _key == dim:
                    _copy[_key] = None
                    _copy[_key + 1] = _dict[_key]
                else:
                    _copy[_key + 1] = _dict[_key]
            self._keys[_item] = _copy

    def flatten_dims(
        self, *args, new_dim_label="Flattened", new_dim_unit="", new_dim_range=None
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
        new_dim_range : object, optional
            The new range for the flattened dimension. The default is None.
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
                _axis_labels.append(self._keys["axis_labels"][_dim])
                _axis_units.append(self._keys["axis_units"][_dim])
                _axis_ranges.append(self._keys["axis_ranges"][_dim])
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

    def transpose(self, *axes):
        """
        Overload the generic transpose method to transpose the metadata as
        well.

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

    def get_rebinned_copy(self, binning):
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
        _copy = self.__getitem__(_slices)
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
    def data_unit(self):
        """
        Get the data unit.

        Returns
        -------
        str
            The data unit.
        """
        return self._data_unit

    @data_unit.setter
    def data_unit(self, data_unit):
        """
        Set the data unit

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
        self._data_unit = data_unit

    @property
    def data_label(self):
        """
        Get the data label.

        Returns
        -------
        str
            The data label.
        """
        return self._data_label

    @data_label.setter
    def data_label(self, data_label):
        """
        Set the data unit

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
        self._data_label = data_label

    @property
    def metadata(self):
        """
        Get the image ID.

        Returns
        -------
        integer
            The image ID.
        """
        return self._metadata.copy()

    @metadata.setter
    def metadata(self, metadata):
        """
        Set the image metadata.

        Parameters
        ----------
        metadata : Union[dict, None]
            The image metadata.

        Raises
        ------
        ValueError
            If metadata is not None or dict
        """
        if not (isinstance(metadata, dict) or metadata is None):
            raise TypeError("Metadata must be a dictionary or None.")
        self._metadata = metadata

    @property
    def array(self):
        """
        Get the raw array data of the dataset.

        Returns
        -------
        np.ndarray
            The array data.
        """
        return self.__array__()

    @property
    def axis_units(self):
        """
        Get the axis units.

        Returns
        -------
        dict
            The axis units: A dictionary with keys corresponding to the
            dimension in the array and respective values.
        """
        return self._keys["axis_units"].copy()

    @axis_units.setter
    def axis_units(self, units):
        """
        Set the axis_units metadata.

        Parameters
        ----------
        labels : Union[dict, list, tuple]
            The new axis units. Both tuples and lists (of length ndim) as
            well as dictionaries (with keys [0, 1, ..., ndim -1]) are
            accepted.
        """
        self._keys["axis_units"] = convert_data_to_dict(units, self.ndim, "axis_units")

    @property
    def axis_labels(self):
        """
        Get the axis_labels

        Returns
        -------
        dict
            The axis labels: A dictionary with keys corresponding to the
            dimension in the array and respective values.
        """
        return self._keys["axis_labels"].copy()

    @axis_labels.setter
    def axis_labels(self, labels):
        """
        Set the axis_labels metadata.

        Parameters
        ----------
        labels : Union[dict, list, tuple]
            The new axis labels. Both tuples and lists (of length ndim) as
            well as dictionaries (with keys [0, 1, ..., ndim -1]) are
            accepted.
        """
        self._keys["axis_labels"] = convert_data_to_dict(
            labels, self.ndim, "axis_labels"
        )

    @property
    def axis_ranges(self):
        """
        Get the axis ranges. These arrays for every dimension give the range
        of the data (in conjunction with the units).

        Returns
        -------
        dict
            The axis ranges: A dictionary with keys corresponding to the
            dimension in the array and respective values.
        """
        return self._keys["axis_ranges"].copy()

    @axis_ranges.setter
    def axis_ranges(self, ranges):
        """
        Set the axis_ranges metadata.

        Parameters
        ----------
        labels : Union[dict, list, tuple]
            The new axis ranges. Both tuples and lists (of length ndim) as
            well as dictionaries (with keys [0, 1, ..., ndim -1]) are
            accepted.
        """
        _ranges = convert_data_to_dict(ranges, self.ndim, "axis_ranges")
        self._convert_ranges_and_verify_length_okay(_ranges)
        self._keys["axis_ranges"] = _ranges

    def _convert_ranges_and_verify_length_okay(self, ranges):
        """
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

    def convert_all_none_properties(self):
        """
        Convert all properties of NoneType to their default values.
        """
        self._data_unit = self._data_unit if self._data_unit is not None else ""
        self._data_label = self._data_label if self._data_label is not None else ""
        for _name in ["axis_units", "axis_labels"]:
            _dict = self._keys[_name]
            for _index, _key in _dict.items():
                if _key is None:
                    _dict[_index] = ""
        for _index, _key in self._keys["axis_ranges"].items():
            if _key is None:
                self._keys["axis_ranges"][_index] = np.arange(self.shape[_index])

    # ################################################
    # Implement update methods for the axis properties
    # ################################################

    def update_axis_ranges(self, index, item):
        """
        Update a single axis ranges value.

        Parameters
        ----------
        index : int
            The dimension to be updated.
        item : Union[None, str, np.ndarray]
            The new item for the range of the selected dimension.

        Raises
        ------
        ValueError
            If the index is not in range of the Dataset dimensions.
        """
        if not 0 <= index < self.ndim:
            raise ValueError(f"The index '{index}' is out of bounds (0..{self.ndim}).")
        self._convert_ranges_and_verify_length_okay({index: item})
        self._keys["axis_ranges"][index] = item

    def update_axis_labels(self, index, item):
        """
        Update a single axis label value.

        Parameters
        ----------
        index : int
            The dimension to be updated.
        item : Union[None, str, np.ndarray]
            The new item for the range of the selected dimension.

        Raises
        ------
        ValueError
            If the index is not in range of the Dataset dimensions.
        """
        if not 0 <= index < self.ndim:
            raise ValueError(f"The index '{index}' is out of bounds (0..{self.ndim}).")
        self._keys["axis_labels"][index] = item

    def update_axis_units(self, index, item):
        """
        Update a single axis unit value.

        Parameters
        ----------
        index : int
            The dimension to be updated.
        item : Union[None, str, np.ndarray]
            The new item for the range of the selected dimension.

        Raises
        ------
        ValueError
            If the index is not in range of the Dataset dimensions.
        """
        if not 0 <= index < self.ndim:
            raise ValueError(f"The index '{index}' is out of bounds (0..{self.ndim}).")
        self._keys["axis_units"][index] = item

    # ############################################
    # Reimplementations of generic ndarray methods
    # ############################################

    def flatten(self, order="C"):
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
        self._keys["axis_labels"] = {0: "Flattened"}
        self._keys["axis_ranges"] = {0: np.arange(self.size)}
        self._keys["axis_units"] = {0: ""}
        _new = np.ndarray.flatten(self, order)
        _new.update_keys_in_flattened_array()
        return _new

    def update_keys_in_flattened_array(self):
        """
        Update the keys in flattened arrays i.e. if the new dimension is one.
        """
        if self.ndim == 1 and (
            len(self._keys["axis_ranges"]) > 1
            or len(self._keys["axis_units"]) > 1
            or len(self._keys["axis_labels"]) > 1
        ):
            self._keys["axis_labels"] = {0: "Flattened"}
            self._keys["axis_ranges"] = {0: np.arange(self.size)}
            self._keys["axis_units"] = {0: ""}

    def squeeze(self, axis=None):
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
        _new = np.ndarray.squeeze(self, axis)
        for _key in ["axis_labels", "axis_ranges", "axis_units"]:
            _entry = [_v for _k, _v in getattr(self, _key).items() if _k in _axes]
            setattr(_new, _key, _entry)
        return _new

    def take(self, indices, axis=None, out=None, mode="raise"):
        """
        Take elements from an array along an axis.

        This method overloads the ndarray.take method to process the axis properties
        as well.

        Parameters
        ----------
        indices : Union[int, array_like]
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
        if not isinstance(_new, EmptyDataset) or axis is None:
            return _new
        _nindices = get_number_of_entries(indices)
        if _nindices == 1 and not isinstance(indices, Iterable):
            for _key in ["axis_labels", "axis_units", "axis_ranges"]:
                _item = getattr(_new, _key)
                _item.pop(axis)
                setattr(_new, _key, _item.values())
        else:
            if isinstance(_new._keys["axis_ranges"][axis], np.ndarray):
                _new._keys["axis_ranges"][axis] = np.take(
                    self.axis_ranges[axis], indices
                )
        return _new

    def __repr__(self):
        """
        Reimplementation of the numpy.ndarray.__repr__ method

        Returns
        -------
        str
            The representation of the Dataset class.
        """
        _thresh = np.get_printoptions()["threshold"]
        _edgeitems = 2 if self.ndim > 1 else 3
        np.set_printoptions(threshold=20, edgeitems=_edgeitems)
        _meta_repr = "\n".join(get_axis_item_representation("metadata", self._metadata))
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

    def __get_axis_item_repr(self, obj_name):
        """
        Get a string representation for a dictionary item of 'axis_labels',
        'axis_ranges' or 'axis_units'

        Parameters
        ----------
        obj_name : str
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

    def __str__(self):
        """
        Reimplementation of the numpy.ndarray.__str__ method.

        Returns
        -------
        str
            The Dataset.__repr__ string.
        """
        return self.__repr__()

    def __reduce__(self):
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

    def __setstate__(self, state):
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

    def __array_wrap__(self, out_arr, context=None):
        """
        Overload the generic __array_wrap__ to return 0-d results from ufuncs
        as single values and not empty Dataset arrays.

        Parameters
        ----------
        out_arr : Union[np.ndarray, pydidas.core.Dataset]
            The output array from the ufunc call.
        context : Union[None, type], optional
            The calling context. The default is None.

        Returns
        -------
        Union[pydidas.core.Dataset, type]
            The output will be be a new Dataset if the output has a dimension
            greater zero or of the basic datatype for 0-d return values.
        """
        if out_arr.shape == ():
            return np.atleast_1d(out_arr)[0]
        return np.ndarray.__array_wrap__(self, out_arr, context)


class Dataset(EmptyDataset):
    """
    Dataset class, a subclass of a numpy ndarray with metadata.

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

    def __new__(cls, array, *args, **kwargs):
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
