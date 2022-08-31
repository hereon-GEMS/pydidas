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
The menu_utils module includes functions used in the pydidas main_menu.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ["find_toolbar_bases"]

import os


def find_toolbar_bases(items):
    """
    Find the bases of all toolbar items which are not included in the items
    itself.

    Base levels in items are separated by forward slashes.

    Parameters
    ----------
    items : Union[list, tuple]
        An iterable of string items.

    Example
    -------
    >>> items = ['a', 'a/b', 'a/c', 'b', 'd/e']
    >>> _find_toolbar_bases(items)
    ['', 'a', 'd']

    The '' entry is the root for all top-level items. Even though 'a' is an
    item itself, it is also a parent for 'a/b' and 'a/c' and it is therefore
    also included in the list, similar to 'd'.

    Returns
    -------
    itembases : list
        A list with string entries of all the items' parents.
    """
    _itembases = []
    for _item in items:
        _parent = os.path.dirname(_item)
        if _parent not in _itembases:
            _itembases.append(_parent)
        _item = _parent
    _itembases.sort()
    return _itembases
