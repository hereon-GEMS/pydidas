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

"""Module with generic utiliy functions."""

__author__      = "Malte Storm"
__copyright__   = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.0.1"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = []

import itertools
import time
import os
import sys
import tempfile
from os.path import join as osjoin
from os.path import dirname, isfile

from numpy import floor

def flatten_list(nested_list):
    """
    Flatten a nested list.

    This function will flatten any nested list.

    Parameters
    ----------
    nested_list : list
        A list with arbitrary nesting.

    Returns
    -------
    list
        The flattened list.
    """
    return list(itertools.chain.from_iterable(nested_list))

def update_separators(path):
    """
    Check the separators and update to os.sep if required.

    Parameters
    ----------
    path : str
        The file path to be checked

    Returns
    -------
    str
        The path with separators updated to os.sep standard.
    """
    if sys.platform in ['win32', 'win64']:
        return path.replace('/', os.sep)
    return path.replace('\\', os.sep)


def get_pydidas_module_dir(path):
    """
    Find the pydidas module directory searching from the input directory.

    Parameters
    ----------
    path : str
        The name of the directory / file acting as starting point for the
        search.

    Returns
    -------
    str
        The path to the pydidas module.
    """
    path = update_separators(os.path.dirname(path) if isfile(path) else path)
    if len(path) == 0:
        raise IOError('No path given')
    p = path.split(os.sep)
    while len(p) > 0:
        for i_pydidas in range(3):
            _ptmp = p + ['pydidas'] * i_pydidas
            _tmppath = os.sep.join(_ptmp)
            if (_ptmp[-1] == 'pydidas' and
                    isfile(osjoin(_tmppath, '__init__.py'))):
                return dirname(_tmppath)
        p.pop(-1)
    raise FileNotFoundError('Could not locate pydidas init file in path '
                            f'"{path}" or subdirectories')


def get_time_string(epoch=None, humanReadable=True):
    """
    Get a formatted time string.

    This function creates a readable time string from an epoch time. If no
    epoch time is specified, the current time will be used.
    By using the "skipSpecChars" flag, the output can be formatted without
    any separators and special characters, for example for using it for
    file names.

    Parameter
    ---------
    epoch : Union[None, float]
        The time in epoch. If None, the current system time will be used.
        The default is None.
    humanReadable : bool, optional
        Flag to create human-readable format with special separation characters
        (":" and "/"). If False, the output items will not be separated by
        separators (e.g. for filenames). The default is True.

    Returns
    -------
    str
        Formatted date and time string
        (if humanReadable: YYYY/MM/DD HH:MM:ss.sss;
         else: YYYYMMDD__HHMMss)
    """
    if epoch is None:
        epoch = time.time()
    _time = time.localtime(epoch)
    _sec = _time[5] + epoch - floor(epoch)
    if humanReadable:
        return ('{:04d}/{:02d}/{:02d} {:02d}:{:02d}:{:06.3f}'
                ''.format(_time[0], _time[1], _time[2], _time[3], _time[4],
                          _sec))
    return ('{:04d}{:02d}{:02d}_{:02d}{:02d}{:02.0f}'
            ''.format(_time[0], _time[1], _time[2], _time[3], _time[4], _sec))
