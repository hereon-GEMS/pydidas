# This file is part of pydidas.
#
# Copyright 2023 - 2025, Helmholtz-Zentrum Hereon
# SPDX-License-Identifier: GPL-3.0-only
#
# pydidas is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 3 as
# published by the Free Software Foundation.
#
# Pydidas is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Pydidas. If not, see <http://www.gnu.org/licenses/>.


"""
Module with the DirectoryExplorerTreeView widget, which is an implementation of a
QTreeView for a file system model.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["DirectoryExplorerTreeView"]


from qtpy import QtCore, QtWidgets

from pydidas.core.constants import POLICY_EXP_EXP
from pydidas.core.utils import apply_qt_properties


AscendingOrder = QtCore.Qt.AscendingOrder
QSortFilterProxyModel = QtCore.QSortFilterProxyModel


class DirectoryExplorerTreeView(QtWidgets.QTreeView):
    """
    The DirectoryExplorerTreeView is an implementation of a QTreeView widget with a
    file system model to display the contents of directories.

    Parameters
    ----------
    **kwargs : dict
        Supported keywords are any keywords that are supported by QTreeView.
    """

    init_kwargs = ["parent"]

    def __init__(self, **kwargs: dict):
        QtWidgets.QTreeView.__init__(self, kwargs.get("parent", None))
        apply_qt_properties(self, **kwargs)
        self.raw_model = None

    def setModel(self, model: QtCore.QAbstractItemModel):
        """
        Set the model of the directory explorer.

        Parameters
        ----------
        model : QtCore.QAbstractItemModel
            The model to be used.
        """
        if isinstance(model, QtCore.QSortFilterProxyModel):
            self.raw_model = model.sourceModel()
        else:
            self.raw_model = model
        QtWidgets.QTreeView.setModel(self, model)
        self.setAnimated(False)
        self.setIndentation(12)
        self.setSortingEnabled(True)
        self.setColumnWidth(0, 400)
        self.setColumnWidth(1, 70)
        self.setColumnWidth(2, 100)
        self.setColumnWidth(3, 140)
        self.setSizePolicy(*POLICY_EXP_EXP)
        self.sortByColumn(0, QtCore.Qt.SortOrder.AscendingOrder)

    def expand_to_path(self, path: str):
        """
        Expand the treeview to a given path.

        Parameters
        ----------
        path : str
            The full path to expand.
        """
        _index = self.raw_model.index(path)
        _indices = []
        while _index.isValid():
            _indices.insert(0, _index)
            _index = _index.parent()
        for _ix in _indices:
            self.setExpanded(self.model().mapFromSource(_ix), True)

    def sizeHint(self) -> QtCore.QSize:
        """
        Overload the generic sizeHint.

        Returns
        -------
        QtCore.QSize
            The updated size hint.
        """
        return QtCore.QSize(400, 4000)
