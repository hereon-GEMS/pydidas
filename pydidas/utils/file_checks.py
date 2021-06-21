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

"""Module with the CompositeCreatorApp class which allows to combine
images to mosaics."""

__author__      = "Malte Storm"
__copyright__   = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "MIT"
__version__ = "0.0.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['check_hdf_key_exists_in_file',
           'check_file_exists',
           'verify_files_in_same_directory',
           'verify_files_of_range_are_same_size']

import os
from numpy import array

from .hdf_dataset_utils import get_hdf5_populated_dataset_keys
from .._exceptions import AppConfigError


def check_hdf_key_exists_in_file(fname, key):
    """
    Veriy that the selected file has a dataset with key.

    Parameters
    ----------
    fname : str
        The filename and path.
    key : str
        The dataset key.

    Raises
    ------
    AppConfigError
        If the dataset key is not found in the hdf5 file.
    """
    dsets = get_hdf5_populated_dataset_keys(fname)
    if key not in dsets:
        raise AppConfigError(f'hdf_key "{key}" is not a valid key '
                             f'for the file "{fname}."')

def check_file_exists(fname):
    """
    Check that a file exists and raise an Exception if not.

    Parameters
    ----------
    fname : str
        The filename and path.

    Raises
    ------
    AppConfigError
        If the selected filename does not exist.
    """
    if not os.path.isfile(fname):
        raise AppConfigError(f'The selected filename "{fname}" does not '
                             'point to a valid file.')

def verify_files_in_same_directory(filename1, filename2):
    """
    Verify the first and last selected file are in the same directory.

    Parameters
    ----------
    filename1 : str
        The filename of the first file.
    filename2 : str
        The filename of the second file.

    Raises
    ------
    OSError
        If the two files are not in the same directory.
    """
    _path1, _name1 = os.path.split(filename1)
    _path2, _name2 = os.path.split(filename2)
    if _path1 != _path2:
        raise OSError(
            'The selected files are not in the same directory:\n'
            f'{filename1}\nand\n{filename2}')

def verify_files_of_range_are_same_size(path, filenames):
    """
    Verify a range of files are all the same size.

    Parameters
    ----------
    path : str
        The directory name for files in the filelist.
    filenames : list
        The list of filenames

    Raises
    ------
    AppConfigError
        If the files in the filelist are not all of the same size.
    """
    _fsizes = array([os.stat(f'{path}/{f}').st_size for f in filenames])
    if _fsizes.std() > 0.:
        raise AppConfigError('The selected files are not all of the '
                             'same size.')
