# MIT License
#
# Copyright (c) 2021 Malte Storm, Helmholtz-Zentrum Hereon.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""Module with generic utiliy functions."""

__author__      = "Malte Storm"
__copyright__   = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "MIT"
__version__ = "0.0.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = []


import os
import sys
import tempfile
from os.path import join as osjoin
from os.path import dirname, isfile


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
    Function to find the pydidas module directory from the input directory.

    Parameters
    ----------
    filename : str
        The filename of the file to be checked.
    overwrite : bool
        Keyword to allow overwriting of existing files. Default: False

    Returns
    -------
    bool
        True if file exists and overwrite or directory is writable.
        False in other cases.
    """
    path = update_separators(os.path.dirname(path) if isfile(path) else path)
    p = path.split(os.sep)
    if len(p) == 0:
        raise IOError('No path given')
    for i in range(1, len(p)):
        _p = os.sep.join(p[:-i])
        if p[-i] == 'tests':
            if isfile(osjoin(_p, 'pydidas', '__init__.py')):
                return _p
        elif p[-i] == 'pydidas' or 'pydidas' in os.listdir(_p):
            if isfile(osjoin(_p, '__init__.py')):
                return dirname(_p)
            if isfile(osjoin(_p, 'pydidas', 'pydidas', '__init__.py')):
                return osjoin(_p, 'pydidas')
    raise FileNotFoundError('Could not locate pydidas init file.')


def create_temp_file():
    """
    Create a temporary file and close the file handle.

    Returns
    -------
    str
        The full path to the temporary file.
    """
    _handle, _file = tempfile.mkstemp()
    os.close(_handle)
    return _file
