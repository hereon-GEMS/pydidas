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

"""Module with the DataBrowsingFrame which is used to browse data."""

__author__      = "Malte Storm"
__copyright__   = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "MIT"
__version__ = "0.0.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['DataBrowsingFrame']

import os
from functools import partial

import numpy as np
import silx

from PyQt5 import QtWidgets, QtCore
from silx.gui.plot.ImageView import ImageView

from ..widgets import (DirectoryExplorer, Hdf5DatasetSelectorViewOnly,
                       QtaIconButton)
from .base_frame import BaseFrame
from ..image_reader import ImageReaderFactory, read_image
from ..config import HDF5_EXTENSIONS


IMAGE_READER = ImageReaderFactory()


class ImageViewNoHist(ImageView):
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

        self.initUI()
        self._tree.doubleClicked.connect(
            partial(self.__fileSelected, self._imview)
            )

    def initUI(self):

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

        # self._imview = PlotWindow()
        self._imview = ImageView()
        # self._imview._histoHPlot.setVisible(False)
        # self._imview._histoVPlot.setVisible(False)
        # self._imview._radarView.setVisible(False)

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

    def __fileSelected(self, widget):
        index = self._tree.selectedIndexes()[0]
        _name = self._tree._filemodel.filePath(index)
        self.set_status(f'New file: {_name}')
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
