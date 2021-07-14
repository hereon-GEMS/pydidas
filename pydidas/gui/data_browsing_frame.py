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

"""Module with the DataBrowsingFrame which is used to browse data."""

__author__      = "Malte Storm"
__copyright__   = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.0.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['DataBrowsingFrame']

import os
from functools import partial

from PyQt5 import QtWidgets, QtCore
from silx.gui.plot.ImageView import ImageView

from ..widgets import (DirectoryExplorer, Hdf5DatasetSelectorViewOnly,
                       QtaIconButton, BaseFrame)
from ..image_reader import ImageReaderFactory, read_image
from ..config import HDF5_EXTENSIONS


IMAGE_READER = ImageReaderFactory()


class ImageViewNoHist(ImageView):
    """
    Subclass silx ImageView with a smaller historgram.
    """
    HISTOGRAMS_HEIGHT = 120

    def __init__(self):
        super().__init__()


class DataBrowsingFrame(BaseFrame):
    """
    The DataBrowsingFrame is widget / frame with a directory exporer
    and a main data visualization window. Its main purpose is to browse
    through datasets.
    """
    def __init__(self, **kwargs):
        parent = kwargs.get('parent', None)
        name = kwargs.get('name', None)
        super().__init__(parent=parent, name=name)
        self.create_label('Data exploration view', fontsize=14)
        self.__settings = QtCore.QSettings('Hereon', 'pydidas')

        self.init_widgets()
        self._tree.doubleClicked.connect(
            partial(self.__fileSelected, self._imview)
            )
        self._tree.clicked.connect(self.__fileHighlighted)

    def init_widgets(self):
        """Init the user interface with the widgets."""
        self._tree = DirectoryExplorer()
        self.hdf_dset_w = Hdf5DatasetSelectorViewOnly()

        button_min = QtaIconButton('fa.chevron-left', size=25)
        button_max = QtaIconButton('fa.chevron-right', size=25)

        self._selection = QtWidgets.QFrame(self)
        self._selection.setSizePolicy(QtWidgets.QSizePolicy.Fixed,
                                      QtWidgets.QSizePolicy.Expanding)
        _layout = QtWidgets.QGridLayout()
        _layout.addWidget(self._tree, 0, 0, 3, 1)
        _layout.addWidget(button_min, 0, 1, 1, 1)
        _layout.addWidget(button_max, 2, 1, 1, 1)
        _layout.setRowStretch(0, 10)
        _layout.addWidget(self.hdf_dset_w, 3, 0, 1, 2)
        self._selection.setLayout(_layout)

        self._imview = ImageView()
        self._imview.setAttribute(QtCore.Qt.WA_DeleteOnClose)

        self.hdf_dset_w.register_view_widget(self._imview)
        self.main_splitter = QtWidgets.QSplitter()
        self.main_splitter.setSizePolicy(QtWidgets.QSizePolicy.Expanding,
                                         QtWidgets.QSizePolicy.Expanding)
        self.main_splitter.addWidget(self._selection)
        self.main_splitter.addWidget(self._imview)

        self.layout().addWidget(self.main_splitter)

        button_min.clicked.connect(partial(self.change_min_widths, False))
        button_max.clicked.connect(partial(self.change_min_widths, True))

        self.__selectionWidth = self._selection.width()
        self._imview.setData = self._imview.setImage

    def change_min_widths(self, enlargeDir=True):
        if enlargeDir:
            self.main_splitter.moveSplitter(770, 1)
        else:
            self.main_splitter.moveSplitter(300, 1)

    def __fileHighlighted(self):
        index = self._tree.selectedIndexes()[0]
        _name = self._tree._filemodel.filePath(index)
        if os.path.isfile(_name):
            _name = os.path.dirname(_name)
        self.__settings.setValue('directory_explorer/path', _name)

    def __fileSelected(self, widget):
        index = self._tree.selectedIndexes()[0]
        _name = self._tree._filemodel.filePath(index)
        self.set_status(f'Opened file: {_name}')
        if not os.path.isfile(_name):
            return
        _extension= f'.{os.path.basename(_name).split(".")[-1]}'
        _supported_ext = (set(IMAGE_READER._extensions.keys())
                          - set(HDF5_EXTENSIONS))
        if _extension in HDF5_EXTENSIONS:
            self.hdf_dset_w.setVisible(True)
            self.hdf_dset_w.set_filename(_name)
            return
        self.hdf_dset_w.setVisible(False)
        if _extension in _supported_ext:
            _data = read_image(_name)
            widget.setData(_data)
        return
