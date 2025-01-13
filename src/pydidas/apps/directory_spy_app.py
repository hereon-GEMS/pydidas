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
Module with the DirectorySpyApp which can scan directories to get the latest available
file or file of a specific pattern.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["DirectorySpyApp"]

import glob
import multiprocessing as mp
import os
from pathlib import Path
from typing import Tuple, Union

import numpy as np
from qtpy import QtCore

from pydidas.apps.parsers import directory_spy_app_parser
from pydidas.core import (
    BaseApp,
    Dataset,
    FileReadError,
    PydidasConfigError,
    UserConfigError,
    get_generic_param_collection,
)
from pydidas.core.constants import HDF5_EXTENSIONS
from pydidas.core.utils import (
    check_file_exists,
    check_hdf5_key_exists_in_file,
    get_extension,
    get_hdf5_metadata,
    pydidas_logger,
)
from pydidas.data_io import import_data


logger = pydidas_logger()


class DirectorySpyApp(BaseApp):
    """
    An App to scan a folder and load the latest image and keep it in shared memory.

    To run the app in the background, please refer to the
    :py:class:`pydidas.multiprocessing.AppRunner` documentation.

    Notes
    -----
    The full list of keyword arguments used by the DirectorySpyApp:

    scan_for_all : bool, optional
        Flag to toggle scanning for all new files or only for files matching
        the input pattern (defined with the Parameter `filename_pattern`).
        The default is False.
    filename_pattern : pathlib.Path, optional
        The pattern of the filename. Use hashes "#" for wildcards which will
        be filled in with numbers. This Parameter must be set if `scan_for_all`
        is False. The default is an empty Path().
    directory_path : pathlib.Path, optional
        The absolute path of the directory to be used. This Parameter is only
        used when `scan_for_all` is True, but it is mandatory then. The default
        is an empty Path().
    hdf5_key : Hdf5key, optional
        Used only for hdf5 files: The dataset key. The default is
        entry/data/data.
    use_det_mask : bool, optional
        Keyword to enable or disable using the global detector mask as
        defined by the global mask file and mask value. The default is True.
    detector_mask_file : Union[pathlib.Path, str], optional
        The full path to the detector mask file.
    det_mask_val : float, optional
        The display value for masked pixels. The default is 0.

    use_bg_file : bool, optional
        Keyword to toggle usage of background subtraction. The default is
        False.
    bg_file : Union[str, pathlib.Path], optional
        The name of the file used for background correction. The default is
        an empty Path.
    bg_hdf5_key : Hdf5key, optional
        Required for hdf5 background image files: The dataset key with the
        image for the background file. The default is entry/data/data
    bg_hdf5_frame : int, optional
        Required for hdf5 background image files: The image number of the
        background image in the dataset. The default is 0.

    Parameters
    ----------
    *args : tuple
        Any number of Parameters. These will be added to the app's
        ParameterCollection.
    **kwargs : dict
        Parameters supplied with their reference key as dict key and the
        Parameter itself as value.
    """

    default_params = get_generic_param_collection(
        "scan_for_all",
        "filename_pattern",
        "directory_path",
        "hdf5_key",
        "hdf5_slicing_axis",
        "use_detector_mask",
        "detector_mask_file",
        "detector_mask_val",
        "use_bg_file",
        "bg_file",
        "bg_hdf5_key",
        "bg_hdf5_frame",
    )
    parse_func = directory_spy_app_parser
    attributes_not_to_copy_to_app_clone = [
        "_shared_array",
        "_index",
        "multiprocessing_carryon",
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._det_mask = None
        self._bg_image = None
        self._fname = lambda x: ""
        self.__current_image = None
        self.__current_fname = ""
        self.__current_metadata = ""
        self.__read_image_meta = {}
        self.reset_runtime_vars()
        self._config["path"] = None
        self._config["shared_memory"] = {}
        self._config["latest_file"] = None
        self._config["2nd_latest_file"] = None
        self._config["file_hash"] = hash((None, -1, None, -1))

    def reset_runtime_vars(self):
        """
        Reset the runtime variables for a new run.
        """
        self._shared_array = None
        self._index = -1

    def multiprocessing_pre_run(self):
        """
        Perform operations prior to running main parallel processing function.
        """
        self.prepare_run()

    def prepare_run(self):
        """
        Prepare running the directory spy app.

        For the main App (i.e. running not in clone_mode), this involves the
        following steps:

            1. Get the shape of all results from the WorkflowTree and store
               them for internal reference.
            2. Get all multiprocessing tasks from the ScanContext.
            3. Calculate the required buffer size and verify that the memory
               requirements are okay.
            4. Initialize the shared memory arrays.

        Both the cloned and the main applications then initialize local numpy
        arrays from the shared memory.
        """
        self._det_mask = self._get_detector_mask()
        self.define_path_and_name()
        self.reset_runtime_vars()
        if self.get_param_value("use_bg_file"):
            self._load_bg_file()
        if not self.clone_mode:
            self.initialize_shared_memory()
        self.__initialize_array_from_shared_memory()
        if not self.get_param_value("scan_for_all"):
            self.__find_current_index()

    def _get_detector_mask(self) -> Union[None, Dataset]:
        """
        Get the detector mask from the file specified in the global QSettings.

        Returns
        -------
        _mask : Union[None, np.ndarray]
            If the mask could be loaded from a numpy file, return the mask.
            Else, None is returned.
        """
        if not self.get_param_value("use_detector_mask"):
            return None
        _mask_file = self.get_param_value("detector_mask_file")
        try:
            _mask = np.load(_mask_file)
            return _mask
        except (FileNotFoundError, ValueError, PermissionError, FileReadError):
            self.set_param_value("use_detector_mask", False)
            return None
        raise PydidasConfigError("Unknown error when reading detector mask file.")

    def define_path_and_name(self):
        """
        Define the path and the name pattern to search for files.

        Raises
        ------
        UserConfigError
            If the naming pattern could not be interpreted.
        """
        self._config["path"] = self.get_param_value("directory_path", dtype=str)
        if self.get_param_value("scan_for_all"):
            return
        _pattern_str = self.get_param_value("filename_pattern", dtype=str)
        _strs = _pattern_str.split("#")
        _lens = [len(_s) for _s in _strs]
        if len(_strs) == 1:
            raise UserConfigError(
                f"No pattern detected in the filename '{_pattern_str}'. Please verify "
                "that the hashtag has been used."
            )
        if set(_lens[1:-1]) != {0}:
            raise UserConfigError(
                "Multiple patterns detected. Cannot process the filename pattern: "
                f"'{_pattern_str}'."
            )
        _len_pattern = _pattern_str.count("#")
        self._config["glob_pattern"] = _pattern_str.replace("#" * _len_pattern, "*")
        _pattern_str = _pattern_str.replace(
            "#" * _len_pattern, "{:0" + str(_len_pattern) + "d}"
        )
        self._fname = lambda index: os.path.join(
            self._config["path"], _pattern_str
        ).format(index)

    def _load_bg_file(self):
        """
        Check the selected background image file for consistency.

        The background image file is checked and if all checks pass, the
        background image is stored.
        """
        _bg_file = self.get_param_value("bg_file")
        check_file_exists(_bg_file)
        _params = {}
        if get_extension(_bg_file) in HDF5_EXTENSIONS:
            check_hdf5_key_exists_in_file(_bg_file, self.get_param_value("bg_hdf5_key"))
            _slice_ax = self.get_param_value("hdf5_slicing_axis")
            _params = {
                "dataset": self.get_param_value("bg_hdf5_key"),
                "indices": (
                    None
                    if _slice_ax is None
                    else (
                        (None,) * _slice_ax + (self.get_param_value("bg_hdf5_frame"),)
                    )
                ),
            }
        _bg_image = import_data(_bg_file, **_params)
        if _bg_image.ndim != 2:
            raise UserConfigError(
                "The background image is not an image with 2 dimensions. Please check "
                "the configuration."
            )
        self._bg_image = self._apply_mask(_bg_image)

    def _apply_mask(self, image: np.ndarray) -> np.ndarray:
        """
        Apply the detector mask to an image.

        Parameters
        ----------
        image : np.ndarray
            The image data.

        Returns
        -------
        image : np.ndarray
            The masked image data.
        """
        if self._det_mask is None:
            return image
        _val = self.get_param_value("detector_mask_val")
        return np.where(self._det_mask, _val, image)

    def initialize_shared_memory(self):
        """
        Initialize the shared memory arrays based on the buffer size and
        the result shapes.
        """
        _share = self._config["shared_memory"]
        _share["flag"] = mp.Value("I", lock=mp.Lock())
        _share["width"] = mp.Value("I", lock=mp.Lock())
        _share["height"] = mp.Value("I", lock=mp.Lock())
        _share["metadata"] = mp.Array("c", 200)
        _share["array"] = mp.Array("f", 10000 * 10000, lock=mp.Lock())

    def __initialize_array_from_shared_memory(self):
        """
        Initialize the numpy arrays from the shared memory buffers.
        """
        self._shared_array = np.frombuffer(
            self._config["shared_memory"]["array"].get_obj(), dtype=np.float32
        ).reshape((10000, 10000))

    def multiprocessing_carryon(self) -> bool:
        """
        Wait for specific tasks to give the clear signal.

        This method will be re-implemented by the prepare_run method.

        Returns
        -------
        bool
            Flag whether processing can continue or should wait.
        """
        if self.get_param_value("scan_for_all"):
            return self.__check_for_new_file()
        return self.__check_for_new_file_of_pattern()

    def __check_for_new_file(self) -> bool:
        """
        Find the file with the last timestamp in a directory.
        """
        _files = glob.glob(self._config["path"] + os.sep + "*")
        _files = [_f for _f in _files if os.path.isfile(_f)]
        _files.sort(key=os.path.getmtime)
        _file_one = _files[-1] if len(_files) > 0 else None
        _file_two = _files[-2] if len(_files) >= 2 else None
        _new_items = self.__process_filenames(_file_one, _file_two)
        return _new_items

    def __process_filenames(self, latest: str, second_latest: str) -> bool:
        """
        Process the filenames.

        This method will take the filenames and file sizes and check whether
        any values have changed since the last call. The result of the check
        will be returned.

        Parameters
        ----------
        latest : str
            The filename of the latest file.
        2nd_latest : str
            The filename of the 2nd latest file.

        Returns
        -------
        bool
            Flag whether any changes have been detected.
        """
        _size_one = os.path.getsize(latest) if latest is not None else -1
        _size_two = os.path.getsize(second_latest) if second_latest is not None else -1
        self._config["latest_file"] = latest
        self._config["2nd_latest_file"] = second_latest
        _hash = hash((latest, _size_one, second_latest, _size_two))
        if _hash != self._config["file_hash"]:
            self._config["file_hash"] = _hash
            return True
        return False

    def __check_for_new_file_of_pattern(self) -> bool:
        """
        Find the latest file matching the defined file pattern.
        """
        while os.path.isfile(self._fname(self._index + 1)):
            self._index += 1
        if not os.path.isfile(self._fname(self._index)):
            self.__find_current_index()
        _file_one = self._fname(self._index) if self._index >= 0 else None
        _file_two = self._fname(self._index - 1) if self._index > 0 else None
        _new_items = self.__process_filenames(_file_one, _file_two)
        return _new_items

    def __find_current_index(self):
        """
        Find the current index of files matching the pattern.
        """
        _files = glob.glob(self._config["path"] + os.sep + self._config["glob_pattern"])
        _index = self._config["glob_pattern"].find("*")
        _prefix = self._config["glob_pattern"][:_index]
        _suffix = self._config["glob_pattern"][_index + 1 :]
        _files = [
            _f
            for _f in _files
            if (
                os.path.isfile(_f)
                and os.path.basename(_f).startswith(_prefix)
                and _f.endswith(_suffix)
            )
        ]
        if len(_files) == 0:
            self._index = -1
            return
        _files.sort()
        if len(_files) > 0:
            _index = (
                os.path.basename(_files[-1]).removeprefix(_prefix).removesuffix(_suffix)
            )
            self._index = int(_index)

    def multiprocessing_post_run(self):
        """
        Perform operations after running main parallel processing function.
        """

    def multiprocessing_get_tasks(self):
        """
        The DirectorySpyApp does not use tasks and will always return an empty
        list.
        """
        return []

    def multiprocessing_pre_cycle(self, index: int):
        """
        Perform operations in the pre-cycle of every task.

        Parameters
        ----------
        index : int
            The image index.
        """
        return

    def multiprocessing_func(self, index: int = -1) -> Tuple[int, str]:
        """
        Read the latest image. If the latest image cannot be read (e.g. the
        file is currently being written), the 2nd latest file will be read.

        Returns
        -------
        index : Union[int, None]
            The input index. As this parameter is not used for this app and
            only implemented for compatibility, this will generally be None
            for the DirectorySpyApp. The default is None.
        filename : str
            The full filename of the file being read
        """
        try:
            _fname = self._config["latest_file"]
            _image = self.get_image(_fname)
            if _image.shape == 0:
                raise ValueError("Empty image.")
        except (ValueError, KeyError, FileNotFoundError, FileReadError):
            try:
                _fname = self._config["2nd_latest_file"]
                _image = self.get_image(_fname)
            except (ValueError, KeyError, FileNotFoundError, FileReadError):
                raise FileReadError(
                    "Cannot read either of the last two files. Please check the "
                    "directory and filenames."
                )
        _image = self._apply_mask(_image)
        if self.get_param_value("use_bg_file"):
            _image -= self._bg_image
        self.__store_image_in_shared_memory(_image)
        return index, _fname

    def get_image(self, fname: Union[Path, str]) -> Dataset:
        """
        Get an image from the given filename.

        In case of HDF5 files, the method will always return the last frame.

        Parameters
        ----------
        fname : Union[pathlib.Path, str]
            The filename (including full path) to the image file.

        Returns
        -------
        np.ndarray
            The image.
        """
        self.__read_image_meta = {}
        if not isinstance(fname, str):
            fname = str(fname)
        if get_extension(fname) in HDF5_EXTENSIONS:
            self.__update_hdf5_metadata(fname)
        _data = import_data(fname, forced_dimension=2, **self.__read_image_meta)
        return _data

    def __update_hdf5_metadata(self, fname: str):
        """
        Get the metadata parameters to read a frame from an HDF5 file.

        Parameters
        ----------
        fname : str
            The filename (including full path) to the HDF5 file.

        Returns
        -------
        dict
            The parameters required to read the frame from the given file.
        """
        _dataset = self.get_param_value("hdf5_key")
        _shape = get_hdf5_metadata(fname, meta="shape", dset=_dataset)
        _slice_ax = self.get_param_value("hdf5_slicing_axis")
        self.__read_image_meta = {
            "indices": (
                None
                if _slice_ax is None
                else ((None,) * _slice_ax + (_shape[_slice_ax] - 1,))
            ),
            "dataset": _dataset,
            "import_pydidas_metadata": False,
        }

    def __store_image_in_shared_memory(self, image: np.ndarray):
        """
        Store the image data in the shared memory.

        Parameters
        ----------
        image : np.ndarray
            The image data
        """
        _meta = self.__get_image_metadata_string()
        _flag_lock = self._config["shared_memory"]["flag"]
        with _flag_lock.get_lock():
            _width = image.shape[1]
            _height = image.shape[0]
            self._config["shared_memory"]["width"].value = _width
            self._config["shared_memory"]["height"].value = _height
            self._config["shared_memory"]["metadata"].value = bytes(_meta, "utf-8")
            self._shared_array[:_height, :_width] = image

    def __get_image_metadata_string(self) -> str:
        """
        Get the metadata string from the metadata dictionary.

        Returns
        -------
        str
            The string representation.
        """
        if len(self.__read_image_meta) == 0:
            return ""
        return (
            f" (frame: {self.__read_image_meta['indices']}, "
            f"dataset: {self.__read_image_meta['dataset']})"
        )

    @QtCore.Slot(object, object)
    def multiprocessing_store_results(self, index: int, fname: str, *args):
        """
        Store the multiprocessing results for other pydidas apps and processes.

        Parameters
        ----------
        index : int
            The frame index. This entry is kept for compatibility and not used
            in this app.
        fname : str
            The filename
        """
        _flag_lock = self._config["shared_memory"]["flag"]
        with _flag_lock.get_lock():
            _width = self._config["shared_memory"]["width"].value
            _height = self._config["shared_memory"]["height"].value
            self.__current_image = self._shared_array[:_height, :_width]
            self.__current_fname = fname
            self.__current_metadata = self._config["shared_memory"][
                "metadata"
            ].value.decode()

    @property
    def image(self) -> np.ndarray:
        """
        Get the currently stored image.

        Returns
        -------
        np.ndarray
            The image data
        """
        return self.__current_image

    @property
    def filename(self) -> str:
        """
        Get the currently stored filename.

        Returns
        -------
        str
            The filename.
        """
        return self.__current_fname

    @property
    def image_metadata(self) -> dict:
        """
        Get the currently stored image metadata.

        For non-Hdf5 files, this will be an empty dictionary.

        Returns
        -------
        dict
            The metadata.
        """
        return self.__current_metadata
