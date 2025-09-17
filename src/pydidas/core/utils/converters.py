# This file is part of pydidas.
#
# Copyright 2025, Helmholtz-Zentrum Hereon
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
Converters for generic type conversions.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = [
    "convert_to_slice",
]


from collections.abc import Iterable
from numbers import Integral
from typing import NoReturn


def convert_to_slice(entry: object) -> slice | NoReturn:
    """
    Create a slice object from the entry, if possible

    The following items can be converted to a slice:

        - None -> slice(None, None)
        - slice objects -> unchanged
        - integer objects -> slice(entry, entry + 1)
        - Iterables of two integers or None -> slice(low, high)

    Parameters
    ----------
    entry : object
        The input object.

    Returns
    -------
    slice
        The selection slice.

    Raises
    ------
    ValueError
        If the entry cannot be converted to a slice object.
    """
    if entry is None:
        return slice(None, None)
    if isinstance(entry, slice):
        return entry
    if isinstance(entry, Integral):
        return slice(entry, entry + 1)
    if isinstance(entry, Iterable) and len(entry) == 1:
        if isinstance(entry[0], Integral):
            return slice(entry[0], entry[0] + 1)
        if entry[0] is None:
            return slice(None, None)
        if isinstance(entry[0], slice):
            return entry[0]
    if (
        isinstance(entry, Iterable)
        and len(entry) == 2
        and all([_item is None or isinstance(_item, Integral) for _item in entry])
    ):
        return slice(entry[0], entry[1])
    raise ValueError(f"Could not convert the entry `{entry}` to a slice object.")
