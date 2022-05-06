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
Module with the flatten function which is a simple wrapper to get
a flatteded list from an iterable.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ["flatten", "flatten_all"]

import itertools
from collections.abc import Iterable


def flatten(nested_iterable, astype=list):
    """
    Flatten a nested iterable.

    This function will flatten any nested iterable.

    Note
    ----
    Only one level of depth will be removed and the iterable must be fully nested, i.e.
    no values must be present on the root level.

    Parameters
    ----------
    nested_iterable : list
        An iterable with nesting.
    astype : type, optional
        The return type of the flattened data, i.e. list, tuple or set. The default is
        list.

    Returns
    -------
    type
        The flattened data in the specified type.
    """
    return astype(astype(itertools.chain.from_iterable(nested_iterable)))


def flatten_all(nested_iterable, astype=list):
    """
    Flatten a nested iterable.

    This function will flatten any nested iterable

    Parameters
    ----------
    nested_iterable : list
        A list with arbitrary nesting.
    astype : type, optional
        The return type of the flattened data, i.e. list, tuple or set. The default is
        list.
    iterations : int, optional
        The number of iterations. This defines the maximum nesting level. The default
        is 1.

    Returns
    -------
    type
        The flattened data in the specified type.
    """
    _new = []
    _index = 0
    for _index, _item in enumerate(nested_iterable):
        if isinstance(_item, Iterable):
            _items = flatten_all(_item, astype=list)
            _new.extend(_items)
        else:
            _new.append(_item)
    return astype(_new)
