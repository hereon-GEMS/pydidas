# This file is part of pydidas.
#
# Copyright 2023 - 2026, Helmholtz-Zentrum Hereon
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
Module with _SearchFilterModel and _PluginViewItemDelegate for browsing plugins.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2026, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["_PluginViewItemDelegate", "_SearchFilterModel"]


import math
from typing import Any

from qtpy import QtCore, QtGui, QtWidgets

from pydidas.core import constants


class _SearchFilterModel(QtCore.QSortFilterProxyModel):
    """
    A custom QSortFilterProxyModel to filter out entries not
    matching the search filter.
    """

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(kwargs.get("parent", None))
        self.setFilterCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self.setDynamicSortFilter(True)

    def _accept_index(self, index: QtCore.QModelIndex) -> bool:
        """
        Recursive implementation to display a row.

        This filter will match a row if
            - its item matches the filter
            - an item in one of its children matches the filter.

        Parameters
        ----------
        index : QModelIndex
            The index of the row.

        Returns
        -------
        bool
            Flag whether the filter accepts the index or not.
        """
        if index.isValid():
            _label = index.data(QtCore.Qt.DisplayRole)
            if self.filterRegularExpression().match(_label).hasMatch():
                return True
            for _row in range(index.model().rowCount(index)):
                if self._accept_index(index.model().index(_row, 0, index)):
                    return True
        return False

    def filterAcceptsRow(
        self, source_row: int, source_parent: QtCore.QModelIndex
    ) -> bool:
        """
        Reimplement the filterAcceptsRow method to use the filter.

        Parameters
        ----------
        source_row : int
            The source row number.
        source_parent : QModelIndex
            The row's parent.

        Returns
        -------
        bool
            Flag whether the filter accepts the row or not.
        """
        _index = self.sourceModel().index(source_row, 0, source_parent)
        return self._accept_index(_index)


class _PluginViewItemDelegate(QtWidgets.QStyledItemDelegate):
    """
    A QStyledItemDelegate to modify the font size for the different items.

    Parameters
    ----------
    parent : QTreeView
        The parent QTreeView widget.
    """

    def __init__(self, parent: QtWidgets.QTreeView) -> None:
        QtWidgets.QStyledItemDelegate.__init__(self, parent)
        self.__qtapp = QtWidgets.QApplication.instance()
        self.__height = math.ceil(2 * self.__qtapp.font_size + 2)
        self.__qtapp.sig_new_font_metrics.connect(self.process_new_font_metrics)

    @QtCore.Slot(float, float)
    def process_new_font_metrics(self, char_width: float, char_height: float) -> None:
        """
        Handle the QApplication's updated font.

        Parameters
        ----------
        char_width : float
            The font width in pixels.
        char_height : float
            The font height in pixels.
        """
        self.__height = int(char_height + 10)
        _parent = self.parent()
        self.sizeHintChanged.emit(_parent.currentIndex())  # type: ignore[union-attr]

    def sizeHint(
        self, options: QtWidgets.QStyleOptionViewItem, index: QtCore.QModelIndex
    ) -> QtCore.QSize:
        """
        Overload the size hint method to achieve a uniform row height.

        Parameters
        ----------
        options : QtWidgets.QStyleOptionViewItem
            The options.
        index : QtCore.QModelIndex
            The index.

        Returns
        -------
        size : QtCore.QSize
            The updated sizeHint from the QStyledItemDelegate.
        """
        size = QtWidgets.QStyledItemDelegate.sizeHint(self, options, index)
        size.setHeight(self.__height)
        return size

    def paint(
        self,
        painter: QtGui.QPainter,
        option: QtWidgets.QStyleOptionViewItem,
        index: QtCore.QModelIndex,
    ) -> None:
        """
        Overload the paint function with a custom font size for the top level items.

        Parameters
        ----------
        painter : QtGui.QPainter
            The QPainter called by the default method.
        option : QStyleOptionViewItem
            Any Qt options passed to the painter.
        index : QModelIndex
            The index of the item to be painted.
        """
        option.font.setFamily(self.__qtapp.font_family)
        if index.data(QtCore.Qt.DisplayRole) in constants.PLUGIN_TYPE_NAMES.values():
            option.font.setPointSizeF(self.__qtapp.font_size + 2)
        QtWidgets.QStyledItemDelegate.paint(self, painter, option, index)
