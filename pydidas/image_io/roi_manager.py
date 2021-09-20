# This file is part of pydidas.

# pydidas is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# Pydidas is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with Pydidas. If not, see <http://www.gnu.org/licenses/>.

"""Module with the RoiManager class which reads arguments and creates slice
objects for ROI cropping."""

__author__      = "Malte Storm"
__copyright__   = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.0.1"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['RoiManager']


import copy


def error_msg(roi, exception=''):
    """
    Get

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
        _str = _str[:-1] + f': {exception}'
    return _str


class RoiManager:
    """Generic implementation of the image reader."""

    def __init__(self, **kwargs):
        """Initialization"""
        self.__kwargs = kwargs
        self.__roi = None
        self.__roi_key = None
        self.create_roi_slices()

    @property
    def roi(self):
        """
        Get the ROI slice objects

        Returns
        -------
        tuple
            The tuple with the two slice objects to create the demanded ROI.
        """
        return self.__roi

    @roi.setter
    def roi(self, *args):
        """
        Create new ROI slice objects from the input.

        Parameters
        ----------
        *args : type
            ROI creation arguments.
        """
        self.__kwargs['ROI'] = args[0]
        self.create_roi_slices()

    def create_roi_slices(self):
        """
        Create new ROI slice objects from the stored (keyword) arguments.
        """
        self.__roi_key = self.__kwargs.get('ROI', None)
        if self.__roi_key is None:
            self.__roi = None
            return
        self.__check_types_roi_key()
        self.__check_types_roi_key_entries()
        self.__check_length_of_roi_key_entries()
        self.__convert_roi_key_to_slice_objects()

    def __check_types_roi_key(self):
        """
        Check the type of the ROI and convert if required.

        Raises
        ------
        ValueError
            If the ROI is not a list or tuple.
        """
        if self.__roi_key is None:
            return
        if isinstance(self.__roi_key, str):
            self.__convert_str_roi_key_to_list()
        if isinstance(self.__roi_key, tuple):
            self.__roi_key = list(self.__roi_key)
        if not isinstance(self.__roi_key, list):
            _msg = error_msg(self.__roi_key, 'Not of type (list, tuple).')
            raise ValueError(_msg)

    def __convert_str_roi_key_to_list(self):
        """
        Convert a string ROI key to a list of entries.
        """
        _tmpstr = self.__roi_key
        _valid_chars = ['0', '1', '2', '3', '4', '5', '6',
                        '7', '8', '9', '-']
        _index = 0
        while _index < len(_tmpstr):
            if _tmpstr[0] not in _valid_chars + ['s']:
                _tmpstr = _tmpstr[1:]
                continue
            _i_slice = _tmpstr.find('slice(', _index)
            if _i_slice == -1:
                break
            _index = _tmpstr.find(')', _index) + 1
        while len(_tmpstr) > _index:
            if _tmpstr[len(_tmpstr) - 1] in _valid_chars:
                break
            _tmpstr = _tmpstr[:-1]
        self.__roi_key = [item.strip() for item in _tmpstr.split(',')]


    def __check_types_roi_key_entries(self):
        """
        Check that only integer and slice objects are present in the roi_key.

        For convenience, strings are parsed and converted.

        Raises
        ------
        ValueError
            If datatypes apart from integer and slice are encountered.
        """
        self.__check_and_convert_str_roi_key_entries()
        roi_dtypes = {type(e) for e in self.__roi_key}
        roi_dtypes.discard(int)
        roi_dtypes.discard(slice)
        if roi_dtypes != set():
            _msg = error_msg(self.__roi_key,
                             'Non-integer, non-slice datatypes encountered.')
            raise ValueError(_msg)

    def __check_and_convert_str_roi_key_entries(self):
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
        _tmpkeys = copy.copy(self.__roi_key)
        _newkeys = []
        try:
            while len(_tmpkeys) > 0:
                key = _tmpkeys.pop(0)
                if not isinstance(key, str):
                    _newkeys.append(key)
                    continue
                if key.startswith('slice('):
                    _start = int(key[6:])
                    _end = _tmpkeys.pop(0)
                    if _end.endswith(')'):
                        _step = None
                        _end = _end.strip(')')
                    else:
                        _step = _tmpkeys.pop(0).strip(')')
                        _step = int(_step) if _step != 'None' else None
                    _newkeys.append(slice(_start, int(_end), _step))
                else:
                    _newkeys.append(int(key))
        except ValueError as _ve:
            raise ValueError(error_msg(self.__roi_key, _ve)) from _ve
        self.__roi_key = _newkeys

    def __check_length_of_roi_key_entries(self):
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
        for key in self.__roi_key:
            if isinstance(key, int):
                _n += 1
            elif isinstance(key, slice):
                _n += 2
        if _n != 4:
            _msg = error_msg(self.__roi_key, 'The input does not have the '
                             'correct length')
            raise ValueError(_msg)

    def __convert_roi_key_to_slice_objects(self):
        """
        Convert the roi_key to slice objects.

        Raises
        ------
        ValueError
            If the conversion does not succeed.
        """
        _roi = copy.copy(self.__roi_key)
        try:
            if isinstance(_roi[0], int) and isinstance(_roi[1], int):
                _out = [slice(_roi.pop(0), _roi.pop(0))]
            elif isinstance(_roi[0], slice):
                _out = [_roi.pop(0)]
            else:
                _msg = error_msg(self.__roi_key, 'Cannot create the slice '
                                 'object for dimension 0.')
                raise ValueError(_msg)
            if isinstance(_roi[0], int) and isinstance(_roi[1], int):
                _out.append(slice(_roi.pop(0), _roi.pop(0)))
            elif isinstance(_roi[0], slice):
                _out.append(_roi.pop(0))
            else:
                _msg = error_msg(self.__roi_key, 'Cannot create the slice '
                                 'object for dimension 1.')
                raise ValueError(_msg)
            self.__roi = tuple(_out)
        except ValueError as _ve:
            raise ValueError(error_msg(self.__roi_key, _ve)) from _ve
