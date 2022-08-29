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
Module with the DataBrowsingFrame which is used to browse data in filesystem
viewer and show it in a view window.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ["DataBrowsingFrame"]

import os
from functools import partial

from qtpy import QtCore

from ...data_io import IoMaster, import_data
from ...core.constants import HDF5_EXTENSIONS
from ...core.utils import get_extension
from .builders import DataBrowsingFrameBuilder


class DataBrowsingFrame(DataBrowsingFrameBuilder):
    """
    The DataBrowsingFrame is frame with a directory explorer
    and a main data visualization window. Its main purpose is to browse
    through datasets.
    """

    menu_icon = "qta::mdi.image-search-outline"
    menu_title = "Data browsing"
    menu_entry = "Data browsing"

    def __init__(self, parent=None, **kwargs):
        DataBrowsingFrameBuilder.__init__(self, parent, **kwargs)

    def connect_signals(self):
        """
        Connect all required signals and slots between widgets and class
        methods.
        """
        self._widgets["tree"].doubleClicked.connect(self.__file_selected)
        self._widgets["tree"].clicked.connect(self.__file_highlighted)
        self._widgets["but_minimize"].clicked.connect(
            partial(self.change_splitter_pos, False)
        )
        self._widgets["but_maximize"].clicked.connect(
            partial(self.change_splitter_pos, True)
        )
        self.sig_this_frame_activated.connect(self._widgets["viewer"].get_detector_size)
        self.sig_this_frame_activated.connect(
            partial(self._widgets["viewer"].cs_transform.check_detector_is_set, True)
        )
        self.sig_this_frame_activated.connect(
            self._widgets["viewer"]._positionWidget.update_exp_setup_params
        )

    @QtCore.Slot(bool)
    def change_splitter_pos(self, enlarge_dir=True):
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
            self._widgets["splitter"].moveSplitter(770, 1)
        else:
            self._widgets["splitter"].moveSplitter(300, 1)

    @QtCore.Slot()
    def __file_highlighted(self):
        """
        Perform actions after a file has been highlighted in the
        DirectoryExplorer.
        """
        index = self._widgets["tree"].selectedIndexes()[0]
        _name = self._widgets["tree"]._filemodel.filePath(index)
        if os.path.isfile(_name):
            _name = os.path.dirname(_name)
        self.q_settings_set_key("directory_explorer/path", _name)

    @QtCore.Slot()
    def __file_selected(self):
        """
        Open a file after sit has been selected in the DirectoryExplorer.
        """
        index = self._widgets["tree"].selectedIndexes()[0]
        _name = self._widgets["tree"]._filemodel.filePath(index)
        if not os.path.isfile(_name):
            return
        self.set_status(f"Opened file: {_name}")
        _extension = get_extension(_name)
        _supported_nothdf_ext = set(IoMaster.registry_import.keys()) - set(
            HDF5_EXTENSIONS
        )
        if _extension in HDF5_EXTENSIONS:
            self._widgets["hdf_dset"].setVisible(True)
            self._widgets["hdf_dset"].set_filename(_name)
            return
        self._widgets["hdf_dset"].setVisible(False)
        if _extension in _supported_nothdf_ext:
            _data = import_data(_name)
            self._widgets["viewer"].setData(_data)
