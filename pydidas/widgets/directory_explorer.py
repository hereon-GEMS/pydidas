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

"""Module with the DirectoryExplorer widget."""

__author__      = "Malte Storm"
__copyright__   = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
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

        if root_path == '':
            _settings = QtCore.QSettings('Hereon', 'pydidas')
            _path = _settings.value('directory_explorer/path', None)
            if _path is not None:
                root_path = _path
        self._filemodel = QtWidgets.QFileSystemModel()
        self._filemodel.setRootPath(root_path)
        self._filemodel.setRootPath('')
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

        self.__expand_to_path(root_path)

    def __expand_to_path(self, path):
        """
        Expand the treeview to a given path.
        """
        _index = self._filemodel.index(path)
        indexes = []
        ix = _index
        while ix.isValid():
            indexes.insert(0, ix)
            ix = ix.parent()
        for ix in indexes:
            self.setExpanded(ix, True)

    def sizeHint(self):
        """
        Overload the generic sizeHint.

        Returns
        -------
        QtCore.QSize
            The updated size hint.

        """
        return QtCore.QSize(400, 900)
