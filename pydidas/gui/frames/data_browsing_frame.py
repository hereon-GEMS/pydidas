# This file is part of pydidas
#
# Copyright 2023, Helmholtz-Zentrum Hereon
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
__copyright__ = "Copyright 2023, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["DataBrowsingFrame"]


from functools import partial

from qtpy import QtCore, QtWidgets

from ...core.constants import HDF5_EXTENSIONS
from ...core.utils import get_extension
from ...data_io import IoMaster, import_data
from ...widgets.framework import BaseFrame
from .builders import DataBrowsingFrameBuilder


class DataBrowsingFrame(BaseFrame):
    """
    The DataBrowsingFrame is frame with a directory explorer
    and a main data visualization window. Its main purpose is to browse
    through datasets.
    """

    menu_icon = "qta::mdi.image-search-outline"
    menu_title = "Data browsing"
    menu_entry = "Data browsing"

    def __init__(self, **kwargs: dict):
        BaseFrame.__init__(self, **kwargs)
        self.__qtapp = QtWidgets.QApplication.instance()
        self.__supported_extensions = set(IoMaster.registry_import.keys())

    def connect_signals(self):
        """
        Connect all required signals and slots between widgets and class
        methods.
        """
        self._widgets["explorer"].sig_new_file_selected.connect(self.__file_selected)
        self._widgets["but_minimize"].clicked.connect(
            partial(self.change_splitter_pos, False)
        )
        self._widgets["but_maximize"].clicked.connect(
            partial(self.change_splitter_pos, True)
        )
        self.sig_this_frame_activated.connect(
            self._widgets["viewer"].update_from_diffraction_exp
        )
        self.sig_this_frame_activated.connect(
            partial(self._widgets["viewer"].cs_transform.check_detector_is_set, True)
        )

    def build_frame(self):
        """
        Build the frame and polulate it with widgets.
        """
        DataBrowsingFrameBuilder.build_frame(self)

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
        self._widgets["hdf_dset"].setVisible(_extension in HDF5_EXTENSIONS)
        self.set_status(f"Opened file: {filename}")
        if _extension in HDF5_EXTENSIONS:
            self._widgets["hdf_dset"].set_filename(filename)
        else:
            _data = import_data(filename)
            self._widgets["viewer"].setData(_data)
