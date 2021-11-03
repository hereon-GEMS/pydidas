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

