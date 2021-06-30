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
The misc module has various stand-alone functions that might be useful in
a general context.
"""
import time

import numpy as np

__all__ = ['stringFill', 'getTimeString', 'getShortTimeString',
           'timedPrint']


def stringFill(_string, _len, fill_front=False, fill_spaces=False):
    """Function to fill the string _string up to length _len
    with dots. If len(_string) > _len, the string is cropped.

    Examples:

        1. stringFill('test 123', 12)
            -->  'test 123 ...'
        2. stringFill('test 123', 12, fill_front = True)
            --> '... test 123'

    :param _string: The string to be processed
    :type _string: str

    :param _len: The length of the return string
    :type _len: int

    :param fill_front: Keyword to select whether the input should be padded
                       in front or at the back. (default: False)
    :type fill_front: bool

    :param fill_spaces: Keyword to select whether the string should be padded
                        with spaces instead of dots (default: False)
    :type fill_spaces: bool

    :return: The padded string
    :rtype: str
    """
    tmp = len(_string)
    if tmp < _len:
        if not fill_spaces:
            if fill_front:
                return (_len - tmp - 1) * '.' + ' ' + _string
            return _string + ' ' + (_len - tmp - 1) * '.'
        if fill_front:
            return (_len - tmp) * ' ' + _string
        return _string + (_len - tmp) * ' '
    return _string[:_len]
# Stringfill


def getTimeString(epoch=None, specChars=True):
    """Function to get a string output of the current time in the format
    (YYYY/MM/DD HH:MM:ss.sss)

    :param epoch: Keyword to process an epoch input. If None, the current
                  system time will be used. (default: None)
    :type epoch: None or float

    :param specChars: Keyword to control special separation characters.
                      If True, the output will be human-readable friendly.
                      (default: True)
    :type specChars: bool

    :return: Formatted date and time string (YYYY/MM/DD HH:MM:ss.sss)
    :rtype: str
    """
    if epoch is None:
        epoch = time.time()
    _time = time.localtime(epoch)
    _sec = _time[5] + epoch - np.floor(epoch)
    if not specChars:
        return ('{:04d}{:02d}{:02d}_{:02d}{:02d}{:02.0f}'
                ''.format(_time[0], _time[1], _time[2], _time[3], _time[4],
                          _sec))
    return ('{:04d}/{:02d}/{:02d} {:02d}:{:02d}:{:06.3f}'
            ''.format(_time[0], _time[1], _time[2], _time[3], _time[4], _sec))
# getTimeString


def getShortTimeString(epoch=None):
    """Function to get a string output of the current time in the format
    (DD/MM HH:MM:ss)

    :param epoch: Keyword to process an epoch input. If None, the current
                  system time will be used. (default: None)
    :type epoch: None or float

    :return: Formatted date and time string (DD/MM HH:MM:ss)
    :rtype: str
    """
    _time = time.localtime(epoch)
    return ('{:02d}/{:02d} {:02d}:{:02d}:{:02d}'
            '').format(_time[2], _time[1], _time[3], _time[4], _time[5])
# getShortTimeString


def timedPrint(_string, nLines=0, verbose=True):
    """Function to format a string with an time prefix in the format
    YYYY/MM/DD HH:MM:ss.sss

    :param _string: The input string to be printed.
    :type _string: str

    :param nLines: The number of preceding empty lines (default: 0)
    :type nLines: int

    :param verbose: If set to False, this keyword can "mute" the output,
                    i.e. prevent any text to be printed. (default: True)
    :type verbose: bool

    :return: A string printed to stdout, no return value.
    """
    if verbose:
        print('{}{}: {}'.format('\n' * nLines, getTimeString(), _string))
# timedPrint


def getWarning(s, severe=False, nLines=0, printWarning=True, getString=False):
    """Function to print a warning (formatted string in a "box" of dashes).

    :param s: input string to be formatted. A multi-line string can be passed
              as a list of strings
    :type s: str or [str, ..., str]

    :param severe: Keyword to add an additional frame of double dashes
                   (default: False)
    :type severe: bool

    :param nLines: Keyword for the number of empty lines to print before the
                   warning (default: 0)
    :type nLines: int

    printWarning : bool, optional
        Keyword to print the warning to sys.stdout. The default is True.

    getString : bool, optional
        Keyword to get the formatted string as return argument. The default
        is False.

    :return: no return value; string printed to stdout
    """
    if isinstance(s, str):
        l = len(s)
        s = [s]
    elif isinstance(s, list):
        l = np.amax(np.r_[[len(_s) for _s in s]])
    _s = '\n' * nLines
    if l <= 54:
        N = 60
    else:
        N = 80
    if severe:
        _s += '=' * N + '\n'
    _s += '-' * N + '\n'
    for li in s:
        ll = len(li)
        if ll == 0:
            _s += '-' * N + '\n'
        elif ll > 0 and (0 < l <= 54):
            _s += '--- {} {}\n'.format(li, '-' * (60 - ll - 5))
        elif 0 < ll <= 77:
            _s += '- {} {}\n'.format(li, '-' * (80 - ll - 3))
        else:
            _s += '- {}[...]\n'.format(li[:73])
    _s += '-' * N
    if severe:
        _s += '\n' +  '=' * N + '\n'
    if printWarning:
        print(_s)
    if getString:
        return _s
    return None
# printWarning
