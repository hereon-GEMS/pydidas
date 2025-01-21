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
Functions to flatten nested iterables of various depths.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = [
    "flatten",
    "flatten_all",
    "insert_item_in_tuple",
    "insert_items_in_tuple",
    "replace_item_in_iterable",
]


import itertools
from collections.abc import Iterable


def flatten(nested_iterable: Iterable, astype: type = list) -> object:
    """
    Flatten a nested iterable.

    This function will flatten any nested iterable.

    Note
    ----
    Only one level of depth will be removed and the iterable must be fully nested, i.e.
    no values must be present on the root level.

    Parameters
    ----------
    nested_iterable : Iterable
        An iterable with nesting.
    astype : type, optional
        The return type of the flattened data, i.e. list, tuple or set. The default is
        list.

    Returns
    -------
    astype
        The flattened data in the specified type.
    """
    return astype(itertools.chain.from_iterable(nested_iterable))


def flatten_all(nested_iterable: Iterable[Iterable], astype: type = list) -> object:
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
    for _item in nested_iterable:
        if isinstance(_item, Iterable):
            _items = flatten_all(_item, astype=list)
            _new.extend(_items)
        else:
            _new.append(_item)
    return astype(_new)


def insert_item_in_tuple(obj: tuple, index: int, item: object) -> tuple:
    """
    Insert an item into a tuple.

    Parameters
    ----------
    obj : tuple
        The original tuple
    index : int
        The index for the new item.
    item : object
        The new item to be inserted.

    Returns
    -------
    tuple
        The updated tuple.
    """
    _new = list(obj)
    _new.insert(index, item)
    return tuple(_new)


def insert_items_in_tuple(obj: tuple, index: int, *items: tuple[object]) -> tuple:
    """
    Insert iterable items into a tuple.

    Parameters
    ----------
    obj : tuple
        The original tuple
    index : int
        The index for the new item.
    item : object
        The new item to be inserted.

    Returns
    -------
    tuple
        The updated tuple.
    """
    _new = list(obj)
    return tuple(_new[:index] + list(items) + _new[index:])


def replace_item_in_iterable(obj: Iterable, index: int, item: object) -> Iterable:
    """
    Replace an item in an existing tuple.

    Parameters
    ----------
    obj : type
        The original iterable
    index : int
        The index for the new item
    item : type
        The new item to be inserted.

    Returns
    -------
    type
        The updated iterable.
    """
    _type = type(obj)
    _new = list(obj)
    del _new[index]
    _new.insert(index, item)
    return _type(_new)


def remove_item_at_index_from_iterable(obj: Iterable, index: int) -> Iterable:
    """
    Remove an item from an iterable.

    Parameters
    ----------
    obj : type
        The iterable
    index : int
        The index of the item to be removed.

    Returns
    -------
    type
        The updated iterable.
    """
    _type = type(obj)
    _new = list(obj)
    del _new[index]
    return _type(_new)
