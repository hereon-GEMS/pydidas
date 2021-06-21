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

"""Module with Warning class for showing notifications."""

__author__      = "Malte Storm"
__copyright__   = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "MIT"
__version__ = "0.0.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['WarningBox']

from PyQt5 import QtWidgets

class WarningBox(QtWidgets.QMessageBox):
    """
    QMessageBox subclass which simplifies the calling syntax to generate
    user warning.
    """
    def __init__(self, title, msg, info=None, details=None):
        """
        Generate a warning box.

        The __init__ function will set title and message of the QMessageBox
        and call the ececute function to display it with a single line of
        code.

        Parameters
        ----------
        title : str
            The message box title.
        msg : str
            The message box text.
        info : str, optional
            Additional informative text. The default is None.
        details : str, optional
            Addition details for the warning. The default is None.

        Returns
        -------
        None.
        """
        super().__init__()
        self.setIcon(self.Warning)
        self.setWindowTitle(title)
        self.setText(msg)
        if info:
            self.setInformativeText(info)
        if details:
            self.setDetailedText(details)
        self.setStandardButtons(self.Ok)
        self.__exec__()

    def __exec__(self):
        """
        Show the QMessageBox

        Returns
        -------
        None.
        """
        self.exec_()
