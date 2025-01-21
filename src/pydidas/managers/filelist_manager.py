# This file is part of pydidas.
#
# Copyright 2023 - 2025, Helmholtz-Zentrum Hereon
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
Module with the FilelistManager class which is used to manage file lists
and access files based on their index.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["FilelistManager"]


import copy
import os
from pathlib import Path
from typing import Union

from pydidas.core import (
    ObjectWithParameterCollection,
    UserConfigError,
    get_generic_param_collection,
)
from pydidas.core.constants import HDF5_EXTENSIONS
from pydidas.core.utils import (
    check_file_exists,
    get_file_naming_scheme,
    verify_files_in_same_directory,
    verify_files_of_range_are_same_size,
)


class FilelistManager(ObjectWithParameterCollection):
    """
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

    def __init__(self, *args: tuple, **kwargs: dict):
        """
        Create a FilelistManager instance.
        """
        ObjectWithParameterCollection.__init__(self)
        self.add_params(*args)
        self.set_default_params()
        self.update_param_values_from_kwargs(**kwargs)
        self._config = {"file_list": [], "file_size": None, "n_files": 0}

    @property
    def n_files(self) -> int:
        """
        Get the number of files.

        Returns
        -------
        n_files : int
            The number of files in the filelist.
        """
        return self._config["n_files"]

    @property
    def filesize(self) -> float:
        """
        Get the file size of the processed files.

        Returns
        -------
        float
            The file size in bytes.
        """
        return self._config["file_size"]

    def get_config(self) -> dict:
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
        self,
        first_file: Union[None, str, Path] = None,
        last_file: Union[None, str, Path] = None,
        live_processing: Union[None, bool] = None,
        file_stepping: Union[None, int] = None,
    ):
        """
        Create a filelist with updated parameters.

        Parameters
        ----------
        first_file : Union[None, str, Path], optional
            The path to the first file. If None, the stored Parameter for
            'first_file' will be used. The default is None.
        last_file : Union[None, str, Path], optional
            The path to the last file. If None, the stored Parameter for
            'last_file' will be used. The default is None.
        live_processing : Union[None. bool], optional
            Flag for live processing (i.e. disable file system checks.)
            If None, the stored Parameter 'live_processing' will be used.
            The default is None.
        file_stepping : Union[None, int], optional
            The file stepping number. If None, the stored Parameter
            'file_stepping' will be used. The default is None.
        """
        self._update_params(first_file, last_file, live_processing, file_stepping)
        self._check_files()
        self._create_filelist()

    def _update_params(
        self,
        first_file: Union[None, str, Path] = None,
        last_file: Union[None, str, Path] = None,
        live_processing: Union[None, bool] = None,
        file_stepping: Union[None, int] = None,
    ):
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
        Check the file names and paths.

        Raises
        ------
        UserConfigError
            If any of the checks fail.
        """
        check_file_exists(self.get_param_value("first_file"))
        verify_files_in_same_directory(
            self.get_param_value("first_file"), self.get_param_value("last_file")
        )
        if (
            self.get_param_value("first_file").suffix
            != self.get_param_value("last_file").suffix
            and self.get_param_value("last_file") != Path()
        ):
            raise UserConfigError(
                "The selected files do not have the same extension. Please check the "
                "selection."
            )

    def _create_filelist(self):
        """
        Create a list of files to be processed.

        This method will select the required method based on the live_processing
        settings and the number of selected files.
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
        Check whether a second file has been selected or the selection is empty.

        Returns
        -------
        bool
            Flag whether only the first file points to a valid path.
        """
        return self.get_param_value("last_file").parent == Path()

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
        Create the list of files for static processing.

        The list of files to be processed is created based on the filenames
        of the first and last files. The directory content will be sorted
        and the first and last files names will be used to select the part
        of filesnames to be stored.
        """
        _file1 = self.get_param_value("first_file")
        _file2 = self.get_param_value("last_file")
        _list = sorted(_file1.parent.rglob(f"*{_file1.suffix}"))
        if _file2 not in _list:
            raise UserConfigError(
                f"No file with the selected name {_file2.name} exists in the directory "
                f"{_file1.parent}."
            )
        _i1 = _list.index(_file1)
        _i2 = _list.index(_file2)
        _list = _list[_i1 : _i2 + 1 : self.get_param_value("file_stepping")]
        if _file1.suffix[1:] not in HDF5_EXTENSIONS:
            verify_files_of_range_are_same_size(_list)
        self._config["file_list"] = _list
        self._config["n_files"] = len(_list)
        self._config["file_size"] = os.stat(_file1).st_size

    def _create_filelist_live_processing(self):
        """
        Create the filelist for live processing.

        This method will filter the compare the names of the first and last
        file and try to interprete the selected range.
        """
        _fnames, _range = get_file_naming_scheme(
            self.get_param_value("first_file"), self.get_param_value("last_file")
        )
        self._config["file_size"] = os.stat(self.get_param_value("first_file")).st_size
        self._config["file_list"] = [Path(_fnames.format(index=i)) for i in _range]
        self._config["n_files"] = len(_range)

    def get_filename(self, index: int) -> Path:
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
                f"the range of the file list [0, {_n - 1}]"
            )
        return self._config["file_list"][index]

    def reset(self):
        """
        Reset the filelist to the initial configuration.
        """
        self._config = {"file_list": [], "file_size": None, "n_files": 0}
