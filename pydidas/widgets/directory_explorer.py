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

"""Module with the DirectoryExplorer widget."""

__author__      = "Malte Storm"
__copyright__   = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "MIT"
__version__ = "0.0.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['DirectoryExplorer']

from PyQt5 import QtWidgets, QtCore

class DirectoryExplorer(QtWidgets.QTreeView):
    """
    The DirectoryExplorer is an implementation of a QTreeView widget with a
    file system model to display the contents of directories.
    """
    def __init__(self, parent=None, root_path=''):
        """
        Create a DirectoryExplorer instance.

        The setup method creates a new instance of the DirectoryExplorer.

        Parameters
        ----------
        parent : Union[QWidget, None], optional
            The parent widget, if appplicable. The default is None.
        root_path : str, optional
            The default path in the file system. The default is ''.

        Returns
        -------
        None.
        """
        super().__init__(parent)

        self._filemodel = QtWidgets.QFileSystemModel()
        self._filemodel.setRootPath(root_path)
        self._filemodel.setReadOnly(True)
        self.setModel(self._filemodel)
        self.header().setSortIndicator(0, QtCore.Qt.AscendingOrder)
        self.setAnimated(False)
        self.setIndentation(20)
        self.setSortingEnabled(True)
        self.setColumnWidth(0, 400)
        self.setColumnWidth(1, 70)
        self.setColumnWidth(2, 100)
        self.setColumnWidth(3, 140)
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding,
                           QtWidgets.QSizePolicy.Expanding)

    def sizeHint(self):
        """
        Overload the generic sizeHint.

        Returns
        -------
        QtCore.QSize
            The updated size hint.

        """
        return QtCore.QSize(400, 900)
