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
Module with the FilelistManager class which is used to manage file lists
and access files based on their index.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ["FilelistManager"]

import os
import re
import copy
from pathlib import Path

import numpy as np

from ..core import (
    ObjectWithParameterCollection,
    UserConfigError,
    get_generic_param_collection,
)
from ..core.constants import FILENAME_DELIMITERS
from ..core.utils import (
    check_file_exists,
    verify_files_in_same_directory,
    verify_files_of_range_are_same_size,
    get_extension,
)


class FilelistManager(ObjectWithParameterCollection):
    """
    Inherits from :py:class:`pydidas.core.ObjectWithParameterCollection
    <pydidas.core.ObjectWithParameterCollection>`

    The FilelistManager creates and manages a file list from which to select
    items for processing.

    Any required Parameters can be supplied as arguments or with
    ``refkey=<ParameterInstance>`` as kwargs. Any Parameter not given will
    default to new instances with the default values.

    Note
    ----
    The FilelistManager uses the following generic Parameters:

    live_processing : bool, optional
        Keyword to toggle live processing which means file existance and size
        checks will be disabled in the setup process and the file processing
        will wait for files to be created (indefinitely). The default is
        False.
    first_file : pathlib.Path
        The name of the first file for a file series or of the hdf5 file in
        case of hdf5 file input.
    last_file : pathlib.Path, optional
        Used only for file series: The name of the last file to be added to
        the composite image.
    file_stepping : int, optional
        The step width (in files). A value n > 1 will only process every n-th
        image for the composite. The default is 1.

    Parameters
    ----------
    *args : tuple
        Any of the Parameters in use can be given as instances.
    **kwargs : dict
        Parameters can also be supplied as kwargs, referencey by their refkey.
    """

    default_params = get_generic_param_collection(
        "live_processing", "first_file", "last_file", "file_stepping"
    )

    def __init__(self, *args, **kwargs):
        """
        Create a FilelistManager instance.
        """
        ObjectWithParameterCollection.__init__(self)
        self.add_params(*args, **kwargs)
        self.set_default_params()
        self._config = {"file_list": [], "file_size": None, "n_files": 0}

    @property
    def n_files(self):
        """
        Get the number of files.

        Returns
        -------
        n_files : int
            The number of files in the filelist.
        """
        return self._config["n_files"]

    @property
    def filesize(self):
        """
        Get the file size of the processed files.

        Returns
        -------
        float
            The file size in bytes.
        """
        return self._config["file_size"]

    def get_config(self):
        """
        Get the full _config dictionary.

        Returns
        -------
        _config : dict
            The config dictionary with information about the file list, sizes
            and number of files.
        """
        return copy.copy(self._config)

    def update(
        self, first_file=None, last_file=None, live_processing=None, file_stepping=None
    ):
        """
        Create a filelist with updated parameters.

        Parameters
        ----------
        first_file : Union[str, Path], optional
            The path to the first file. If None, the stored Parameter for
            'first_file' will be used. The default is None.
        last_file : Union[str, Path], optional
            The path to the last file. If None, the stored Parameter for
            'last_file' will be used. The default is None.
        live_processing : bool, optional
            Flag for live processing (i.e. disable file system checks.)
            If None, the stored Parameter 'live_processing' will be used.
            The default is None.
        file_stepping : int, optional
            The file stepping number. If None, the stored Parameter
            'file_stepping' will be used.  The default is None.
        """
        self._update_params(first_file, last_file, live_processing, file_stepping)
        self._check_files()
        self._create_filelist()

    def _update_params(self, first_file, last_file, live_processing, file_stepping):
        """
        Update the internally stored Parameters if new values have been
        provided.

        Parameters
        ----------
        first_file : Union[str, None]
            The name of the first file. If None, the Parameter value will not
            be updated.
        last_file : Union[str, None]
            The name of the last file. If None, the Parameter value will not
            be updated.
        live_processing : Union[bool, None]
            Flag to enable or disable live processing. If live processing is
            True, checks for file existance and size will be performed.
            If None, the Parameter value will not be updated.
        file_stepping : Union[int, None]
            The file stepping determined which files will be processed. A value
            of n means that only every n-th file will be read. If None, the
            Parameter value will not be updated.
        """
        if first_file is not None:
            self.set_param_value("first_file", first_file)
        if last_file is not None:
            self.set_param_value("last_file", last_file)
        if live_processing is not None:
            self.set_param_value("live_processing", live_processing)
        if file_stepping is not None:
            self.set_param_value("file_stepping", file_stepping)

    def _check_files(self):
        """
        Check the file names, paths and (for hdf5 images), the size of the
        dataset with respect to the selected image numbers.

        Raises
        ------
        UserConfigError
            If any of the checks fail.
        """
        check_file_exists(self.get_param_value("first_file"))
        verify_files_in_same_directory(
            self.get_param_value("first_file"), self.get_param_value("last_file")
        )

    def _create_filelist(self):
        """
        Create a list of files to be processed. This method will select the
        required method based on the live_processing settings and the number
        of selected files.
        """
        if self._check_only_first_file_selected():
            self._create_one_file_list()
            return
        if self.get_param_value("live_processing"):
            self._create_filelist_live_processing()
        else:
            self._create_filelist_static()

    def _check_only_first_file_selected(self):
        """
        Check whether a second file has been selected or the selection is
        empty.

        Returns
        -------
        bool
            Flag whether only the first file points to a valid path.
        """
        _path2, _fname2 = os.path.split(self.get_param_value("last_file"))
        if _path2 == "":
            return True
        return False

    def _create_one_file_list(self):
        """
        Create a filelist with only one the first file.
        """
        _fullname = self.get_param_value("first_file")
        self._config["file_list"] = [_fullname]
        self._config["file_size"] = os.stat(_fullname).st_size
        self._config["n_files"] = 1

    def _create_filelist_static(self):
        """
        Create the list of files for static processing,

        The list of files to be processed is created based on the filenames
        of the first and last files. The directory content will be sorted
        and the first and last files names will be used to select the part
        of filesnames to be stored.
        """
        _path1, _fname1 = os.path.split(self.get_param_value("first_file"))
        _path2, _fname2 = os.path.split(self.get_param_value("last_file"))
        _list = sorted(os.listdir(_path1))
        _i1 = _list.index(_fname1)
        _i2 = _list.index(_fname2)
        _list = _list[_i1 : _i2 + 1 : self.get_param_value("file_stepping")]
        verify_files_of_range_are_same_size(_path1, _list)
        self._config["file_list"] = [Path(os.path.join(_path1, f)) for f in _list]
        self._config["n_files"] = len(_list)
        self._config["file_size"] = os.stat(self.get_param_value("first_file")).st_size

    def _create_filelist_live_processing(self):
        """
        Create the filelist for live processing.

        This method will filter the compare the names of the first and last
        file and try to interprete the selected range.
        """
        _fnames, _range = self._get_live_processing_naming_scheme()
        self._config["file_size"] = os.stat(self.get_param_value("first_file")).st_size
        self._config["file_list"] = [Path(_fnames.format(index=i)) for i in _range]
        self._config["n_files"] = len(_range)

    def _get_live_processing_naming_scheme(self):
        """
        Get the naming scheme for live processing files.

        This method tries to find the single difference in the filenames and
        builds a formattable string from it.

        Returns
        -------
        fnames : str
            The formattable string (keyword "index") to get the file name.
        range : range
            The range iteratable which points to all file names.
        """

        def raise_error():
            raise UserConfigError(
                "Could not interprete the filenames. The filenames do not "
                "differ in exactly one item, as determined by the delimiters."
                f'Delimiters considered are: {FILENAME_DELIMITERS.split("|")}'
            )

        _path1, _fname1 = os.path.split(self.get_param_value("first_file"))
        _fname2 = os.path.split(self.get_param_value("last_file"))[1]
        _items1 = re.split(FILENAME_DELIMITERS, os.path.splitext(_fname1)[0])
        _items2 = re.split(FILENAME_DELIMITERS, os.path.splitext(_fname2)[0])
        if len(_items1) != len(_items2) or get_extension(_fname1) != get_extension(
            _fname2
        ):
            raise_error()
        diff_index = []
        for index, item in enumerate(_items1):
            item2 = _items2[index]
            if item != item2 and len(item) == len(item2):
                diff_index.append(index)
        if len(diff_index) != 1:
            raise_error()
        diff_index = diff_index[0]
        _n = len(_items1[diff_index])
        _strindex = int(
            np.sum(np.r_[[len(_items1[index]) + 1 for index in range(diff_index)]])
        )
        _fnames = (
            _path1
            + os.sep
            + _fname1[:_strindex]
            + "{index:0"
            + f"{_n}"
            + "d}"
            + _fname1[_strindex + _n :]
        )
        _index1 = int(_items1[diff_index])
        _index2 = int(_items2[diff_index])
        return _fnames, range(_index1, _index2 + 1)

    def get_filename(self, index):
        """
        Get the filename of the image file numbered with index.

        Parameters
        ----------
        index : int
            The index of the image file.

        Raises
        ------
        UserConfigError
            If the file list is not correctly initiated or if the index is
            out of the range of the file list.

        Returns
        -------
        Path
            The filename (and path) of the image file indexed with index.
        """
        _n = self._config["n_files"]
        if not 0 <= index < _n:
            raise UserConfigError(
                f'The selected number "{index}" is out of '
                f"the range of the file list [0, {_n-1}]"
            )
        return self._config["file_list"][index]

    def reset(self):
        """
        Reset the filelist to the initial configuration.
        """
        self._config = {"file_list": [], "file_size": None, "n_files": 0}
