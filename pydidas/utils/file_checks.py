# This file is part of pydidas.

# pydidas is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# Foobar is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with Foobar.  If not, see <http://www.gnu.org/licenses/>.

"""Module with the CompositeCreatorApp class which allows to combine
images to mosaics."""

__author__      = "Malte Storm"
__copyright__   = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.0.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['check_hdf5_key_exists_in_file',
           'check_file_exists',
           'verify_files_in_same_directory',
           'verify_files_of_range_are_same_size']

import os
from numpy import array

from .hdf5_dataset_utils import get_hdf5_populated_dataset_keys
from .._exceptions import AppConfigError


def check_hdf5_key_exists_in_file(fname, key):
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
