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
__copyright__ = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.0.1"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['Dataset']

import warnings
from numbers import Integral
from collections.abc import Iterable
from copy import copy

import numpy as np

from .exceptions import DatasetConfigException


def _default_vals(ndim):
    """
    Generate default values of None for a number of dimensions.

    Parameters
    ----------
    ndim : int
        The number of dimensions

    Returns
    -------
    dict
        A dict with entries of type (dim: None).
    """
    return {i: None for i in range(ndim)}


class EmptyDataset(np.ndarray):
    """
    Inherits from :py:class:`numpy.ndarray`

    Base class of an empty dataset (numpy.ndarray subclass) for instantiation.
    """
    __safe_for_unpickling__ = True

    def __new__(cls, *args, **kwargs):
        """
        __new__ method for creation of new numpy.ndarray object.
        """
        local_kws = kwargs.copy()
        for item in ['axis_labels', 'axis_ranges', 'axis_units', 'metadata']:
            if item in kwargs:
                del kwargs[item]
        obj = np.ndarray.__new__(cls, *args, **kwargs)
        for key in ['axis_labels', 'axis_ranges', 'axis_units']:
            _data = local_kws.get(key, _default_vals(obj.ndim))
            _labels = obj._get_dict(_data, '__new__')
            setattr(obj, key, _labels)
        obj.metadata = local_kws.get('metadata', {})
        obj.getitem_key = None
        return obj

    def __getitem__(self, key):
        """
        Overwrite the generic __getitem__ method to catch the the slicing
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
        return super().__getitem__(key)

    def __array_finalize__(self, obj):
        """
        Finalizazion of numpy.ndarray object creation.

        This method will delete or append dimensions to the associated
        axis_labels/_scales/_units attributes, depending on the object
        dimensionality.
        """
        if obj is None or self.shape == tuple():
            return
        self.metadata = getattr(obj, 'metadata', {})
        self.getitem_key = getattr(obj, 'getitem_key', None)

        self.__check_and_set_default_axis_attributes()
        self._keys = {_key: copy(getattr(obj, _key, _default_vals(self.ndim)))
                      for _key in ['axis_labels', 'axis_ranges', 'axis_units']}

        if self.getitem_key is not None:
            self.__modify_axis_keys()
        self.__update_keys_for_flattened_array()

        for _key in ['axis_labels', 'axis_ranges', 'axis_units']:
            setattr(self, f'_{_key}', self._keys[_key])
        if isinstance(obj, EmptyDataset):
            obj.getitem_key = None
        self.getitem_key = None

    def __check_and_set_default_axis_attributes(self):
        """
        Check whether the attributes for axis_labels, -units and -ranges exist
        and initialize them with default values if not.
        """
        for _att in ['_axis_labels', '_axis_units', '_axis_ranges']:
            if not hasattr(self, _att):
                setattr(self, _att, _default_vals(self.ndim))

    def __modify_axis_keys(self):
        """
        Modify the axis keys (axis_labels, -_units, and -_ranges) and store
        the new values in place.
        """
        for _dim, _cutter in enumerate(self.getitem_key):
            # in the case of a masked array, keep all axis keys.
            if isinstance(_cutter, np.ndarray) and _cutter.ndim > 1:
                return
            if isinstance(_cutter, Integral):
                self.__store_keys_in_metadata(_dim, _cutter)
                for _item in ['axis_labels', 'axis_units', 'axis_ranges']:
                    del self._keys[_item][_dim]
            elif isinstance(_cutter, (slice, Iterable, np.ndarray)):
                if self._keys['axis_ranges'][_dim] is not None:
                    self._keys['axis_ranges'][_dim] = (
                        self._keys['axis_ranges'][_dim][_cutter])
            elif _cutter is None:
                self.__insert_axis_keys(_dim)
        # finally, shift all keys to have a consistent numbering:
        for _item in ['axis_labels', 'axis_units', 'axis_ranges']:
            _itemdict = self._keys[_item]
            _newkeys = {_index: _itemdict[_key] for _index, _key
                        in enumerate(sorted(_itemdict))}
            self._keys[_item] = _newkeys

    def __store_keys_in_metadata(self, dim, cutter):
        """
        Store the sliced key in the metadata.

        Parameters
        ----------
        dim : int
            The sliced dimension.
        cutter : Union[int, slice]
            The cutting object to reduce the specified dimension.
        """
        for _item in ['axis_labels', 'axis_units']:
            _refkey = f'sliced_dim_{dim:02d}_{_item[5:-1]}'
            self.metadata[_refkey] = self._keys[_item][dim]
        _refkey = f'sliced_dim_{dim:02d}_range_value'
        if self._keys['axis_ranges'][dim] is not None:
            self.metadata[_refkey] = self._keys['axis_ranges'][dim][cutter]
        else:
            self.metadata[_refkey] = None

    def __insert_axis_keys(self, dim):
        """
        Insert a new axis key at the specified dimension.

        Parameters
        ----------
        dim : int
            The dimension in front of which the new key shall be inserted.
        """
        for _item in ['axis_labels', 'axis_units', 'axis_ranges']:
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

    def __update_keys_for_flattened_array(self):
        """
        Update the keys for flattened arrays.
        """
        if self.ndim == 1 and (len(self._keys['axis_ranges']) > 1
                               or len(self._keys['axis_units']) > 1
                               or len(self._keys['axis_labels']) > 1):
            self._keys['axis_labels'] = {0: 'Flattened'}
            self._keys['axis_ranges'] = {0: np.arange(self.size)}
            self._keys['axis_units'] = {0: ''}

    def flatten(self, order='C'):
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
        self._axis_labels = {0: 'Flattened'}
        self._axis_ranges = {0: np.arange(self.size)}
        self._axis_units = {0: ''}
        return super().flatten(order)

    def flatten_dims(self, *args, new_dim_label='Flattened',
                     new_dim_unit='', new_dim_range=None):
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
        if set(np.diff(args)) != set([1]):
            raise ValueError('The dimensions to flatten must be adjacent.')
        _axis_labels = []
        _axis_units = []
        _axis_ranges = []
        _new_shape = []
        for _dim in range(self.ndim):
            if _dim not in args:
                _axis_labels.append(self._axis_labels[_dim])
                _axis_units.append(self._axis_units[_dim])
                _axis_ranges.append(self._axis_ranges[_dim])
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
        _slices = tuple(slice(low, high)
                        for low, high in zip(_lowlim, _highlim))
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

    def _get_dict(self, _data, method_name):
        """
        Get an ordered dictionary with the axis keys for _data.

        This method will create a dictionary from lists or tuples and sort
        dictionary keys for dict inputs. The new keys will be 0, 1, ...,
        ndim - 1.

        Parameters
        ----------
        _data : Union[dict, list, tuple]
            The keys for the axis meta data.
        method_name : str
            The name of the calling method (for exception handling)

        Raises
        ------
        DatasetConfigException
            If a dictionary is passed as data and the keys do not correspond
            to the set(0, 1, ..., ndim - 1)
        DatasetConfigException
            If a tuple of list is passed and the length of entries is not
            equal to ndim.

        Returns
        -------
        dict
            A dictionary with keys [0, 1, ..., ndim - 1] and the corresponding
            values from the input _data.
        """
        if isinstance(_data, dict):
            if set(_data.keys()) != set(np.arange(self.ndim)):
                warnings.warn('The number of keys does not match the number '
                              'of array dimensions. Resettings keys to '
                              'defaults. (Error encountered in '
                              f'{method_name}).')
                return _default_vals(self.ndim)
            return  _data
        if isinstance(_data, (list, tuple)):
            if len(_data) != self.ndim:
                warnings.warn('The number of keys does not match the number '
                              'of array dimensions. Resettings keys to '
                              'defaults.(Error encountered in '
                              f'{method_name}).')
                return _default_vals(self.ndim)
            _data = dict(enumerate(_data))
            return _data
        raise DatasetConfigException(
            f'Input {_data} cannot be converted to dictionary for property'
            f' {method_name}')

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
        return self._axis_labels

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
        self._axis_labels = self._get_dict(labels, 'axis_labels')

    @property
    def axis_ranges(self):
        """
        Get the axis ranges. These arrays for every dimension give the range
        of the data (in conjunction with the units).

        Returns
        -------
        dict
            The axis scales: A dictionary with keys corresponding to the
            dimension in the array and respective values.
        """
        return self._axis_ranges

    @axis_ranges.setter
    def axis_ranges(self, scales):
        """
        Set the axis_ranges metadata.

        Parameters
        ----------
        labels : Union[dict, list, tuple]
            The new axis scales. Both tuples and lists (of length ndim) as
            well as dictionaries (with keys [0, 1, ..., ndim -1]) are
            accepted.
        """
        self._axis_ranges = self._get_dict(scales, 'axis_ranges')

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
        return self._axis_units

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
        self._axis_units = self._get_dict(units, 'axis_units')

    @property
    def metadata(self):
        """
        Get the image ID.

        Returns
        -------
        integer
            The image ID.
        """
        return self.__metadata

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
            raise TypeError('Metadata must be a dictionary or None.')
        self.__metadata = metadata

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

    def __repr__(self):
        """
        Reimplementation of the numpy.ndarray.__repr__ method

        Returns
        -------
        str
            The representation of the Dataset class.
        """
        _info = {'axis_labels': self.axis_labels,
                 'axis_ranges': self.axis_ranges,
                 'axis_units': self.axis_units,
                 'metadata': self.metadata,
                 'array': self.__array__()}
        return (self.__class__.__name__
                + '(\n'
                + ', '.join(f'{i}: {_info[i]}\n' for i in _info)
                + ')')

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


class Dataset(EmptyDataset):
    """
    Inherits from :py:class:`pydidas.core.EmptyDataset
    <pydidas.core.EmptyDataset>`

    Dataset class, a subclass of a numpy ndarray with metadata.

    Parameters for class creation:
    ------------------------------
    array : np.ndarray
        The data array.
    axis_labels : Union[dict, list, tuple], optional
        The labels for the axes. The length must correspond to the array
        dimensions. The default is None.
    axis_ranges : Union[dict, list, tuple], optional
        The scales for the axes. The length must correspond to the array
        dimensions. The default is None.
    axis_units : Union[dict, list, tuple], optional
        The units for the axes. The length must correspond to the array
        dimensions. The default is None.
    metadata : Union[dict, None], optional
        A dictionary with metadata. The default is None.
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
            metadata. For information on the keywords please refer to the
            class docstring.

        Returns
        -------
        obj : Dataset
            The new dataset object.
        """
        obj = np.asarray(array).view(cls)
        obj.axis_units = kwargs.get('axis_units', _default_vals(obj.ndim))
        obj.axis_labels = kwargs.get('axis_labels', _default_vals(obj.ndim))
        obj.axis_ranges = kwargs.get('axis_ranges', _default_vals(obj.ndim))
        obj.metadata = kwargs.get('metadata', {})
        return obj
