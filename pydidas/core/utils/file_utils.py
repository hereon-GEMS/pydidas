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
Module with file utility functions pertaining to generic names.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.1.1"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['trim_filename', 'find_valid_python_files']

import os

from .flatten_list_ import flatten_list


def trim_filename(path):
    """
    Trim a filename from a path if present.

    Parameters
    ----------
    path : str
        The file system path, including eventual filenames.

    Returns
    -------
    path : str
        The path without the filename.
    """
    path = os.path.dirname(path) if os.path.isfile(path) else path
    if os.sep == '/':
        path.replace('\\', os.sep)
    else:
        path.replace('/', os.sep)
    return path


def find_valid_python_files(path):
    """
    Search for all python files in path and subdirectories.

    This method will search the specified path recursicely for all
    python files, defined as files with a .py extension.
    It will ignore protected files /directories (starting with "__")
    and hidden files / directories (starting with ".").

    Parameters
    ----------
    path : str
        The file system path to search.

    Returns
    -------
    list
        A list with the full filesystem path of python files in the
        directory and its subdirectories.
    """
    if path is None or not os.path.exists(path):
        return []
    path = trim_filename(path)
    _entries = [os.path.join(path, item) for item in os.listdir(path)
                if not (item.startswith('__') or item.startswith('.'))]
    _dirs = [item for item in _entries if os.path.isdir(item)]
    _files = [item for item in _entries if os.path.isfile(item)]
    _results = flatten_list(
        [find_valid_python_files(os.path.join(path, entry))
         for entry in _dirs])
    _results += [f for f in _files if f.endswith('.py')]
    return _results
