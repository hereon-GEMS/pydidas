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
Module with the RoiController class which reads arguments and creates slice
objects for ROI cropping.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['RoiController1d']

import copy

from numpy import mod

from .roi_controller import error_msg, RoiController


class RoiController1d(RoiController):
    """
    The RoiController1d is used to create slice objects to crop 1d Datasets
    with a region of interest.

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
    **roi : Union[None, tuple, dict]
        The region of interest to be used in an image. If not given at
        initialization, this value can be supplied through the .roi property.
    """

    def __init__(self, **kwargs):
        """Initialization"""
        RoiController.__init__(self, **kwargs)

    @property
    def roi_coords(self):
        """
        Get the pixel coordinates of the lower and upper boundaries of the
        ROI.

        Returns
        -------
        Union[None, tuple]
            If the ROI is not set, this property returns None. Else, it
            returns a tuple with (x_low, x_high) values.
        """
        if self._roi is None:
            return None
        return (self._roi[0].start, self._roi[0].stop)

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
            self._input_shape = (self._roi[0].stop - self._roi[0].start)
            self.create_roi_slices()
            self._merge_rois()
        except ValueError as _error:
            self._roi = self._original_roi
            raise TypeError(f'Cannot add second ROI: {_error}')
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
        _slice1 = self._original_roi[0]
        _slice2 = self._roi[0]
        _step1 = _slice1.step if _slice1.step is not None else 1
        _step2 = _slice2.step if _slice2.step is not None else 1
        _step = _step1 * _step2
        _start = _slice1.start + _step1 * _slice2.start
        _stop1 = _slice1.stop if _slice1.stop is not None else -1
        _stop2 = _slice2.stop if _slice2.stop is not None else -1
        if _stop1 < 0 or _stop2 < 0:
            raise ValueError('Cannot merge ROIs with negative indices. '
                             'Please change indices to positive numbers.')
        _stop = min(_slice1.start + _stop2 * _step1, _stop1)
        _roi.append(slice(_start, _stop, _step))
        self._roi = tuple(_roi)

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
            if isinstance(key, (int, type(None))):
                _n += 1
            elif isinstance(key, slice):
                _n += 2
        if _n != 2:
            _msg = error_msg(self._roi_key, 'The input does not have the '
                             'correct length')
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
        try:
            if (isinstance(_roi[0], (int, type(None)))
                    and isinstance(_roi[1], (int, type(None)))):
                _index0 = _roi.pop(0)
                _index0 = _index0 if _index0 is not None else 0
                _index1 = _roi.pop(0)
                _out.append(slice(_index0, _index1))
            elif isinstance(_roi[0], slice):
                _out.append(_roi.pop(0))
            else:
                _msg = error_msg(self._roi_key, 'Cannot create the slice '
                                  'object for dimension 0.')
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
        _mod = self.input_shape[0]
        _start = apply_neg_mod(self._roi[0].start, _mod, True)
        _step = self._roi[0].step
        _stop = apply_neg_mod(self._roi[0].stop, _mod, False)
        _new_roi.append(slice(_start, _stop, _step))
        self._roi = tuple(_new_roi)
