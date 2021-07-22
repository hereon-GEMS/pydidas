# This file is part of pydidas.

# pydidas is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# Foobar is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with Foobar.  If not, see <http://www.gnu.org/licenses/>.

"""String formatting tools."""

import numpy as np

__all__ = ['format_str']


def format_str(obj, length, fill_back=True, fill_char='.', formatter='{:.3f}',
               final_space=True):
    """
    Format an input object to a string of defined length.

    Numerical objects (integer, float) will be converted to a string with
    the formatter defined in the call, input strings will be processed
    as they are.
    If the string is shorter than the required length, it will be filled with
    chars defined in the call, either in the front or back.

    Parameters
    ----------
    string : str
        The input string to be formatted.
    length : int
        The length of the output string.
    fill_back: bool, optional
        Keyword to toggle filling the front or end.
        The default is True (filling the end of the string).
    fill_char : char, optional
        The character used for filling the string. Note that if a string is
        padded, a space is always preserved between the padding and the input.
        The default is '.'.
    final_space: bool, optional
        A keyword to add a final space to the return string. This will be
        within the length defined in the input parameter. The default is True.

    Returns
    -------
    str
        The formatted string.
    """
    if len(fill_char) != 1:
        raise TypeError('fill_char must be exactly one character.')
    if type(obj) in [int, np.uint8, np.uint8, np.int16, np.uint16,
                     np.int32, np.uint32, np.int64, np.uint64,
                     float, np.float32, np.float64, bool]:
        obj = formatter.format(obj)
    elif type(obj) in [list, dict, tuple, set]:
        obj = repr(obj)
    elif type(obj) == str:
        pass
    else:
        raise TypeError(f'Cannot convert object of type {type(obj)} to '
                        'string.')
    if len(obj) + final_space >= length:
        return obj[:length - final_space] + ' ' * final_space
    _n = length - len(obj) - 1 - final_space
    return (_n * fill_char * (not fill_back)
            + ' ' * (not fill_back)
            + obj
            + ' ' * (fill_back)
            + _n * fill_char * (fill_back)
            + ' ' * final_space)
