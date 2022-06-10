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
Module with utility functions required for the Dataset class.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ["get_number_of_entries", "get_axis_item_representation"]

import textwrap
from collections.abc import Iterable
from numbers import Integral


import numpy as np


def get_number_of_entries(obj):
    if isinstance(obj, np.ndarray):
        return obj.size
    elif isinstance(obj, Integral):
        return 1
    elif isinstance(obj, Iterable):
        return len(obj)
    raise ValueError(f"Cannot calculate the number of entries for type {type(obj)}.")


def get_axis_item_representation(key, item, use_key=True):
    """
    Get a string representation for a dictionary item of 'axis_labels',
    'axis_ranges' or 'axis_units'

    Parameters
    ----------
    key : str
        The key (i.e. reference name) for the item.
    item : object
        The item to be represented as a string.
    use_key : bool, optional
        Keyword to print the key name in front of the values. The default
        is True.

    Returns
    -------
    list
        A list with a representation for each line.
    """
    _repr = (f"{key}: " if use_key else "") + item.__repr__()
    if isinstance(item, np.ndarray):
        _repr = _repr.replace("\n      ", "")
        _lines = textwrap.wrap(
            _repr, initial_indent="", width=75, subsequent_indent=" " * 10
        )
        _i0 = _lines[0].find(",")
        for _index in range(1, len(_lines)):
            _ii = _lines[_index].find(",")
            _lines[_index] = " " * (_i0 - _ii) + _lines[_index]
    else:
        _lines = textwrap.wrap(
            _repr, initial_indent="", width=75, subsequent_indent=" " * 3
        )
    return _lines
