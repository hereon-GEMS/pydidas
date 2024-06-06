# This file is part of pydidas
#
# Copyright 2023 - 2024, Helmholtz-Zentrum Hereon
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
__copyright__ = "Copyright 2023 - 2024, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["DataBrowsingFrame"]

from functools import partial
from typing import Union

import h5py
from qtpy import QtCore
from silx.gui.data.DataViews import IMAGE_MODE, PLOT1D_MODE, RAW_MODE

from pydidas_qtcore import PydidasQApplication

from ...core import Dataset
from ...core.constants import BINARY_EXTENSIONS, HDF5_EXTENSIONS
from ...core.utils import get_extension
from ...data_io import IoMaster, import_data
from ...widgets.framework import BaseFrame
from .builders import DataBrowsingFrameBuilder


class DataBrowsingFrame(BaseFrame):
    """
    A class to browse the filesystem tree and display data.

    The DataBrowsingFrame is frame with a directory explorer
    and a main data visualization window. Its main purpose is to browse
    through datasets.
    """

    menu_icon = "qta::mdi.image-search-outline"
    menu_title = "Data browsing"
    menu_entry = "Data browsing"

    def __init__(self, **kwargs: dict):
        BaseFrame.__init__(self, **kwargs)
        self.__qtapp = PydidasQApplication.instance()
        self.__supported_extensions = set(IoMaster.registry_import.keys())
        self.__current_filename = None
        self.__open_file = None

    def connect_signals(self):
        """
        Connect all required signals and slots between widgets and class
        methods.
        """
        self._widgets["explorer"].sig_new_file_selected.connect(self.__file_selected)
        self._widgets["explorer"].sig_new_file_selected.connect(
            self._widgets["raw_metadata_selector"].new_filename
        )
        self._widgets["explorer"].sig_new_file_selected.connect(
            self._widgets["hdf5_dataset_selector"].new_filename
        )
        self._widgets["but_minimize"].clicked.connect(
            partial(self.change_splitter_pos, False)
        )
        self._widgets["but_maximize"].clicked.connect(
            partial(self.change_splitter_pos, True)
        )
        self._widgets["hdf5_dataset_selector"].sig_new_dataset_selected.connect(
            self.__display_hdf5_dataset
        )
        self._widgets["raw_metadata_selector"].sig_decode_params.connect(
            self.__display_raw_data
        )
        # self.sig_this_frame_activated.connect(
        #     self._widgets["viewer"].update_from_diffraction_exp
        # )
        # self.sig_this_frame_activated.connect(
        #     partial(
        #         self._widgets["viewer"].cs_transform_button.check_detector_is_set, True
        #     )
        # )

    def build_frame(self):
        """
        Build the frame and populate it with widgets.
        """
        DataBrowsingFrameBuilder.build_frame(self)

    def finalize_ui(self):
        """
        Finalize UI creation.
        """
        # self._widgets["hdf5_dataset_selector"].register_plot_widget(
        #     self._widgets["viewer"]
        # )
        # self._widgets["raw_metadata_selector"].register_plot_widget(
        #     self._widgets["viewer"]
        # )

    @QtCore.Slot(bool)
    def change_splitter_pos(self, enlarge_dir: bool = True):
        """
        Change the position of the window splitter to one of two predefined
        positions.

        The positions toggled using the enlarge_dir keyword.

        Parameters
        ----------
        enlarge_dir : bool, optional
            Keyword to enlarge the directory view. If False, the plot window
            is enlarged instead of the directory viewer. The default is True.
        """
        if enlarge_dir:
            self._widgets["splitter"].moveSplitter(self.__qtapp.font_height * 50, 1)
        else:
            self._widgets["splitter"].moveSplitter(self.__qtapp.font_height * 20, 1)

    @QtCore.Slot(str)
    def __file_selected(self, filename: str):
        """
        Open a file after sit has been selected in the DirectoryExplorer.

        Parameters
        ----------
        filename : str
            The full file name (including directory) of the selected file.
        """
        _extension = get_extension(filename)
        if _extension not in self.__supported_extensions:
            return
        self.set_status(f"Selected file: {filename}")
        self.__current_filename = filename
        if self.__open_file is not None:
            self.__open_file.close()
            self.__open_file = None
        if _extension in HDF5_EXTENSIONS:
            self.__open_file = h5py.File(filename, "r")
            return
        if _extension in BINARY_EXTENSIONS:
            return
        _data = import_data(filename)
        self.__display_dataset(_data)
        self._widgets["filename"].setText(self.__current_filename)

    def __display_dataset(self, data: Union[Dataset, h5py.Dataset]):
        """
        Display the data in the viewer widget.

        Parameters
        ----------
        data : Union[Dataset, h5py.Dataset]
            The data to display.
        """
        self._widgets["viewer"].setData(data)
        self._widgets["viewer"].setDisplayMode(
            PLOT1D_MODE
            if data.ndim == 1
            else (IMAGE_MODE if data.ndim >= 2 else RAW_MODE)
        )

    @QtCore.Slot(str)
    def __display_hdf5_dataset(self, dataset: str):
        """
        Display the selected dataset in the viewer widget.

        Parameters
        ----------
        dataset : str
            The key of the dataset to display.
        """
        self.__display_dataset(self.__open_file[dataset])
        self._widgets["filename"].setText(f"{self.__current_filename}::{dataset}")

    @QtCore.Slot(object)
    def __display_raw_data(self, kwargs: dict):
        """
        Display the raw data in the viewer widget.

        Parameters
        ----------
        kwargs : dict
            The kwargs required for decoding the raw data.
        """
        print(self.__current_filename, kwargs)
        _data = import_data(self.__current_filename, **kwargs)
        self.__display_dataset(_data)
        self._widgets["filename"].setText(self.__current_filename)
