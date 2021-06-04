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

"""Module with the DataBrowsingFrame which is used to preview data."""

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

from ..widgets import (DirectoryExplorer, Hdf5DatasetSelector,
                       QtaIconButton)
from .toplevel_frame import ToplevelFrame

class DataBrowsingFrame(ToplevelFrame):
    """
    The DataBrowsingFrame is widget / frame with a directory exporer, a
    data preview window and a main data visualization window. Its main
    purpose is to browse through datasets.
    """
    def __init__(self, **kwargs):
        parent = kwargs.get('parent', None)
        name = kwargs.get('name', None)
        super().__init__(parent=parent, name=name)
        self.add_text_widget('Data exploration view', fontsize=14)

        self.initUI()
        self._tree.clicked.connect(partial(self.__fileSelected, self._preview))
        self._tree.doubleClicked.connect(partial(self.__fileSelected, self._imview))


    def initUI(self):
        from silx.gui.plot.ImageView import ImageView
        from silx.gui.dialog.ImageFileDialog import _ImagePreview

        self._tree = DirectoryExplorer()
        self.hdf_dset_w = Hdf5DatasetSelector()

        button_min = QtaIconButton('fa.chevron-left', size=25)
        button_max = QtaIconButton('fa.chevron-right', size=25)

        self._preview = _ImagePreview()
        self._preview.setFixedHeight(200)

        self._selection = QtWidgets.QFrame(self)
        self._selection.setSizePolicy(QtWidgets.QSizePolicy.Fixed,
                                      QtWidgets.QSizePolicy.Expanding)
        _layout = QtWidgets.QGridLayout()
        _layout.addWidget(self._tree, 0, 0, 3, 1)
        _layout.addWidget(button_min, 0, 1, 1, 1)
        _layout.addWidget(button_max, 2, 1, 1, 1)
        _layout.setRowStretch(0, 10)
        _layout.addWidget(self.hdf_dset_w, 3, 0, 1, 2)
        _layout.addWidget(self._preview, 4, 0, 1, 2)
        self._selection.setLayout(_layout)

        # self._imview = PlotWindow()
        self._imview = ImageView()
        self._imview.setAttribute(QtCore.Qt.WA_DeleteOnClose)

        self.hdf_dset_w.register_view_widget(self._imview)
        self.hdf_dset_w.register_preview_widget(self._preview)
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
        name = self._tree._filemodel.filePath(index)
        self.set_status(f'New file: {name}')
        if not os.path.isfile(name):
            return
        self._preview.setData(None)
        if os.path.basename(name).split('.')[-1] in ['hdf', 'nxs', 'h5']:
            self.hdf_dset_w.setVisible(True)
            self.hdf_dset_w.set_filename(name)
            return
        self.hdf_dset_w.setVisible(False)
        if os.path.basename(name).split('.')[-1] in ['tif', 'tiff']:
            import skimage.io
            _data = skimage.io.imread(name)
        elif os.path.basename(name).split('.')[-1] in ['npy', 'npz']:
            _data = np.load(name)
        elif os.path.basename(name).split('.')[-1] in ['edf']:
            try:
                with silx.io.open(name) as f:
                    _data = f['scan_0/image/data'][...]
            except OSError:
                return
        else:
            return
        widget.setData(_data)
        return
