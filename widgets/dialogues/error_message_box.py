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

"""Module with ErrorMessageBox class for exception output."""

__author__      = "Malte Storm"
__copyright__   = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "MIT"
__version__ = "0.0.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['ErrorMessageBox']

from PyQt5 import QtCore, QtWidgets

class ErrorMessageBox(QtWidgets.QDialog):
    """
    Show a dialogue box with exception information.

    Methods
    -------
    setText(str) :
        Set the message box text to the input string.
    """
    def __init__(self, *args, **kwargs):
        """
        Initialize the message box.

        Parameters
        ----------
        *args : TYPE
            Arguments passed to QtWidgets.QDialogue instantiation.
        **kwargs : TYPE
            Keyword arguments passed to QtWidgets.QDialogue instantiation.

        Returns
        -------
        None.
        """
        _text = None
        if 'text' in kwargs:
            _text = kwargs['text']
            del kwargs['text']
        super().__init__(*args, **kwargs)
        self.setWindowTitle("An exception has occured")

        self._label = QtWidgets.QLabel()
        self._label.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
        _scroll_area = QtWidgets.QScrollArea()

        _scroll_area.setWidget(self._label)
        _scroll_area.setWidgetResizable(True)
        _ok_button = QtWidgets.QPushButton('OK')

        _layout = QtWidgets.QVBoxLayout()
        _layout.addWidget(_scroll_area, 1, QtCore.Qt.AlignLeft)
        _layout.addWidget(_ok_button, 1, QtCore.Qt.AlignRight)

        self.setLayout(_layout)
        _ok_button.clicked.connect(self.close)
        if _text:
            self.set_text(_text)

    def __exec__(self):
        """
        Show the box.

        This method will show the ErrorMessageBox

        Returns
        -------
        None.
        """
        self.exec_()

    def set_text(self, text):
        """
        Set the text in the message box.

        Parameters
        ----------
        text : str
            The text to be displayed.

        Returns
        -------
        None.
        """
        self._label.setText(text)
