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
__copyright__ = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.0.1"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['DataBrowsingFrame']

import os
from functools import partial

from PyQt5 import QtCore

from ..image_io import ImageReaderCollection, read_image
from ..core.constants import HDF5_EXTENSIONS
from ..widgets import BaseFrame
from .builders import DataBrowsingFrame_BuilderMixin


IMAGE_READER = ImageReaderCollection()


class DataBrowsingFrame(BaseFrame, DataBrowsingFrame_BuilderMixin):
    """
    The DataBrowsingFrame is frame with a directory exporer
    and a main data visualization window. Its main purpose is to browse
    through datasets.
    """
    def __init__(self, **kwargs):
        parent = kwargs.get('parent', None)
        BaseFrame.__init__(self, parent)
        DataBrowsingFrame_BuilderMixin.__init__(self)
        self.build_frame()
        self.connect_signals()

    def connect_signals(self):
        """
        Connect all required signals and slots between widgets and class
        methods.
        """
        self._widgets['tree'].doubleClicked.connect(self.__file_selected)
        self._widgets['tree'].clicked.connect(self.__file_highlighted)
        self._widgets['but_minimize'].clicked.connect(
        partial(self.change_splitter_pos, False))
        self._widgets['but_maximize'].clicked.connect(
            partial(self.change_splitter_pos, True))
        self.__selection_width = self._widgets['selection'].width()

    @QtCore.pyqtSlot(bool)
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
            self._widgets['splitter'].moveSplitter(770, 1)
        else:
            self._widgets['splitter'].moveSplitter(300, 1)

    @QtCore.pyqtSlot()
    def __file_highlighted(self):
        """
        Perform actions after a file has been highlighted in the
        DirectoryExplorer.
        """
        index = self._widgets['tree'].selectedIndexes()[0]
        _name = self._widgets['tree']._filemodel.filePath(index)
        if os.path.isfile(_name):
            _name = os.path.dirname(_name)
        self.q_settings.setValue('directory_explorer/path', _name)

    @QtCore.pyqtSlot()
    def __file_selected(self):
        """
        Open a file after sit has been selected in the DirectoryExplorer.
        """
        index = self._widgets['tree'].selectedIndexes()[0]
        _name = self._widgets['tree']._filemodel.filePath(index)
        self.set_status(f'Opened file: {_name}')
        if not os.path.isfile(_name):
            return
        _extension= '.' + os.path.basename(_name).split(".")[-1]
        _supported_nothdf_ext = (set(IMAGE_READER._extensions.keys())
                          - set(HDF5_EXTENSIONS))
        if _extension in HDF5_EXTENSIONS:
            self._widgets['hdf_dset'].setVisible(True)
            self._widgets['hdf_dset'].set_filename(_name)
            return
        self._widgets['hdf_dset'].setVisible(False)
        if _extension in _supported_nothdf_ext:
            _data = read_image(_name)
            self._widgets['viewer'].setData(_data)
