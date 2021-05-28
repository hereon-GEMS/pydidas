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

"""Module with filter functions to crawl hdf5 files / groups and determine
a list of all dataset keys which fulfill certain filter criteria."""

__author__      = "Malte Storm"
__copyright__   = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "MIT"
__version__ = "0.0.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['hdf5_dataset_check', 'get_hdf5_populated_dataset_keys',
           'get_hdf5_dataset_shape']

import os
import pathlib
import h5py
import hdf5plugin


def hdf5_dataset_check(item, minDataSize=50, minDataDim=3, ignoreList=()):
    """
    Check if an h5py item is a dataset which corresponds to the filter
    criteria.

    This function checks if an item is an instance of :py:class:`h5py.Dataset`
    and if it fulfills the defined filtering criteria for minimum data size,
    minimum data dimensionality and and filtered keys.


    Parameters
    ----------
    item : object
        This is the object to be checked for being an instance of
        :py:class:`h5py.Dataset`.
    minDataSize : int, optional
        The minimum data size of the item. This is the total size of the
        dataset, not the size along any one dimension. The default is 50.
    minDataDim : int, optional
        The minimum dimensionality of the item. The default is 3.
    ignoreList : Union[list, tuple], optional
        A list or tuple of strings. If the dataset key starts with any
        of the entries, the dataset is ignored. The default is ().

    Returns
    -------
    bool
        The result of the check: Is the item an :py:class:`h5py.Dataset`
        and fulfills the requirements of minimum data size and dimensionality
        and does not start with any keys specified in the ignoreList?
    """
    if (isinstance(item, h5py.Dataset)
            and len(item.shape) >= minDataDim
            and item.size >= minDataSize
            and not item.name.startswith(tuple(ignoreList))):
        return True
    return False


def get_hdf5_dataset_shape(fname, dset=None):
    """
    Get the shape of an hdf5 dataset.

    This function will return the shape of an hdf5 dataset. Input can be given
    either with file name and dataset parameters or using the hdf5
    nomenclature with <filename>://</dataset> (note the total of 3 slashes).

    Parameters
    ----------
    fname : Union[str, pathlib.Path]
        The filepath or path to filename and dataset.
    dset : str, optional
        The optional dataset key, if not specified in the fname.
        The default is None.

    Raises
    ------
    KeyError
        If the dataset has not been specified.
    TypeError
        If fname is not of type str or pathlib.Path.

    Returns
    -------
    shape : tuple
        The shape of the dataset.

    """
    if dset is not None:
        _dset = dset
    if not isinstance(fname, (str, pathlib.Path)):
        raise TypeError('The path must be specified as string or pathlib.Path')

    if isinstance(fname, pathlib.Path):
        fname = str(fname)

    if fname.find('://') > 0:
        _fname, _dset = fname.split('://')
    else:
        _fname = fname

    if _dset is None:
        raise KeyError('No dataset specified. Cannot determine shape.')

    with h5py.File(_fname, 'r') as f:
        shape = f[_dset].shape
    return shape


def get_hdf5_populated_dataset_keys(item, minDataSize=50, minDataDim=3,
                                    itemFileRef=None,
                                    ignoreKeys=None):
    """
    Get the dataset keys of all datasets that match the conditions.

    Function which crawls through the full tree of a hdf5 file and finds
    all datasets which correspond to the search criteria. Allowed input items
    are h5py Files, Groups and Datasets as well as strings. If a string is
    passed, the function will open a :py:class:`h5py.File` object and close
    it after traversal. If an open h5py object is passed, this object will
    not be closed on return of the function.

    Parameters
    ----------
    item : Union[str, h5py.File, h5py.Group, h5py.Dataset]
        The item to be checked recursively. A str will be interpreted as
        filepath to the hdf5 file.
    minDataSize : int, optional
        A minimum size which datasets need to have. Any integers between 0
        and 1,000,000,000 are acceptable. The default is 50.
    minDataDim : int, optional
        The minimum dimensionality of the dataset. Allowed entries are
        between 0 and 3. The default is 3.
    itemFileRef : h5py.File reference, optional
        A reference to the base hdf5 file. This information is used to
        detect external datasets. If not specified, this information will
        be queried from the base calling parameter >item>. The default is None.
    ignoreKeys : Union[list, None], optional
        Dataset keys (or snippets of key names) to be ignored. Any keys
        starting with any of the items in this list are ignored.
        The default is None.

    Raises
    ------
    KeyError
        If any Groups are links to external files, a KeyError is raised
        because h5py cannot get the reference name attributes from these
        keys but returns the name keys in the external file which does not
        allow to open these datasets.

    Returns
    -------
    list
        A list with all dataset keys which correspond to the filter criteria.
    """
    _close_on_exit = False
    _ignore = ignoreKeys if ignoreKeys is not None else []
    _datasets = []

    if isinstance(item, (str, pathlib.Path)):
        if os.path.exists(item):
            item = h5py.File(item, 'r')
            _close_on_exit = True

    if itemFileRef is None:
        itemFileRef = item.file

    if hdf5_dataset_check(item, minDataSize, minDataDim, _ignore):
        return [item.name]
    elif isinstance(item, h5py.Dataset):
        return []

    if isinstance(item, (h5py.File, h5py.Group)):
        for key in item:
            _item = item[key]
            # add a check to filter external datasets. These are referenced
            # by their .name in the external datafile, not the current file.
            if itemFileRef != _item.file:
                if hdf5_dataset_check(_item, minDataSize, minDataDim, _ignore):
                    _datasets += [f'{item.name}/{key}']
                elif isinstance(_item, (h5py.File, h5py.Group)):
                    raise KeyError('External link to hdf5.Group detected: '
                                   f'"{item.name}/{key}"'
                                   ' Cannot follow the link. Aborting ...')
            else:
                _datasets += (
                    get_hdf5_populated_dataset_keys(
                        item[key], minDataSize, minDataDim,
                        itemFileRef=itemFileRef, ignoreKeys=_ignore))
    if _close_on_exit:
        item.close()
    return _datasets
