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
Module with the RoiSliceManager class which reads arguments and creates slice
objects for ROI cropping.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["RoiSliceManager"]


import copy
from numbers import Integral
from typing import Union

from numpy import mod

from pydidas.core.utils import flatten_all


def error_msg(roi: object, exception: Exception = "") -> str:
    """
    Get a formatted error message.

    Parameters
    ----------
    roi : object
        The ROI key which is being parsed.
    exception : Exception
        The exception text if it has been raised.

    Returns
    -------
    str
        The updated Exception error message.
    """
    _str = f'The format of the ROI "{roi}" could not be interpreted.'
    if exception:
        _str = _str[:-1] + f": {exception}"
    return _str


class RoiSliceManager:
    """
    The RoiSliceManager is used to create slice objects to crop images with a
    region of interest.

    Input must be given in form of a list or tuple. Acceptable formats for each
    input are:

        - int for any boundary
        - slice objects for a direction
        - string representations of any of the above entries.

    Parameters
    ----------
    **kwargs : dict
        Any keyword arguments
    **input_shape : Union[None, tuple], optional
        The input shape of the images. This value is only required if negative
        indices are used in the ROI to generate the correct size of the ROI.
    **dim : int, optional
        The dimension of the ROI. The default is 2.
    **roi : Union[None, tuple, dict]
        The region of interest to be used in an image. If not given at
        initialization, this value can be supplied through the .roi property.
    """

    def __init__(self, **kwargs: dict):
        self._roi = None
        self._original_roi = None
        self._input_shape = kwargs.get("input_shape", None)
        self._ndim = kwargs.get("dim", 2)
        self._original_input_shape = None
        self._roi_key = kwargs.get("roi", None)
        self.create_roi_slices()

    @property
    def input_shape(self) -> Union[None, tuple[float, float]]:
        """
        Get the shape of the input image, if given.

        Returns
        -------
        Union[None, tuple[float, float]]
            The shape of the input image.
        """
        return self._input_shape

    @input_shape.setter
    def input_shape(self, shape: Union[None, tuple[float, float]]):
        """
        Set the input shape of the image.

        Parameters
        ----------
        shape : Union[None, tuple[float, float]]
            The shape of the input image.
        """
        if not isinstance(shape, tuple):
            raise TypeError("The input shape must be a tuple.")
        self._input_shape = shape

    @property
    def roi(self) -> tuple[slice, ...]:
        """
        Get the ROI slice objects

        Returns
        -------
        tuple
            The tuple with the two slice objects to create the demanded ROI.
        """
        return self._roi

    @roi.setter
    def roi(self, _roi):
        """
        Create new ROI slice objects from the input.

        Parameters
        ----------
        _roi : Union[tuple, list, str]
            ROI creation arguments.
        """
        self._roi_key = _roi
        self.create_roi_slices()

    @property
    def roi_coords(self):
        """
        Get the pixel coordinates of the lower and upper boundaries of the
        ROI.

        Returns
        -------
        Union[None, tuple]
            If the ROI is not set, this property returns None. Else, it
            returns a tuple with (ax0_low, ax0_high, ..., ax_n_low, ax_n_high) values.
        """
        if self._roi is None:
            return None
        _coords = flatten_all(
            [[_roi.start, _roi.stop] for _roi in self._roi], astype=tuple
        )
        return _coords

    @property
    def ndim(self) -> int:
        """
        Get the number of dimensions.

        Returns
        -------
        int
            The number of dimensions.
        """
        return self._ndim

    @ndim.setter
    def ndim(self, ndim: int):
        """
        Set the number of dimensions.

        Parameters
        ----------
        ndim : int
            The new number of dimensions.
        """
        if ndim == self._ndim:
            return
        self._ndim = ndim
        self._roi = None
        self._roi_key = None

    def apply_second_roi(self, roi2):
        """
        Apply a second ROI to the ROI.

        Parameters
        ----------
        roi2 : Union[tuple, list]
            A ROI in the same format accepted by the roi property or roi
            keyword.

        Raises
        ------
        TypeError
            If the ROI could not be added.
        """
        try:
            self._original_roi = self._roi
            self._original_input_shape = self._input_shape
            self._roi_key = roi2
            self._input_shape = tuple(_roi.stop - _roi.start for _roi in self._roi)
            self.create_roi_slices()
            self._merge_rois()
        except ValueError as _error:
            self._roi = self._original_roi
            raise TypeError(f"Cannot add second ROI: {_error}")
        finally:
            self._input_shape = self._original_input_shape

    def _merge_rois(self):
        """
        Merge two ROIs and store them as the new ROI.

        Raises
        ------
        ValueError
            If negative stop indices are used. Merging only supports positive
            (i.e. absolute) slices ranges.
        """
        # slice combine explained here for all cases:
        # https://stackoverflow.com/questions/19257498/
        # combining-two-slicing-operations
        _roi = []
        for _axis in range(self._ndim):
            _slice1 = self._original_roi[_axis]
            _slice2 = self._roi[_axis]
            _step1 = _slice1.step if _slice1.step is not None else 1
            _step2 = _slice2.step if _slice2.step is not None else 1
            _step = _step1 * _step2
            _start = _slice1.start + _step1 * _slice2.start
            _stop1 = _slice1.stop if _slice1.stop is not None else -1
            _stop2 = _slice2.stop if _slice2.stop is not None else -1
            if _stop1 < 0 or _stop2 < 0:
                raise ValueError(
                    "Cannot merge ROIs with negative indices. "
                    "Please change indices to positive numbers."
                )
            _stop = min(_slice1.start + _stop2 * _step1, _stop1)
            _roi.append(slice(_start, _stop, _step))
        self._roi = tuple(_roi)

    def create_roi_slices(self):
        """
        Create new ROI slice objects from the stored (keyword) arguments.
        """
        if self._roi_key is None:
            self._roi = None
            return
        self._check_types_roi_key()
        self._check_types_roi_key_entries()
        self._convert_str_roi_key_entries()
        self._check_length_of_roi_key_entries()
        self._convert_roi_key_to_slice_objects()
        if self.input_shape is not None:
            self._modulate_roi_keys()

    def _check_types_roi_key(self):
        """
        Check the type of the ROI and convert if required.

        Raises
        ------
        ValueError
            If the ROI is not a list or tuple.
        """
        if self._roi_key is None:
            return
        if isinstance(self._roi_key, str):
            self._convert_str_roi_key()
        elif isinstance(self._roi_key, (list, tuple)):
            self._roi_key = list(self._roi_key)
        else:
            raise ValueError(error_msg(self._roi_key, "Not of type (list, tuple)."))

    def _convert_str_roi_key(self):
        """
        Convert a string ROI key to a list of entries and strip any leading
        and trailing brackets and empty characters.
        """
        self._strip_string_roi_key()
        self._roi_key = [item.strip() for item in self._roi_key.split(",")]

    def _strip_string_roi_key(self):
        """
        Strip a ROI key of type string of any leadind and trailing chars which
        do not belong (i.e. brackets, spaces etc.)
        """
        _tmpstr = self._roi_key
        _valid_chars = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "-"]
        # strip leading chars:
        while True:
            if _tmpstr[0] in _valid_chars + ["s"]:
                break
            _tmpstr = _tmpstr[1:]
        # strip trailing chars:
        while True:
            if _tmpstr[-1] in _valid_chars or (
                _tmpstr[-1] == ")" and _tmpstr.count(")") == _tmpstr.count("slice(")
            ):
                break
            _tmpstr = _tmpstr[:-1]
        self._roi_key = _tmpstr

    def _check_types_roi_key_entries(self):
        """
        Check that only integer and slice objects are present in the roi_key.

        For convenience, strings are parsed and converted.

        Raises
        ------
        ValueError
            If datatypes apart from integer and slice are encountered.
        """
        roi_dtypes = {
            (Integral if issubclass(type(e), Integral) else type(e))
            for e in self._roi_key
        }
        roi_dtypes.discard(Integral)
        roi_dtypes.discard(slice)
        roi_dtypes.discard(str)
        roi_dtypes.discard(type(None))
        if roi_dtypes != set():
            _msg = error_msg(
                self._roi_key, "Non-integer, non-slice datatypes encountered."
            )
            raise ValueError(_msg)

    def _convert_str_roi_key_entries(self):
        """
        Check the roi_key for string entries and parse these.

        This method will look for "slice" entries and parse these with start,
        stop (and optional step). Integers will be returned directly.

        Raises
        ------
        ValueError
            If the conversion of the string to a slice or interger object
            was not sucessful.
        """
        _tmpkeys = copy.copy(self._roi_key)
        _newkeys = []
        try:
            while len(_tmpkeys) > 0:
                key = _tmpkeys.pop(0)
                if isinstance(key, (Integral, slice, type(None))):
                    _newkeys.append(key)
                    continue
                if key.startswith("slice("):
                    _start = int(key[6:])
                    _end = _tmpkeys.pop(0)
                    if _end.endswith(")"):
                        _step = None
                        _end = _end.strip(")")
                    else:
                        _step = _tmpkeys.pop(0).strip(")")
                        _step = int(_step) if _step != "None" else None
                    _newkeys.append(slice(_start, int(_end), _step))
                else:
                    _newkeys.append(int(key))
        except ValueError as _ve:
            raise ValueError(error_msg(self._roi_key, _ve)) from _ve
        self._roi_key = _newkeys

    def _check_length_of_roi_key_entries(self):
        """
        Verify that the length of the entries is correct to create 2 slice
        objects.

        Raises
        ------
        ValueError
            If the length of the items does not allow the creation of two
            slice objects.
        """
        _n = 0
        for key in self._roi_key:
            if isinstance(key, (Integral, type(None))):
                _n += 1
            elif isinstance(key, slice):
                _n += 2
        if _n != 2 * self._ndim:
            _msg = error_msg(
                self._roi_key, "The input does not have the correct length."
            )
            raise ValueError(_msg)

    def _convert_roi_key_to_slice_objects(self):
        """
        Convert the roi_key to slice objects.

        Raises
        ------
        ValueError
            If the conversion does not succeed.
        """
        _roi = copy.copy(self._roi_key)
        _out = []
        for _dim in range(1, self._ndim + 1):
            try:
                if isinstance(_roi[0], (Integral, type(None))) and isinstance(
                    _roi[1], (Integral, type(None))
                ):
                    _index0 = _roi.pop(0)
                    _index0 = _index0 if _index0 is not None else 0
                    _index1 = _roi.pop(0)
                    _out.append(slice(_index0, _index1))
                elif isinstance(_roi[0], slice):
                    _out.append(_roi.pop(0))
                else:
                    _msg = error_msg(
                        self._roi_key,
                        f"Cannot create the slice object for dimension {_dim}.",
                    )
                    raise ValueError(_msg)
            except ValueError as _ve:
                raise ValueError(error_msg(self._roi_key, _ve)) from _ve
        self._roi = tuple(_out)

    def _modulate_roi_keys(self):
        """
        Modulate the ROI keys by the input shape to remove negative
        indices and limit it to the image dimensions.
        """

        def apply_neg_mod(value, modulo, start=True):
            if value is None:
                return (not start) * modulo
            if value >= modulo:
                value = modulo
            elif value < 0:
                value = mod(value, modulo)
            return value

        _new_roi = []
        for _axis in range(self._ndim):
            _mod = self.input_shape[_axis]
            _start = apply_neg_mod(self._roi[_axis].start, _mod, True)
            _step = self._roi[_axis].step
            _stop = apply_neg_mod(self._roi[_axis].stop, _mod, False)
            _new_roi.append(slice(_start, _stop, _step))
        self._roi = tuple(_new_roi)
