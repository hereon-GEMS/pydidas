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

"""
The str_utils module has convenience functions for string formatting.
"""

__author__      = "Malte Storm"
__copyright__   = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.0.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"

import time
from numbers import Real
import numpy as np

__all__ = ['format_str', 'get_time_string', 'get_short_time_string',
           'timed_print', 'get_warning']


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
    formatter : str, optional
        The formatter to convert numbers to strings. The default is "{:.3f}".
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
    if Real.__subclasscheck__(type(obj)):
        obj = formatter.format(obj)
    if not isinstance(obj, str):
        obj = repr(obj)
    if len(obj) + final_space >= length:
        return obj[:length - final_space] + ' ' * final_space
    _n = length - len(obj) - 1 - final_space
    return (_n * fill_char * (not fill_back)
            + ' ' * (not fill_back)
            + obj
            + ' ' * (fill_back)
            + _n * fill_char * (fill_back)
            + ' ' * final_space)


def get_time_string(epoch=None, human_output=True):
    """
    Return a formatted time string.

    This function creates a string output of a time in the format
    (YYYY/MM/DD HH:MM:ss.sss). If no epoch-time is specified, the current
    system time will be used.

    Parameters
    ----------
    epoch : Union[float, None]
        Keyword to process an epoch input. If None, the current
        system time will be used. The default is None.

    human_output : bool, optional
        Keyword to control special  separation characters. If True, the
        output will be human-readable friendly (with special sep. chars).
        If False, only a "_" will be included between the date and time.
        The default is True.

    Returns
    -------
    str :
        The formatted date and time string.
        If human-readible: (YYYY/MM/DD HH:MM:ss.sss)
        Else: YYYYMMDD_HHMMss
    """
    if epoch is None:
        epoch = time.time()
    _time = time.localtime(epoch)
    _sec = _time[5] + epoch - np.floor(epoch)
    if human_output:
        return (
            '{:04d}/{:02d}/{:02d} {:02d}:{:02d}:{:06.3f}'
            ''.format(_time[0], _time[1], _time[2], _time[3], _time[4], _sec))
    return ('{:04d}{:02d}{:02d}_{:02d}{:02d}{:02.0f}'
            ''.format(_time[0], _time[1], _time[2], _time[3], _time[4], _sec))


def get_short_time_string(epoch=None):
    """
    Return a short time string in the format (DD/MM HH:MM:ss)

    Parameters
    ----------
    epoch : Union[float, None]
        Keyword to process an epoch input. If None, the current
        system time will be used. The default is None.

    Returns
    -------
    str :
        Formatted date and time string (DD/MM HH:MM:ss)
    """
    return get_time_string(epoch)[5:-4]

def timed_print(string, new_lines=0, verbose=True):
    """
    Print a string with a time prefix.

    This function prints a time prefix in the format YYYY/MM/DD HH:MM:ss.sss
    and the input string. If new_lines > 0, a number of new lines will be
    printed before the output is returned.

    Parameters
    ----------
    string : str
        The input string to be printed.

    new_lines : int, optional
        The number of preceding empty lines. The default is 0.

    verbose : bool, optinoal
        Keyword to "mute" the output, i.e. prevent any text to be printed.
        If True, the output will be printed, if False, this function will
        do nothing. The default is True.
    """
    if verbose:
        print('{}{}: {}'.format('\n' * new_lines, get_time_string(), string))


def get_warning(string, severe=False, new_lines=0, print_warning=True,
                get_warning=False):
    """
    Generate a warning message (formatted string in a "box" of dashes).

    This function will create a warning string and add a box of dashes around
    it. The output to sys.stdout can be controlled with "print_warning" and
    the formatted string can be returned with the "get_warning" keyword.

    Parameters
    ----------
    string : Union[str, list, tuple]
        The input string to be formatted. A multi-line string can be passed
        as a list or tuple of strings.
    severe : boo, optional
        Keyword to add an additional frame of double dashes. The default is
        False.
    new_lines : int, optional
        The number of preceding empty lines. The default is 0.
    print_warning : bool, optional
        Keyword to print the warning to sys.stdout. The default is True.
    get_warning: bool, optional
        Keyword to get the formatted string as return argument. The default
        is False.

    Returns
    -------
    Union[None, str]
        If "get_warning" is True, the function returns the formatted string.
        Else, it will return None.
    """
    if isinstance(string, str):
        _max = len(string)
        string = [string]
    elif isinstance(string, (list, tuple)):
        _max = np.amax(np.r_[[len(_s) for _s in string]])
    _length = 60 if _max <= 54 else 80
    _s = ('\n' * new_lines
          + severe * ('=' * _length + '\n')
          + '-' * _length + '\n')
    for item in string:
        ll = len(item)
        if ll == 0:
            _s += '-' * _length + '\n'
        elif ll <= 77:
            _filler =  '-' * (_length - ll - 3)
            _s += f'- {item} {_filler}\n'
        else:
            _s += f'- {item[:73]}[...]\n'
    _s += '-' * _length + severe * ('\n' +  '=' * _length)
    if print_warning:
        print(_s)
    if get_warning:
        return _s
    return None
