# This file is part of pydidas
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
# along with pydidas If not, see <http://www.gnu.org/licenses/>.

"""
Module with the DataBrowsingFrame which is used to browse through the filesystem in a
dedicated filesystem tree and show file data in a view window.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["DataBrowsingFrame"]


from pathlib import Path
from typing import Union

import h5py
import numpy as np
from qtpy import QtCore
from silx.gui.data.DataViews import IMAGE_MODE, PLOT1D_MODE, RAW_MODE
from silx.gui.hdf5 import H5Node
from silx.gui.hdf5.Hdf5Item import Hdf5Item
from silx.gui.hdf5.Hdf5Node import Hdf5Node

from pydidas.core import Dataset
from pydidas.core.constants import BINARY_EXTENSIONS, HDF5_EXTENSIONS
from pydidas.core.exceptions import FileReadError
from pydidas.core.utils import CatchFileErrors, get_extension
from pydidas.data_io import IoManager, import_data
from pydidas.gui.frames.builders.data_browsing_frame_builder import (
    create_splitter,
    get_widget_creation_information,
)
from pydidas.widgets.framework import BaseFrame
from pydidas.widgets.windows import Hdf5BrowserWindow
from pydidas_qtcore import PydidasQApplication


class DataBrowsingFrame(BaseFrame):
    """
    A class to browse the filesystem tree and display data.

    The DataBrowsingFrame is frame with a directory explorer
    and a main data visualization window. Its main purpose is to browse
    through datasets.
    """

    menu_icon = "pydidas::frame_icon_data_browsing"
    menu_title = "Data browsing"
    menu_entry = "Data browsing"

    def __init__(self, **kwargs: dict):
        BaseFrame.__init__(self, **kwargs)
        self.__qtapp = PydidasQApplication.instance()
        self.__supported_extensions = set(IoManager.registry_import.keys())
        self.__current_filename = None
        self.__open_file = None
        self.__hdf5node = Hdf5Node()
        self.__browser_window = None

    def connect_signals(self):
        """
        Connect all required signals and slots between widgets and class
        methods.
        """
        self._widgets["explorer"].sig_new_file_selected.connect(self.__file_selected)
        self._widgets["explorer"].sig_new_file_selected.connect(
            self._widgets["raw_metadata_selector"].new_filename
        )
        self._widgets["hdf5_dataset_selector"].sig_new_dataset_selected.connect(
            self.__display_hdf5_dataset
        )
        self._widgets["raw_metadata_selector"].sig_decode_params.connect(
            self.__display_raw_data
        )
        self._widgets["hdf5_dataset_selector"].sig_request_hdf5_browser.connect(
            self.__inspect_hdf5_tree
        )

    def build_frame(self):
        """
        Build the frame and populate it with widgets.
        """
        for _method, _args, _kwargs in get_widget_creation_information():
            _widget_creation_method = getattr(self, _method)
            _widget_creation_method(*_args, **_kwargs)
        self.add_any_widget(
            "splitter",
            create_splitter(
                self._widgets["browser"],
                self._widgets["viewer_and_filename"],
                self.width(),
            ),
        )

    @QtCore.Slot(int)
    def frame_activated(self, index: int):
        """
        Received signal that frame has been activated.

        This method is called when this frame becomes activated by the
        central widget. By default, this method will perform no actions.
        If specific frames require any actions, they will need to overwrite
        this method.

        Parameters
        ----------
        index : int
            The index of the activated frame.
        """
        BaseFrame.frame_activated(self, index)
        if index != self.frame_index and self.__browser_window is not None:
            self.__browser_window.hide()

    @QtCore.Slot(str)
    def __file_selected(self, filename: str):
        """
        Open a file after sit has been selected in the DirectoryExplorer.

        Parameters
        ----------
        filename : str
            The full file name (including directory) of the selected file.
        """
        if self.__current_filename == filename:
            return
        _extension = get_extension(filename)
        if _extension not in self.__supported_extensions:
            return
        if self.__browser_window is not None:
            self.__browser_window.hide()
        self.__check_for_and_process_hdf5_file(filename)
        self.__current_filename = filename
        self._widgets["filename"].setText(self.__current_filename)
        if _extension not in BINARY_EXTENSIONS + HDF5_EXTENSIONS:
            _data = import_data(filename)
            self.__display_dataset(_data)

    def __check_for_and_process_hdf5_file(self, filename: str):
        """
        Process the input file and check whether it is a hdf5 file.

        Parameters
        ----------
        filename : str
            The filename of the hdf5 file to open.
        """
        if self.__open_file is not None:
            self._widgets["viewer"].setData(None)
            self.__open_file.close()
            self.__open_file = None
        if get_extension(filename) not in HDF5_EXTENSIONS:
            self._widgets["hdf5_dataset_selector"].setVisible(False)
            return
        with CatchFileErrors(
            filename, KeyError, raise_file_read_error=False
        ) as catcher:
            self.__open_file = h5py.File(filename, mode="r")
            self._widgets["hdf5_dataset_selector"].new_filename(filename)
        if catcher.raised_exception:
            try:
                self.__open_file.close()
            except (OSError, AttributeError):
                pass
            self.__open_file = None
            self._widgets["hdf5_dataset_selector"].clear()
            if get_extension(self.__current_filename) in HDF5_EXTENSIONS:
                self._widgets["filename"].setText("")
            self.__current_filename = None
            raise FileReadError(catcher.exception_message)

    def __display_dataset(self, data: Union[Dataset, H5Node]):
        """
        Display the data in the viewer widget.

        Parameters
        ----------
        data : Union[Dataset, h5py.Dataset]
            The data to display.
        """
        self._widgets["viewer"].setData(data)
        if isinstance(data, (np.ndarray, H5Node, h5py.Dataset)):
            _shape = data.shape
        else:
            raise TypeError("Data type not supported.")
        _target_mode = (
            PLOT1D_MODE
            if len(_shape) == 1
            else (IMAGE_MODE if len(_shape) >= 2 else RAW_MODE)
        )
        _current_mode = self._widgets["viewer"].displayMode()
        if _target_mode != _current_mode:
            self._widgets["viewer"].setDisplayMode(_target_mode)

    @QtCore.Slot(str)
    def __display_hdf5_dataset(self, dataset: str):
        """
        Display the selected dataset in the viewer widget.

        Parameters
        ----------
        dataset : str
            The key of the dataset to display.
        """
        if dataset == "":
            self._widgets["viewer"].setData(None)
            return
        try:
            _item = Hdf5Item(
                text=dataset,
                obj=self.__open_file[dataset],
                parent=self.__hdf5node,
                openedPath=self.__current_filename,
            )
            _data = H5Node(_item)
            self.__display_dataset(_data)
        except KeyError:
            self._widgets["viewer"].setData(None)
            raise FileReadError(
                f"Dataset `{dataset}` could not be read from the file "
                f"`{Path(self.__current_filename).name}`."
            )

    @QtCore.Slot(object)
    def __display_raw_data(self, kwargs: dict):
        """
        Display the raw data in the viewer widget.

        Parameters
        ----------
        kwargs : dict
            The kwargs required for decoding the raw data.
        """
        _data = import_data(self.__current_filename, **kwargs)
        self.__display_dataset(_data)

    @QtCore.Slot()
    def __inspect_hdf5_tree(self):
        """
        Inspect the hdf5 tree structure of the current file.

        This method will open a new window with the hdf5 tree structure to display.
        """
        if self.__browser_window is None:
            self.__browser_window = Hdf5BrowserWindow()
        self.__browser_window.open_file(self.__current_filename)
