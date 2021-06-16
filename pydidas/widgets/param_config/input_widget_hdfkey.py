#!/usr/bin/env python

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

"""Module with the PluginParamConfig class used to edit plugin parameters."""

__author__      = "Malte Storm"
__copyright__   = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "MIT"
__version__ = "0.0.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['InputWidgetHdfKey']

from PyQt5 import QtWidgets, QtCore
from .input_widget_with_button import InputWidgetWithButton
from pydidas.widgets.dialogues import Hdf5DatasetSelectionPopup
from pydidas.config import HDF5_EXTENSIONS

class InputWidgetHdfKey(InputWidgetWithButton):
    """
    Widgets for I/O during plugin parameter for filepaths.
    (Includes a small button to select a filepath from a dialogue.)
     """
    #for some reason, inhering the signal from the base class does not work
    io_edited = QtCore.pyqtSignal(str)

    def __init__(self, parent, param, width=255):
        """
        Setup the widget.

        Init method to setup the widget and set the links to the parameter
        and Qt parent widget.

        Parameters
        ----------
        parent : QWidget
            A QWidget instance.
        param : Parameter
            A Parameter instance.
        width : int, optional
            The width of the IOwidget.

        Returns
        -------
        None.
        """
        super().__init__(parent, param, width)
        self._button.setToolTip(
            'Select a dataset from all dataset keys in a file.')

    def button_function(self):
        """
        Open a dialogue to select a file.

        This method is called upon clicking the "open file" button
        and opens a QFileDialog widget to select a filename.

        Returns
        -------
        None.
        """
        _fnames = ' *'.join(HDF5_EXTENSIONS)
        fname = QtWidgets.QFileDialog.getOpenFileName(
            self, 'Name of file', None,
            (f'HDF5 files (*{_fnames});; All files (*.*)')
        )[0]
        if fname:
            dset = Hdf5DatasetSelectionPopup(self, fname).get_dset()
            if dset is not None:
                self.setText(str(dset))
                self.emit_signal()
