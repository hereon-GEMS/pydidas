# MIT License
#
# Copyright (c) 2021 Malte Storm, HZG
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

"""File input and output related routines."""

import os

__all__ = ['file_is_writable']

def file_is_writable(filename, overwrite=False):
    """
    Check whether a file exists and the file is writable.

    If the filename does not exist, the function checks whether write
    permissions are granted for the directory in which the file would
    be created.

    Parameters
    ----------
    filename : str
        The filename of the file to be checked.
    overwrite: bool
        Keyword to allow overwriting of existing files. Default: False

    Returns
    -------
    bool
        True if file exists and is writeable and overwrite or
        directory is writable. False in other cases.
    """
    #check for existing files:
    if (os.path.isfile(filename) and os.access(filename, os.W_OK) and
        overwrite):
        return True
    elif os.path.isfile(filename):
        return False

    #check if directory is writable:
    if not os.path.isdir(filename):
        filename = os.path.dirname(filename)

    #if directory, check if writable:
    if os.path.isdir(filename) and os.access(filename, os.W_OK):
        return True
    return False
