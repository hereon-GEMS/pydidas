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
Module with the flatten_list function which is a simple wrapper to get
a flatteded list from an iterable.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['flatten_list']

import itertools


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
