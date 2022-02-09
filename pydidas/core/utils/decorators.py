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
The decorator module has useful decorators to facilitate coding.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.1.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['copy_docstring']

import functools


def copy_docstring(origin):
    """
    Decorator to initialize the docstring from another source.

    This is useful to duplicate a docstring for inheritance and composition.

    If origin is a method or a function, it copies its docstring.
    If origin is a class, the docstring is copied from the method
    of that class which has the same name as the method/function
    being decorated.

    Parameters
    ----------
    origin : object
        The origin object with the docstring.

    Raises
    ------
    ValueError
        If the origin class does not have the method with the same name.
    """
    def _docstring(dest, origin):
        if not isinstance(dest, type) and isinstance(origin, type):
            try:
                origin = getattr(origin, dest.__name__)
            except AttributeError:
                raise ValueError('Origin class has no method called '
                                 f'{dest.__name__}')

        dest.__doc__ = origin.__doc__
        return dest
    return functools.partial(_docstring, origin=origin)
